import logging
import os
import shutil
import threading
import time
import traceback
# from termcolor import colored
from functools import wraps
from glob import glob

import six
from tabulate import tabulate

from . import docker_interface, helper
from .graph.nodes import Container, Software, Volume
from .helper import Logger
from .managers.container_manager import Container_manager
from .managers.software_manager import Software_manager
from .managers.volume_manager import Volume_manager
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


def _filter_interface(interface):
    def _filter_interface_decorator(func):
        @wraps(func)
        def func_wrapper(self, *args):
            filter_componets = [c for c in args[0]
                                if interface in c.interfaces]
            return func(self, filter_componets, *args[1:])
        return func_wrapper
    return _filter_interface_decorator


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
        except os.error as e:
            self._log.info(e)
        Memory.set_db(data_dir)

        status, faulty = self._update_state()
        Logger.println('update memory {} {}'.format(
            'ok' if status else 'fixed',
            '({})'.format(', '.join(faulty)) if not status else ''))

    def orchestrate(self, file_path, commands, components=[], inputs={}):
        # Parse TOSCA file
        try:
            tpl = get_tosca_template(file_path, inputs)
        except Exception as e:
            Logger.println(e.args[0])
            self._log.debug(traceback.format_exc())
            return False

        # Check if inputs components exists in the TOSCA file
        if not self._components_exists(tpl, components):
            Logger.println('ERROR: a selected component do not exists')
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
                self._log.debug('down_deploy: {}'.format(', '
                                ''.join((c.name for c in down_deploy))))
            # must calculate the up extension/sorting
            if any((c in ('stop', 'delete') for c in commands)):
                up_extension = self._extend_up(tpl, components)
                up_deploy = list(reversed(self._sort(tpl, up_extension)))
                self._log.debug('up_deploy: {}'.format(', '
                                ''.join((c.name for c in up_deploy))))

            for cmd in commands:
                {
                  'create': lambda: self._create(down_deploy, tpl),
                  'start': lambda: self._start(down_deploy, tpl),
                  'stop': lambda: self._stop(up_deploy, tpl),
                  'delete': lambda: self._delete(up_deploy, tpl),
                }.get(cmd)()

            self._print_outputs(tpl)
        except Exception as e:
            self._print_cross(e)
            # Logger.println(e)
            self._log.debug(traceback.format_exc())
            return False
        return True

    # @_filter_interface('create')
    def _create(self, components, tpl):
        self._print_loading_start('Create network... ')
        docker_interface.create_network(tpl.name)  # TODO: da rimuovere
        self._print_tick()
        for node in components:
            self._print_loading_start('Create {}... '.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.DELETED == status:
                if isinstance(node, Container):
                    Container_manager.create(node)
                elif isinstance(node, Volume):
                    Volume_manager.create(node)
                elif isinstance(node, Software):
                    Software_manager.create(node)
                    Software_manager.configure(node)

                Memory.update_state(node, Memory.STATE.CREATED)

                self._print_tick()
            else:
                self._print_skip()
                self._log.info('skipped already created')

    @_filter_interface('start')
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
                    Container_manager.start(node)
                elif isinstance(node, Software):
                    Software_manager.start(node)
                Memory.update_state(node, Memory.STATE.STARTED)
                self._print_tick()
            else:
                self._print_cross('the components must be created first')
                self._log.info('{} have to be created first'.format(node))
                break

    @_filter_interface('stop')
    def _stop(self, components, tpl):
        for node in components:
            self._print_loading_start('Stop {}... '.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.STARTED == status:
                if isinstance(node, Container):
                    Container_manager.stop(node)
                elif isinstance(node, Software):
                    Software_manager.stop(node)
                Memory.update_state(node, Memory.STATE.CREATED)
                self._print_tick()
            else:
                self._print_skip()
                self._log.info('skipped already stopped')

    @_filter_interface('start')
    def _delete(self, components, tpl):
        self._log.debug('start delete')
        for node in components:
            self._print_loading_start('Delete {}... '.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.CREATED == status:
                if isinstance(node, Container):
                    Container_manager.delete(node)
                elif isinstance(node, Software):
                    Software_manager.delete(node)
                Memory.update_state(node, Memory.STATE.DELETED)
                self._print_tick()
            elif Memory.STATE.STARTED == status:
                self._print_cross('The component must be stopped first')
                self._log.info('{} have to be stopped first'.format(node))
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

        def format_row(comp):
            return [comp['app_name'],
                    comp['name'],
                    comp['type'],
                    comp['state']]

        table = [format_row(c) for c in comps]
        table_str = tabulate(table, headers=['Application', 'Component',
                                             'Type', 'State'])
        Logger.println(table_str)

    def _print_outputs(self, tpl):
        if len(tpl.outputs) != 0:
            Logger.println('\nOUTPUTS:')
        for out in tpl.outputs:
            self._log.debug('value: {}'.format(out.value))
            value = out.value if isinstance(out.value, six.string_types) \
                else helper.get_attributes(out.value.args, tpl)
            Logger.println('  - ' + out.name + ":", value)

    def _update_state(self):
        errors = []

        def manage_error(comp, state):
            errors.append(comp['full_name'])
            Memory.update_state(comp, state)

        def manage_error_container(comp, state):
            manage_error(comp, state)
            path = os.path.join(self._tmp_dir, comp['app_name'], comp['name'])

            software = [(f.name, f.path) for f in scandir(path) if f.is_dir()]
            self._log.debug('path {} found {}'.format(path, software))

            for s, s_path in software:
                full_name = '{}.{}'.format(comp['app_name'], s)
                Memory.update_state('{}.{}'.format(comp['app_name'], s), state)
                # with open(os.path.join(s_path, 'state'), 'w') as f:
                #     f.write(state.value)
                try:
                    os.remove(os.path.join(s_path, 'state'))
                except FileNotFoundError:
                    pass
                errors.append(full_name)

        for c in Memory.get_comps(filters={'type': 'Software'}):
            state = glob('{}/{}/*/{}/state'.format(self._tmp_dir,
                                                   c['app_name'],
                                                   c['name']))
            self._log.debug('software update {}'.format(state))

            if len(state) == 1:
                with open(state[0], 'r') as f:
                    state = f.read().replace('\n', '')
                if state != c['state']:
                    manage_error(c, Memory.STATE(state))

        for c in Memory.get_comps(filters={'type': 'Container'}):
                status = docker_interface.inspect_container(c['full_name'])
                if status is not None:
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
                raise Exception('ERROR: the TOSCA file is not a DAG')
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
        self._stop_loading()
        Logger.println('Done')

    def _print_skip(self):
        self._stop_loading()
        Logger.println('Skipped')

    def _print_cross(self, error):
        self._stop_loading()
        Logger.println('Error ({})'.format(error))

    def _print_loading_start(self, msg):
        def loading(msg):
            t = threading.currentThread()
            t.run = True
            i = 0
            s = ['/', '-', '\\', '|']
            while t.run:
                Logger.print_("\r{} {}".format(msg, s[i % len(s)]))
                i += 1
                time.sleep(0.1)
            Logger.print_("\r{}".format(msg))

        self._loading_thread = threading.Thread(target=loading, args=(msg,))
        self._loading_thread.start()

    def _stop_loading(self):
        if hasattr(self, '_loading_thread'):
            self._loading_thread.run = False
            self._loading_thread.join()
