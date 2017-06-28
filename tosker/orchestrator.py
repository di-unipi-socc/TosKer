import json
import logging
import os
import shutil
import six
import traceback
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


class Orchestrator:

    def __init__(self,
                 log_handler=logging.NullHandler(),
                 quiet=True,
                 tmp_dir='/tmp/tosker/',
                 data_dir='/tmp/tosker'):  # TODO: use /usr/lib/tokser instead
        Logger.set(log_handler, quiet)
        self._log = Logger.get(__name__)
        self._tmp_dir = tmp_dir

        self._data_dir = data_dir
        try:
            os.makedirs(data_dir)
        except os.error as e:
            self._log.info(e)

        Storage.set_db(data_dir)

    def orchestrate(self, file_path, commands, components=[], inputs={}):
        if not self._parse(file_path, components, inputs):
            return False

        try:
            if len(components) != 0:
                # must calculate the down extension/sorting
                if any((c in ('create', 'start') for c in commands)):
                    down_extension = _extend_down(components, self._tpl)
                    down_deploy = _sort(down_extension, self._tpl)

                # must calculate the up extension/sorting
                if any((c in ('stop', 'delete') for c in commands)):
                    up_extension = _extend_up(components, self._tpl)
                    up_deploy = _sort(up_extension, self._tpl)
            else:
                all_deploy = _sort(list(self._tpl.nodes), self._tpl)

            for cmd in commands:
                if len(components) != 0:
                    if cmd in ('create', 'start'):
                        sorted_components = down_deploy
                    else:
                        sorted_components = up_deploy
                else:
                    sorted_components = all_deploy

                self._log.debug('components {}'.format(','.join((c.name for c in sorted_components))))
                # TODO: inefficient should sort max 2 times
                # sorted_components = _sort(to_deploy, self._tpl)

                # Logger.println('Deploy order: \n  ' + '\n  '.join(
                #     ['{}. {}'.format(i + 1, n)
                #      for i, n in enumerate(self._tpl.nodes)]
                # ))

                {
                  'create': self._create,
                  'start': self._start,
                  'stop': self._stop,
                  'delete': self._delete,
                }.get(cmd)(sorted_components)

            self._print_outputs()
        except Exception as e:
            self._print_cross()
            Logger.println(e)
            self._log.debug(traceback.format_exc())
            return False
        return True

    def _parse(self, file_path, components=[], inputs={}):
        try:
            self._tpl = get_tosca_template(file_path, inputs)
        except Exception as e:
            Logger.println(e.args[0])
            self._log.debug(traceback.format_exc())
            return False

        if not _components_exists(self._tpl, components):
            raise Exception('ERROR: a selected component do not exists')

        self._tmp_dir = path.join(self._tmp_dir, self._tpl.name)
        try:
            os.makedirs(self._tmp_dir)
        except os.error as e:
            self._log.info(e)

        self._docker = Docker_interface(
            'tosker_{}'.format(self._tpl.name),
            'tosker_{}'.format(self._tpl.name),
            self._tmp_dir
        )
        self._container_manager = Container_manager(self._docker)
        self._volume_manager = Volume_manager(self._docker)
        self._software_manager = Software_manager(self._docker)

        return True

    def _create(self, components):
        self._log.debug('create operation')
        self._docker.create_network()  # TODO: da rimuovere
        Logger.println('CREATE')
        for node in components:
            Logger.print_('  {}'.format(node))

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

    def _start(self, components):
        Logger.println('START')
        for node in components:
            Logger.print_('  {}'.format(node))

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
                self._print_cross()
                self._log.info('{} have to be created first'.format(node))

    def _stop(self, components):
        Logger.println('STOP')
        for node in reversed(components):
            Logger.print_('  {}'.format(node))

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

    def _delete(self, components):
        Logger.println('DELETE')
        for node in reversed(components):
            Logger.print_('  {}'.format(node))

            status = Memory.get_comp_state(node)
            if Memory.STATE.CREATED == status:
                if isinstance(node, Container):
                    self._container_manager.delete(node)
                elif isinstance(node, Software):
                    self._software_manager.delete(node)
                Memory.update_state(node, Memory.STATE.DELETED)
                self._print_tick()
            elif Memory.STATE.STARTED == status:
                self._print_cross()
                self._log.info('{} have to be stopped first'.format(node))
            else:
                self._print_skip()
                self._log.info('skipped already deleted')

        self._docker.delete_network()
        shutil.rmtree(self._tmp_dir)

    def _print_outputs(self):
        if len(self._tpl.outputs) != 0:
            Logger.println('\nOUTPUTS:')
        for out in self._tpl.outputs:
            self._log.debug('value: {}'.format(out.value))
            value = out.value if isinstance(out.value, six.string_types) \
                else helper.get_attributes(out.value.args, self._tpl)
            Logger.println('  - ' + out.name + ":", value)

    def _print_tick(self):
        Logger.println(' ' + colored(u"\u2714", 'green'))

    def _print_skip(self):
        Logger.println(' ' + colored(u"\u2714", 'white'))

    def _print_cross(self):
        Logger.println(' ' + colored(u"\u274C", 'red'))


def _components_exists(tpl, components):
    for c in components:
        if not any(c == n.name for n in tpl.nodes):
            return False
    return True


def _extend_down(components, tpl):
    assert isinstance(components, list) and isinstance(tpl, Template)

    def get_down_req(c):
        for r in c.relationships:
            if r.to.name not in components:
                yield r.to
            for c in get_down_req(r.to):
                yield c

    return _extend(components, tpl, get_down_req)


def _extend_up(components, tpl):
    assert isinstance(components, list) and isinstance(tpl, Template)

    def get_up_req(c):
        for r in c.up_requirements:
            if r.origin.name not in components:
                yield r.origin
            for c in get_up_req(r.origin):
                yield c

    return _extend(components, tpl, get_up_req)


def _extend(components, tpl, extension_gen):
    assert isinstance(components, list) and isinstance(tpl, Template)

    extend_comp = []

    for c in components:
        extend_comp.append(tpl[c])
        for rc in extension_gen(tpl[c]):
            extend_comp.append(rc)

    return extend_comp


def _sort(components, tpl):
    assert isinstance(components, list) and isinstance(tpl, Template)

    for n in tpl.nodes:
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
        visit(tpl[n])

    return deploy_order
