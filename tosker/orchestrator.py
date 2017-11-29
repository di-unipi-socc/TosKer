'''
Orchestrator module
'''
import logging
import os
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

    def __init__(self,
                 log_handler=logging.NullHandler(),
                 quiet=True,
                 tmp_dir='/tmp/tosker',
                 data_dir='/tmp/tosker'):  # TODO: use /usr/lib/tokser instead
        Logger.set(log_handler, quiet)
        self._log = Logger.get(__name__)
        self._tmp_dir = tmp_dir

        # Setup Storage system (folder and class
        self._data_dir = data_dir
        try:
            os.makedirs(data_dir)
        except os.error:
            pass
        Memory.set_db(data_dir)

        # FIXME: add this again!
        # status, faulty = self._update_state()
        # Logger.println('update memory {} {}'.format(
        #     'ok' if status else 'fixed',
        #     '({})'.format(', '.join(faulty)) if not status else ''))

    def orchestrate(self, file_path, operations, inputs):
        '''
        Start the orchestration using the management protocols
            operations:['component:interface.operation'...]
        '''
        # Parse TOSCA file
        tpl = self._parse_tosca(file_path, inputs)
        if tpl is None:
            return False

        # Create tmp directory for the template
        self._create_tmp_dir(tpl)

        # Load components state
        for comp in Memory.get_comps(tpl.name):
            tpl[comp['name']].protocol.current_state = comp['state']
        self._log.debug('State: %s', ' '.join(
            (c['name']+'.'+c['state'] for c in Memory.get_comps(tpl.name))
        ))

        # Create Network
        # TODO: do not create network if already there
        self._print_loading_start('Create network... ')
        docker_interface.create_network(tpl.name)
        self._print_tick()

        # TODO: validate operatin format.

        try:
            for op in operations:
                op_list = op.split(':')
                comp_name, operation = ':'.join(op_list[:-1]), op_list[-1]
                
                component = tpl[comp_name]
                if component is None:
                    self._print_cross('Cannot find component {}'.format(comp_name))
                    return False
                protocol = component.protocol
                self._print_loading_start('Execute op "{}" on "{}"... '
                    ''.format(operation, comp_name))

                if not protocol_helper.can_execute(operation, component):
                    # TODO: write the motivation because is not possible
                    self._print_cross('Cannot execute the operation')
                    return False

                transition = protocol.next_transition(operation)
                self._log.debug('transition: i={} o={}'.format(transition.interface, transition.operation))
                
                if isinstance(component, Container):
                    ContainerManager.exec_operation(component, transition.operation)
                elif isinstance(component, Volume):
                    VolumeManager.exec_operation(component, transition.operation)
                elif isinstance(component, Software):
                    SoftwareManager.exec_operation(component, transition.interface,
                                                   transition.operation)

                state = protocol.execute_operation(operation)

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

    def ls_components(self, app=None, filters={}):
        comps = Memory.get_comps(app, filters)

        def get_state(state):
            return colored(state, {
                Memory.STATE.CREATED.value: None,
                Memory.STATE.STARTED.value: 'green'}.get(state))

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
        try:
            split_list = component.split('.')
            app = '.'.join(split_list[:-1])
            name = split_list[-1]
        except ValueError:
            Logger.print_error('First argument must be a component full name (i.e my_app.my_component)')
            return
        
        if '.' not in operation:
            operation = 'Standard.{}'.format(operation)

        self._log.debug('app: %s, name: %s, operation: %s', app, name, operation)

        log_file_name = '{}/{}/*/{}/{}.log'.format(self._tmp_dir,
                                               app, name, operation)

        log_file = glob(log_file_name)

        if len(log_file) != 1:
            Logger.print_error('Component or operation log not found')
            return

        with open(log_file[0], 'r', encoding='utf-8', errors='ignore') as f:
            for line in f.readlines():
                line = colored(line, 'green') if line.startswith('+ ') else line
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

        # self._print_loading_start('Remove images.. ')
        # images = docker_interface.get_images()
        # for i in (i for i in images if i['RepoTags'][0].startswith('tosker')):
        #     self._log.debug(i['RepoTags'][0])
        #     docker_interface.delete_image(i['Id'])
        # self._print_tick()
        
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

    def _print_outputs(self, tpl):
        if len(tpl.outputs) != 0:
            Logger.println('\nOUTPUTS:')
        for out in tpl.outputs:
            self._log.debug('value: %s', out.value)
            value = out.value if isinstance(out.value, six.string_types) \
                else helper.get_attributes(out.value.args, tpl)
            Logger.println('  - ' + out.name + ":", value)

    def _update_state(self):
        # FIXME: this method update the memory not in the correct way 
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
                Memory.update_state('{}.{}'.format(comp['app_name'], s), state)
                # with open(os.path.join(s_path, 'state'), 'w') as f:
                #     f.write(state.value)
                try:
                    os.remove(os.path.join(s_path, 'state'))
                except FileNotFoundError:
                    pass
                errors.add(full_name)

        for c in Memory.get_comps(filters={'type': 'Software'}):
            state = glob('{}/{}/*/{}/state'.format(self._tmp_dir,
                                                   c['app_name'],
                                                   c['name']))
            self._log.debug('software update %s', state)

            if len(state) == 1:
                with open(state[0], 'r') as f:
                    state = f.read().replace('\n', '')
                if state != c['state']:
                    manage_error(c, Memory.STATE(state))

        for c in Memory.get_comps(filters={'type': 'Container'}):
                status = docker_interface.inspect_container(c['full_name'])
                if status is not None:
                    self._log.debug('%s status %s', c['full_name'], status['State'])
                    if c['state'] == Memory.STATE.CREATED.value and \
                       status['State']['Running'] is not False:
                        manage_error_container(c, Memory.STATE.STARTED)
                    if c['state'] == Memory.STATE.STARTED.value and\
                       status['State']['Running'] is not True:
                        manage_error_container(c, Memory.STATE.CREATED)
                else:
                    manage_error_container(c, Memory.STATE.DELETED)

        for c in Memory.get_comps(filters={'type': 'Volume'}):
                status = docker_interface.inspect_volume(c['full_name'])
                if status is None:
                    manage_error(c, Memory.STATE.DELETED)

        return len(errors) == 0, errors

    def _print_tick(self):
        self._loading_thread.succeed(self._loading_thread.text + 'Done')

    def _print_skip(self):
        self._loading_thread.info(self._loading_thread.text + 'Skipped')

    def _print_cross(self, error):
        self._loading_thread.fail(self._loading_thread.text +
                                  'Error ({})'.format(error))

    def _print_loading_start(self, msg):
        self._loading_thread = Halo(text=msg, spinner='dots')
        self._loading_thread.start()
