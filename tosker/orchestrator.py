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

from . import docker_interface, helper
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


def _filter_components(*comps):
    def _filter_components_decorator(func):
        @wraps(func)
        def func_wrapper(self, *args):
            filter_componets = [c for c in args[0]
                                if isinstance(c, comps)]
            return func(self, filter_componets, *args[1:])
        return func_wrapper
    return _filter_components_decorator

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

        status, faulty = self._update_state()
        Logger.println('update memory {} {}'.format(
            'ok' if status else 'fixed',
            '({})'.format(', '.join(faulty)) if not status else ''))

    def orchestrate(self, file_path, commands, components=[], inputs={}):
        # Parse TOSCA file
        try:
            tpl = get_tosca_template(file_path, inputs)
        except ScannerError as e:
            Logger.print_error('YAML parse error\n    {}'.format(e))
            return False
        except ValidationError as e:
            Logger.print_error('TOSCA validation error\n    {}'.format(e))
            return False
        except ValueError as e:
            Logger.print_error('TosKer validation error\n    {}'.format(e))
            return False
        except Exception as e:
            Logger.print_error('Internal error\n    {}'.format(e))
            self._log.debug('Exception type: %s', type(e))
            self._log.debug(colored(traceback.format_exc(), 'red'))
            return False

        # Check if inputs components exists in the TOSCA file
        if not self._components_exists(tpl, components):
            Logger.print_error('a selected component do not exists')
            return False

        # Create temporany directory
        tpl.tmp_dir = os.path.join(self._tmp_dir, tpl.name)
        try:
            os.makedirs(tpl.tmp_dir)
        except os.error as e:
            self._log.info(e)

        # Start orchestration
        try:
            if len(components) == 0:
                components = [n.name for n in tpl.nodes]

            # must calculate the down extension/sorting
            if any((c in ('create', 'start') for c in commands)):
                down_extension = self._extend_down(tpl, components)
                down_deploy = self._sort(tpl, down_extension)
                self._log.debug('down_deploy: %s', ', '.join(
                                (c.name for c in down_deploy)))
            # must calculate the up extension/sorting
            if any((c in ('stop', 'delete') for c in commands)):
                up_extension = self._extend_up(tpl, components)
                up_deploy = list(reversed(self._sort(tpl, up_extension)))
                self._log.debug('up_deploy: %s', ', '.join(
                                (c.name for c in up_deploy)))

            for cmd in commands:
                {
                  'create': lambda: self._create(down_deploy, tpl),
                  'start': lambda: self._start(down_deploy, tpl),
                  'stop': lambda: self._stop(up_deploy, tpl),
                  'delete': lambda: self._delete(up_deploy, tpl),
                }.get(cmd)()

            self._print_outputs(tpl)
        except Exception as e:
            self._log.debug('Exception type: %s', type(e))
            self._log.debug(traceback.format_exc())
            self._print_cross(e)
            return False
        return True

    def _create(self, components, tpl):
        self._print_loading_start('Create network... ')
        docker_interface.create_network(tpl.name)  # TODO: da rimuovere
        self._print_tick()
        for node in components:
            self._print_loading_start('Create {}... '.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.DELETED == status:
                if isinstance(node, Container):
                    ContainerManager.create(node)
                elif isinstance(node, Volume):
                    VolumeManager.create(node)
                elif isinstance(node, Software):
                    SoftwareManager.create(node)
                    SoftwareManager.configure(node)

                Memory.update_state(node, Memory.STATE.CREATED)

                self._print_tick()
            else:
                self._print_skip()
                self._log.info('skipped already created')
    
    @_filter_components(Software, Container)
    def _start(self, components, tpl):
        for node in components:
            self._print_loading_start('Start {}... '.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.STARTED == status:
                self._print_skip()
                self._log.info('skipped already started')
            elif Memory.STATE.CREATED == status or\
                    'create' not in node.interfaces:
                if isinstance(node, Container):
                    ContainerManager.start(node)
                elif isinstance(node, Software):
                    SoftwareManager.start(node)
                Memory.update_state(node, Memory.STATE.STARTED)
                self._print_tick()
            else:
                self._print_cross('the components must be created first')
                self._log.info('%s have to be created first', node)
                break
    
    @_filter_components(Software, Container)
    def _stop(self, components, tpl):
        for node in components:
            self._print_loading_start('Stop {}... '.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.STARTED == status:
                if isinstance(node, Container):
                    ContainerManager.stop(node)
                elif isinstance(node, Software):
                    SoftwareManager.stop(node)
                Memory.update_state(node, Memory.STATE.CREATED)
                self._print_tick()
            else:
                self._print_skip()
                self._log.info('skipped already stopped')

    @_filter_components(Software, Container)
    def _delete(self, components, tpl):
        self._log.debug('start delete')
        for node in components:
            self._print_loading_start('Delete {}... '.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.CREATED == status:
                if isinstance(node, Container):
                    ContainerManager.delete(node)
                elif isinstance(node, Software):
                    SoftwareManager.delete(node)
                Memory.update_state(node, Memory.STATE.DELETED)
                self._print_tick()
            elif Memory.STATE.STARTED == status:
                self._print_cross('The component must be stopped first')
                self._log.info('%s have to be stopped first', node)
                break
            else:
                self._print_skip()
                self._log.info('skipped already deleted')
        else:
            self._print_loading_start('Delete network... ')
            docker_interface.delete_network(tpl.name)
            self._print_tick()
            shutil.rmtree(tpl.tmp_dir)

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

    def log(self, component, interface):
        # TODO: add logs also for Docker container
        try:
            split_list = component.split('.')
            app = '.'.join(split_list[:-1])
            name = split_list[-1]
        except ValueError:
            Logger.print_error('First argument must be a component full name (i.e my_app.my_component)')
            return
        
        self._log.debug('app: %s, name: %s, interface: %s', app, name, interface)

        log_file_name = '{}/{}/*/{}/{}.log'.format(self._tmp_dir,
                                               app, name, interface)

        log_file = glob(log_file_name)

        if len(log_file) != 1:
            Logger.print_error('Component or interface log not found')
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

        self._print_loading_start('Remove images.. ')
        images = docker_interface.get_images()
        for i in (i for i in images if i['RepoTags'][0].startswith('tosker')):
            self._log.debug(i['RepoTags'][0])
            docker_interface.delete_image(i['Id'])
        self._print_tick()
        
        # TODO: remove also networks

        self._print_loading_start('Remove tosker data.. ')
        shutil.rmtree(self._tmp_dir)
        self._print_tick()

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

    def _components_exists(self, tpl, components):
        for c in components:
            if not any(c == n.name for n in tpl.nodes):
                return False
        return True

    def _extend_down(self, tpl, components):
        assert isinstance(components, list)

        def get_down_req(c):
            for r in c.relationships:
                if r.to.name not in components:
                    yield r.to
                for c in get_down_req(r.to):
                    yield c

        return self._extend(tpl, components, get_down_req)

    def _extend_up(self, tpl, components):
        assert isinstance(components, list)

        def get_up_req(c):
            for r in c.up_requirements:
                if r.origin.name not in components:
                    yield r.origin
                # python3 alternative
                # yield from get_up_req(r.origin)
                for c in get_up_req(r.origin):
                    yield c

        return self._extend(tpl, components, get_up_req)

    def _extend(self, tpl, components, extension_gen):
        assert isinstance(components, list)

        extend_comp = []

        for c in components:
            extend_comp.append(tpl[c])
            for rc in extension_gen(tpl[c]):
                extend_comp.append(rc)

        return extend_comp

    def _sort(self, tpl, components):
        assert isinstance(components, list)

        for n in tpl.nodes:
            n._mark = ''
        unmarked = set((c.name for c in components))
        deploy_order = []

        def visit(n):
            if n._mark == 'temp':
                self._log.debug('no dag')
                raise ValueError('the TOSCA file is not a DAG')
            elif n._mark == '':
                n._mark = 'temp'
                if n.name in unmarked:
                    unmarked.remove(n.name)
                for r in n.relationships:
                    if any(r.to == c for c in components):
                        visit(r.to)
                n._mark = 'perm'
                deploy_order.append(n)

        while len(unmarked) > 0:
            n = unmarked.pop()
            visit(tpl[n])

        return deploy_order

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
