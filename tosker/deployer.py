import json
import logging
import os
import shutil
from os import path

from termcolor import colored
from docker import Client, errors
from six import print_

from tosker import utility

from .docker_interface import Docker_interface
from .nodes import Container, Software, Volume
from .software_engine import Software_engine
from .tosca_utility import get_tosca_template
from .utility import Logger


class Deployer:

    def __init__(self, file_path,
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

        self._docker = Docker_interface(self._tpl.name, self._tmp_dir)
        self._software = Software_engine(
            self._docker, self._tpl, self._tmp_dir
        )

        Logger.println('Deploy order: \n  ' + '\n  '.join(
            ['{}. {}'.format(i + 1, n)
             for i, n in enumerate(self._tpl.deploy_order)]
        ))

    def create(self):
        self._docker.create_network(self._tpl.name)
        Logger.println('\nCREATE')
        for node in self._tpl.deploy_order:
            Logger.print_('  {}'.format(node))
            try:
                if type(node) is Container:
                    if node.persistent:
                        self._docker.create(node)
                    else:
                        self._docker.pull(node.image)
                elif type(node) is Volume:
                    self._docker.create_volume(node)
                elif type(node) is Software:
                    self._software.create(node)
                    self._software.configure(node)
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

            if isinstance(node, Container) and node.persistent:
                stat = self._docker.inspect(node.name)
                if stat is not None:
                    node.id = stat['Id']
                    self._docker.start(node.name)
                    # sleep(1)
                else:
                    self._log.error(
                        'ERROR: Container "{}" not exists!'.format(node.name))

            elif isinstance(node, Software):
                self._software.start(node)

            self._print_tick()

    def stop(self):
        Logger.println('\nSTOP')
        for node in reversed(self._tpl.deploy_order):
            Logger.print_('  {}'.format(node))

            if isinstance(node, Container):
                self._docker.stop(node)
                self._docker.delete(node)
                self._docker.create(node, saved_image=True)
            elif isinstance(node, Software):
                self._software.stop(node)

            self._print_tick()

    def delete(self):
        Logger.println('\nDELETE')

        for node in reversed(self._tpl.deploy_order):
            Logger.print_('  {}'.format(node))
            try:
                if isinstance(node, Container):
                    self._docker.delete(node.name)
                    self._docker.delete_image(
                        '{}/{}'.format(self._tpl.name, node.name)
                    )
                elif isinstance(node, Software):
                    self._software.delete(node)
            except Exception as e:
                self._print_cross()
                Logger.println(e)
                exit(-1)

            self._print_tick()

        self._docker.delete_network(self._tpl.name)
        shutil.rmtree(self._tmp_dir)

#   def run(self):
#     self.create()
#     self.start()

    def print_outputs(self):
        if len(self._tpl.outputs) != 0:
            Logger.println('\nOUTPUTS:')
        for out in self._tpl.outputs:
            self._log.debug('args: {}'.format(out.value.args))
            self._log.debug('hello_container.id: {}'.format(
                self._tpl['hello_container']))

            Logger.println('  - ' + out.name + ":",
                           utility.get_attributes(out.value.args, self._tpl))

    def _print_tick(self):
        Logger.println(' ' + colored(u"\u2714", 'green'))

    def _print_cross(self):
        Logger.println(' ' + colored(u"\u274C", 'red'))
