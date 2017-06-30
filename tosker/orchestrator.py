import json
import logging
import os
import shutil
import six
import traceback
import threading
import time
from os import path

from termcolor import colored
from functools import wraps

from . import helper
from .docker_interface import Docker_interface
from .graph.nodes import Container, Software, Volume
from .graph.template import Template
from .managers.software_manager import Software_manager
from .managers.container_manager import Container_manager
from .managers.volume_manager import Volume_manager
from .tosca_parser import get_tosca_template
from .helper import Logger
from .storage import Storage, Memory


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
                 tmp_dir='/tmp/tosker/',
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
        Storage.set_db(data_dir)

    def orchestrate(self, file_path, commands, components=[], inputs={}):
        # Parse TOSCA file
        try:
            self._tpl = get_tosca_template(file_path, inputs)
        except Exception as e:
            Logger.println(e.args[0])
            self._log.debug(traceback.format_exc())
            return False

        # Check if inputs components exists in the TOSCA file
        if not self._components_exists(components):
            raise Exception('ERROR: a selected component do not exists')

        # Create temporany directory
        self._tmp_dir = path.join(self._tmp_dir, self._tpl.name)
        try:
            os.makedirs(self._tmp_dir)
        except os.error as e:
            self._log.info(e)

        # Initialize managers
        self._docker = Docker_interface(
            'tosker_{}'.format(self._tpl.name),
            'tosker_{}'.format(self._tpl.name),
            self._tmp_dir
        )
        self._container_manager = Container_manager(self._docker)
        self._volume_manager = Volume_manager(self._docker)
        self._software_manager = Software_manager(self._docker)

        # Start orchestration
        try:
            if len(components) == 0:
                components = [n.name for n in self._tpl.nodes]

            # must calculate the down extension/sorting
            if any((c in ('create', 'start') for c in commands)):
                down_extension = self._extend_down(components)
                down_deploy = self._sort(down_extension)
                self._log.debug('down_deploy: {}'.format(', '
                                ''.join((c.name for c in down_deploy))))
            # must calculate the up extension/sorting
            if any((c in ('stop', 'delete') for c in commands)):
                up_extension = self._extend_up(components)
                up_deploy = list(reversed(self._sort(up_extension)))
                self._log.debug('up_deploy: {}'.format(', '
                                ''.join((c.name for c in up_deploy))))

            for cmd in commands:
                {
                  'create': lambda: self._create(down_deploy),
                  'start': lambda: self._start(down_deploy),
                  'stop': lambda: self._stop(up_deploy),
                  'delete': lambda: self._delete(up_deploy),
                }.get(cmd)()

            self._print_outputs()
        except Exception as e:
            self._print_cross(e)
            # Logger.println(e)
            self._log.debug(traceback.format_exc())
            return False
        return True

    def _create(self, components):
        self._print_loading_start('Create network... ')
        self._docker.create_network()  # TODO: da rimuovere
        self._print_tick()
        for node in components:
            self._print_loading_start('Create {}... '.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.DELETED == status:
                if isinstance(node, Container):
                    self._container_manager.create(node)
                elif isinstance(node, Volume):
                    self._volume_manager.create(node)
                elif isinstance(node, Software):
                    self._software_manager.create(node)
                    self._software_manager.configure(node)

                Memory.update_state(node, Memory.STATE.CREATED)

                self._print_tick()
            else:
                self._print_skip()
                self._log.info('skipped already created')

    @_filter_components(Container, Software)
    def _start(self, components):
        for node in components:
            self._print_loading_start('Start {}... '.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.CREATED == status:
                if isinstance(node, Container):
                    self._container_manager.start(node)
                elif isinstance(node, Software):
                    self._software_manager.start(node)
                Memory.update_state(node, Memory.STATE.STARTED)
                self._print_tick()
            elif Memory.STATE.STARTED == status:
                self._print_skip()
                self._log.info('skipped already started')
            else:
                self._print_cross('the components must be created first')
                self._log.info('{} have to be created first'.format(node))

    @_filter_components(Container, Software)
    def _stop(self, components):
        for node in components:
            self._print_loading_start('Stop {}... '.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.STARTED == status:
                if isinstance(node, Container):
                    self._container_manager.stop(node)
                elif isinstance(node, Software):
                    self._software_manager.stop(node)
                Memory.update_state(node, Memory.STATE.CREATED)
                self._print_tick()
            else:
                self._print_skip()
                self._log.info('skipped already stopped')

    @_filter_components(Container, Software)
    def _delete(self, components):
        for node in components:
            self._print_loading_start('Delete {}... '.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.CREATED == status:
                if isinstance(node, Container):
                    self._container_manager.delete(node)
                elif isinstance(node, Software):
                    self._software_manager.delete(node)
                Memory.update_state(node, Memory.STATE.DELETED)
                self._print_tick()
            elif Memory.STATE.STARTED == status:
                self._print_cross('The component must be stopped first')
                self._log.info('{} have to be stopped first'.format(node))
            else:
                self._print_skip()
                self._log.info('skipped already deleted')

        self._print_loading_start('Delete network... ')
        self._docker.delete_network()
        self._print_tick()
        shutil.rmtree(self._tmp_dir)

    def _print_outputs(self):
        if len(self._tpl.outputs) != 0:
            Logger.println('\nOUTPUTS:')
        for out in self._tpl.outputs:
            self._log.debug('value: {}'.format(out.value))
            value = out.value if isinstance(out.value, six.string_types) \
                else helper.get_attributes(out.value.args, self._tpl)
            Logger.println('  - ' + out.name + ":", value)

    def _components_exists(self, components):
        for c in components:
            if not any(c == n.name for n in self._tpl.nodes):
                return False
        return True

    def _extend_down(self, components):
        assert isinstance(components, list)

        def get_down_req(c):
            for r in c.relationships:
                if r.to.name not in components:
                    yield r.to
                for c in get_down_req(r.to):
                    yield c

        return self._extend(components, get_down_req)

    def _extend_up(self, components):
        assert isinstance(components, list)

        def get_up_req(c):
            for r in c.up_requirements:
                if r.origin.name not in components:
                    yield r.origin
                # python3 alternative
                # yield from get_up_req(r.origin)
                for c in get_up_req(r.origin):
                    yield c

        return self._extend(components, get_up_req)

    def _extend(self, components, extension_gen):
        assert isinstance(components, list)

        extend_comp = []

        for c in components:
            extend_comp.append(self._tpl[c])
            for rc in extension_gen(self._tpl[c]):
                extend_comp.append(rc)

        return extend_comp

    def _sort(self, components):
        assert isinstance(components, list)

        for n in self._tpl.nodes:
            n._mark = ''
        unmarked = set((c.name for c in components))
        deploy_order = []

        def visit(n):
            if n._mark == 'temp':
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
            visit(self._tpl[n])

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
            i = 0
            s = ['/', '-', '\\', '|']
            while getattr(t, "do_run", True):
                Logger.print_("\r{} {}".format(msg, s[i % len(s)]))
                i += 1
                time.sleep(0.1)
            Logger.print_("\r{}".format(msg))

        self._loading_thread = threading.Thread(target=loading, args=(msg,))
        self._loading_thread.start()

    def _stop_loading(self):
        if hasattr(self, '_loading_thread'):
            self._loading_thread.do_run = False
            self._loading_thread.join()
