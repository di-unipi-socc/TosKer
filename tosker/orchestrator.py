"""
Orchestrator module
"""
import logging
import os
import re
import shutil
import traceback
from functools import wraps
from glob import glob
from io import open

import six
from halo import Halo
from tabulate import tabulate
from toscaparser.common.exception import ValidationError
from yaml.scanner import ScannerError

from termcolor import colored

from . import docker_interface, helper, protocol_helper
from .graph.nodes import Container, Software, Volume
from .graph.protocol import (CONTAINER_STATE_CREATED, CONTAINER_STATE_DELETED,
                             CONTAINER_STATE_RUNNING, SOFTWARE_STATE_ZOTTED,
                             STATE_RUNNING, VOLUME_STATE_CREATED,
                             VOLUME_STATE_DELETED)
from .helper import Logger
from .managers.container_manager import ContainerManager
from .managers.software_manager import SoftwareManager
from .managers.volume_manager import VolumeManager
from .storage import Memory
from .tosca_parser import get_tosca_template

try:
    from os import scandir
except ImportError:
    from scandir import scandir


class Orchestrator:

    def update_memory(f):
        """decorator that update memory before execute function"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            status, faulty = args[0]._update_state()
            Logger.println('(update memory: {})'.format(
                           'ok' if status else 'fixed {}'.format(', '.join(faulty))))
            return f(*args, **kwargs)
        return decorated_function

    def __init__(self,
                 log_handler=logging.NullHandler(),
                 quiet=True,
                 tmp_dir='/tmp/tosker',
                 data_dir='/tmp/tosker'):  # TODO: use /usr/lib/tokser instead
        Logger.set(log_handler, quiet)
        self._log = Logger.get(__name__)
        self._tmp_dir = tmp_dir

        # Setup Storage system (folder and class)
        self._data_dir = data_dir
        try:
            os.makedirs(data_dir)
        except os.error:
            pass
        Memory.set_db(data_dir)

    @update_memory
    def orchestrate(self, file_path, operations, inputs=None):
        """
        Start the orchestration using the management protocols.
        Operations mus be a list where every element are in the
        format "component:interface.operation"
        """
        # Parse TOSCA file
        tpl = self._parse_tosca(file_path, inputs)
        if tpl is None:
            return False

        # Parse operations
        operations = self._parse_operations(tpl, operations)
        if operations is None:
            return False

        # Create tmp directory for the template
        self._create_tmp_dir(tpl)

        # Load components state
        if not self._load_component_state(tpl):
            Logger.print_error('Cannot load components state,'
                               'try to use "tosker prune" to hard reset.')
            return False
        self._log.debug('State: %s', ' '.join(
            (c['name'] + '.' + c['state'] for c in Memory.get_comps(tpl.name))))

        try:
            # Check plan
            self._print_loading_start('Check deployment plan... ')
            for component, full_operation in operations:
                try:
                    protocol_helper.can_execute(full_operation, component)
                    component.protocol.execute_operation(full_operation)
                except ValueError as e:
                    self._print_cross('Error on {}.{}: {}'
                                      ''.format(component.name, full_operation, e))
                    return False
            self._load_component_state(tpl)
            self._print_tick()

            # Create Network
            # TODO: do not create network if already there
            self._print_loading_start('Create network... ')
            docker_interface.create_network(tpl.name)
            self._print_tick()

            # Execute plan
            for component, full_operation in operations:
                protocol = component.protocol
                self._log.debug('Component %s is in state %s',
                                component.name, component.protocol.current_state)
                self._print_loading_start('Execute op "{}" on "{}"... '
                                          ''.format(full_operation, component.name))

                transition = protocol.next_transition(full_operation)
                self._log.debug('transition: i={} o={}'.format(
                    transition.interface, transition.operation))

                if isinstance(component, Container):
                    ContainerManager.exec_operation(
                        component, transition.operation)
                elif isinstance(component, Volume):
                    VolumeManager.exec_operation(
                        component, transition.operation)
                elif isinstance(component, Software):
                    SoftwareManager.exec_operation(component, transition.interface,
                                                   transition.operation)

                state = protocol.execute_operation(full_operation)

                # remove the component if it is in the initial state
                if state == protocol.initial_state:
                    Memory.remove(component)
                else:
                    Memory.update_state(component, state.name)
                self._print_tick()

            self._print_outputs(tpl)
        except Exception as e:
            self._log.debug('Exception type: %s', type(e))
            self._log.debug(traceback.format_exc())
            self._print_cross(e)
            return False

        return True

    def read_plan(self, file):
        with open(file, 'r') as plan:
            plan_list = [l for l in (l.strip() for l in plan.readlines())
                         if l and not l.startswith('#')]
            return plan_list

    @update_memory
    def ls_components(self, app=None, filters={}):
        comps = Memory.get_comps(app, filters)

        def get_state(state):
            return colored(state, ('green' if state == STATE_RUNNING else None))

        def format_row(comp):
            return [comp['app_name'],
                    comp['name'],
                    comp['type'],
                    get_state(comp['state']),
                    '{}.{}'.format(comp['app_name'], comp['name'])]

        table = [format_row(c) for c in comps]
        table_str = tabulate(table, headers=['Application', 'Component',
                                             'Type', 'State', 'Full name'])
        Logger.println(table_str)

    def log(self, component, operation):
        # TODO: add logs also for Docker container

        app, name = helper.split(component, '.')
        if app is None:
            Logger.print_error('First argument must be a component full name '
                               '(i.e my_app.my_component)')
            return

        if '.' not in operation:
            operation = 'Standard.{}'.format(operation)

        self._log.debug('app: %s, name: %s, operation: %s',
                        app, name, operation)

        log_file_name = '{}/{}/*/{}/{}.log'.format(self._tmp_dir,
                                                   app, name, operation)

        log_file = glob(log_file_name)

        if len(log_file) != 1:
            Logger.print_error('Component or operation log not found')
            return

        with open(log_file[0], 'r', encoding='utf-8', errors='ignore') as f:
            for line in f.readlines():
                line = colored(line, 'green') if line.startswith(
                    '+ ') else line
                Logger.print_(line)

    def prune(self):
        self._print_loading_start('Remove containers.. ')
        con = docker_interface.get_containers(all=True)
        for c in (c for c in con if c['Names'][0].startswith('/tosker')):
            self._log.debug(c['Names'][0])
            docker_interface.delete_container(c['Id'], force=True)
        self._print_tick()

        self._print_loading_start('Remove volumes.. ')
        vol = docker_interface.get_volumes()
        for v in (v for v in vol if v['Name'].startswith('tosker')):
            self._log.debug(v['Name'])
            docker_interface.delete_volume(v['Name'])
        self._print_tick()

        # TODO: remove also networks

        self._print_loading_start('Remove tosker data.. ')
        shutil.rmtree(self._tmp_dir)
        self._print_tick()

    def _parse_tosca(self, file_path, inputs):
        '''
        Parse TOSCA file
        '''
        try:
            return get_tosca_template(file_path, inputs)
        except ScannerError as e:
            Logger.print_error('YAML parse error\n    {}'.format(e))
            return None
        except ValidationError as e:
            Logger.print_error('TOSCA validation error\n    {}'.format(e))
            return None
        except ValueError as e:
            Logger.print_error('TosKer validation error\n    {}'.format(e))
            self._log.debug(colored(traceback.format_exc(), 'red'))
            return None
        except Exception as e:
            Logger.print_error('Internal error\n    {}'.format(e))
            self._log.debug('Exception type: %s', type(e))
            self._log.debug(colored(traceback.format_exc(), 'red'))
            return None

    def _create_tmp_dir(self, tpl):
        '''
        Create temporany directory
        '''
        tpl.tmp_dir = os.path.join(self._tmp_dir, tpl.name)
        try:
            os.makedirs(tpl.tmp_dir)
        except os.error as e:
            self._log.info(e)

    def _parse_operations(self, tpl, operations):
        res = []
        for op in operations:
                # Check that the component existes in the template
            comp_name, full_operation = helper.split(op, ':')
            comp = tpl[comp_name]
            if comp is None:
                Logger.print_error(
                    'Component "{}" not found in template.'.format(comp_name))
                return None

            # check that the component has interface.operation
            interface, operation = helper.split(full_operation, '.')
            if interface not in comp.interfaces and\
               operation not in comp.interfaces[interface]:
                Logger.print_error('Component "{}" not has the "{}"'
                                   'operation in the "{}" interface.'
                                   ''.format(comp_name, operation, interface))
                return None
            res.append((comp, full_operation))

        return res

    def _load_component_state(self, tpl):
        for comp in tpl.nodes:
            state = Memory.get_comp_state(comp)
            if state is not None:
                state = comp.protocol.find_state(state)
                if state is not None:
                    comp.protocol.current_state = state
                else:
                    return False
            else:
                comp.protocol.reset()
        return True

    def _print_outputs(self, tpl):
        if len(tpl.outputs) != 0:
            Logger.println('\nOUTPUTS:')
        for out in tpl.outputs:
            self._log.debug('value: %s', out.value)
            value = out.value if isinstance(out.value, six.string_types) \
                else helper.get_attributes(out.value.args, tpl)
            Logger.println('  - ' + out.name + ":", value)

    def _update_state(self):
        errors = set()

        def manage_error(comp, state):
            errors.add(comp['full_name'])
            Memory.update_state(comp, state)

        def manage_error_container(comp, state):
            manage_error(comp, state)
            path = os.path.join(self._tmp_dir, comp['app_name'], comp['name'])

            try:
                software = [(f.name, f.path) for f in scandir(path)
                            if f.is_dir()]
            except FileNotFoundError as e:
                software = []
            self._log.debug('path %s found %s', path, software)

            for s, s_path in software:
                full_name = '{}.{}'.format(comp['app_name'], s)
                Memory.update_state('{}.{}'.format(
                    comp['app_name'], s), SOFTWARE_STATE_ZOTTED)
                errors.add(full_name)

        for container in Memory.get_comps(filters={'type': 'Container'}):
            status = docker_interface.inspect_container(container['full_name'])
            deleted, created, running = status is None,\
                status is not None and not status['State']['Running'],\
                status is not None and status['State']['Running']
            if deleted and container['state'] != CONTAINER_STATE_DELETED:
                manage_error_container(container, CONTAINER_STATE_DELETED)
            elif created and container['state'] != CONTAINER_STATE_CREATED:
                manage_error_container(container, CONTAINER_STATE_CREATED)
            elif running and container['state'] != CONTAINER_STATE_RUNNING:
                manage_error_container(container, CONTAINER_STATE_RUNNING)

        for volume in Memory.get_comps(filters={'type': 'Volume'}):
            status = docker_interface.inspect_volume(volume['full_name'])
            if status is None:
                manage_error(volume, VOLUME_STATE_DELETED)

        return len(errors) == 0, errors

    def _print_tick(self):
        self._loading_thread.succeed(self._loading_thread.text + 'Done')

    def _print_skip(self):
        self._loading_thread.info(self._loading_thread.text + 'Skipped')

    def _print_cross(self, error):
        self._loading_thread.fail(self._loading_thread.text + '\n' +
                                  colored(error, 'red'))

    def _print_loading_start(self, msg):
        self._loading_thread = Halo(text=msg, spinner='dots')
        self._loading_thread.start()
