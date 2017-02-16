import json
import logging
import os
import shutil
from os import path

from termcolor import colored
from docker import Client, errors
from six import print_

from tosker import helper

from .docker_interface import Docker_interface
from .graph.nodes import Container, Software, Volume
from .managers.software_manager import Software_manager
from .managers.container_manager import Container_manager
from .managers.volume_manager import Volume_manager
from .tosca_utility import get_tosca_template
from .helper import Logger


class Orchestrator:

    def __init__(self,
                 file_path,
                 inputs={},
                 log_handler=logging.NullHandler(),
                 quiet=True,
                 tmp_dir='/tmp/tosker/'):
        Logger.set(log_handler, quiet)
        self._log = Logger.get(__name__)

        self._tpl = get_tosca_template(file_path, inputs)
        self._tmp_dir = path.join(tmp_dir, self._tpl.name)
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

    def create(self):
        self._docker.create_network()  # TODO: da rimuovere
        Logger.println('\nCREATE')
        for node in self._tpl.deploy_order:
            Logger.print_('  {}'.format(node))

            try:
                if isinstance(node, Container):
                    self._container_manager.create(node)
                elif isinstance(node, Volume):
                    self._volume_manager.create(node)
                elif isinstance(node, Software):
                    self._software_manager.create(node)
                    self._software_manager.configure(node)
            except Exception as e:
                self._print_cross()
                Logger.println(e)
                self._log.exception(e)
                exit(-1)

            self._print_tick()

    def start(self):
        Logger.println('\nSTART')
        for node in self._tpl.deploy_order:
            Logger.print_('  {}'.format(node))

            if isinstance(node, Container):
                self._container_manager.start(node)
            elif isinstance(node, Software):
                self._software_manager.start(node)

            self._print_tick()

    def stop(self):
        Logger.println('\nSTOP')
        for node in reversed(self._tpl.deploy_order):
            Logger.print_('  {}'.format(node))

            if isinstance(node, Container):
                self._container_manager.stop(node)
            elif isinstance(node, Software):
                self._software_manager.stop(node)

            self._print_tick()

    def delete(self):
        Logger.println('\nDELETE')
        for node in reversed(self._tpl.deploy_order):
            Logger.print_('  {}'.format(node))
            try:
                if isinstance(node, Container):
                    self._container_manager.delete(node)
                elif isinstance(node, Software):
                    self._software_manager.delete(node)
            except Exception as e:
                self._print_cross()
                Logger.println(e)
                exit(-1)

            self._print_tick()

        self._docker.delete_network()
        shutil.rmtree(self._tmp_dir)

    def print_outputs(self):
        if len(self._tpl.outputs) != 0:
            Logger.println('\nOUTPUTS:')
        for out in self._tpl.outputs:
            self._log.debug('args: {}'.format(out.value.args))
            Logger.println('  - ' + out.name + ":",
                           helper.get_attributes(out.value.args, self._tpl))

    def _print_tick(self):
        Logger.println(' ' + colored(u"\u2714", 'green'))

    def _print_cross(self):
        Logger.println(' ' + colored(u"\u274C", 'red'))
