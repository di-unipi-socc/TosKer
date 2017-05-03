import json
import logging
import os
import shutil
import six
from os import path

from termcolor import colored
from functools import wraps

from . import helper
from .docker_interface import Docker_interface
from .graph.nodes import Container, Software, Volume
from .managers.software_manager import Software_manager
from .managers.container_manager import Container_manager
from .managers.volume_manager import Volume_manager
from .tosca_parser import get_tosca_template
from .helper import Logger


class Orchestrator:

    def __init__(self,
                 log_handler=logging.NullHandler(),
                 quiet=True,
                 tmp_dir='/tmp/tosker/'):
        Logger.set(log_handler, quiet)
        self._log = Logger.get(__name__)
        self._tmp_dir = tmp_dir

    def orchestrate(self, file_path, commands, components=[], inputs={}):
        if not self._parse(file_path, components, inputs):
            return False
        try:
            for cmd in commands:
                {
                  'create': self._create,
                  'start': self._start,
                  'stop': self._stop,
                  'delete': self._delete,
                }.get(cmd)()

            self._print_outputs()
        except Exception as e:
            self._print_cross()
            Logger.println(e)
            self._log.exception(e)
            return False
        return True

    def _parse(self, file_path, components=[], inputs={}):
        try:
            self._tpl = get_tosca_template(file_path, inputs, components)
        except Exception as e:
            Logger.println(e.args[0])
            return False

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

        Logger.println('Deploy order: \n  ' + '\n  '.join(
            ['{}. {}'.format(i + 1, n)
             for i, n in enumerate(self._tpl.deploy_order)]
        ))
        return True

    def _create(self):
        self._log.debug('create operation')
        self._docker.create_network()  # TODO: da rimuovere
        Logger.println('\nCREATE')
        for node in self._tpl.deploy_order:
            Logger.print_('  {}'.format(node))

            # try:
            if isinstance(node, Container):
                self._container_manager.create(node)
            elif isinstance(node, Volume):
                self._volume_manager.create(node)
            elif isinstance(node, Software):
                self._software_manager.create(node)
                self._software_manager.configure(node)
            # except Exception as e:
                # TODO: catch this error

            self._print_tick()

    def _start(self):
        Logger.println('\nSTART')
        for node in self._tpl.deploy_order:
            Logger.print_('  {}'.format(node))

            if isinstance(node, Container):
                self._container_manager.start(node)
            elif isinstance(node, Software):
                self._software_manager.start(node)

            self._print_tick()

    def _stop(self):
        Logger.println('\nSTOP')
        for node in reversed(self._tpl.deploy_order):
            Logger.print_('  {}'.format(node))

            if isinstance(node, Container):
                self._container_manager.stop(node)
            elif isinstance(node, Software):
                self._software_manager.stop(node)

            self._print_tick()

    def _delete(self):
        Logger.println('\nDELETE')
        for node in reversed(self._tpl.deploy_order):
            Logger.print_('  {}'.format(node))
            # try:
            if isinstance(node, Container):
                self._container_manager.delete(node)
            elif isinstance(node, Software):
                self._software_manager.delete(node)
            # except Exception as e:
            #     self._print_cross()
            #     Logger.println(e)
            #     raise e
            #     # TODO: catch this error

            self._print_tick()

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

    def _print_cross(self):
        Logger.println(' ' + colored(u"\u274C", 'red'))
