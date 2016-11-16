import json
import logging
import os
import shutil
from os import path
from time import sleep  # DEBUG

from docker import Client, errors
from six import print_

from tosker import utility

from .docker_engine import Docker_engine
from .nodes import Container, Software, Volume
from .software_engine import Software_engine
from .TOSCA_parser import parse_TOSCA
from .utility import Logger


class Deployer:

    def __init__(self, file_path, inputs={}, tmp_dir='/tmp/docker_tosca/'):
        self._log = Logger.get(__name__)
        self._tmp_dir = '/tmp/tosker/'
        self._inputs = {} if inputs is None else inputs
        self._tpl = parse_TOSCA(file_path, inputs)
        print_('Deploy order: ' + str(self._tpl))
        self._tmp_dir = path.join(tmp_dir, self._tpl.name)
        try:
            os.makedirs(self._tmp_dir)
        except os.error:
            pass
        self._docker = Docker_engine(self._tpl.name, self._tmp_dir)
        self._software = Software_engine(self._docker, self._tpl, self._tmp_dir)
        # print('\nDeploy order:\n  - ' + '\n  - '.join([i.name for i in self._tpl.deploy_order]))

    def create(self):
        self._docker.create_network(self._tpl.name)
        for node in self._tpl.deploy_order:
            if type(node) is Container:
                self._docker.create(node)
            elif type(node) is Volume:
                self._docker.create_volume(node)
            elif type(node) is Software:
                self._software.create(node)
                self._software.configure(node)

        self._print_outputs()

    def start(self):
        # self.create()
        for node in self._tpl.deploy_order:
            if type(node) is Container:
                stat = self._docker.inspect(node.name)
                if stat is not None:
                    node.id = stat['Id']
                    self._docker.start(node.name)
                    # sleep(1)
                else:
                    self._log.error(
                        'Container "{}" not exists!'.format(node.name))

            elif type(node) is Software:
                self._software.start(node)

        self._print_outputs()

    def stop(self):
        for node in reversed(self._tpl.deploy_order):
            if isinstance(node, Container):
                self._docker.stop(node.name)
                self._docker.create(node, saved_image=True)
            elif isinstance(node, Software):
                self._software.stop(node)

    def delete(self):
        # self.stop()
        for node in reversed(self._tpl.deploy_order):
            if isinstance(node, Container):
                self._docker.delete(node.name)
                self._docker.delete_image(
                    '{}/{}'.format(self._tpl.name, node.name)
                )
            elif isinstance(node, Software):
                self._software.delete(node)

        self._docker.delete_network(self._tpl.name)
        shutil.rmtree(self._tmp_dir)

#   def run(self):
#     self.create()
#     self.start()

    def _print_outputs(self):
        if len(self._tpl.outputs) != 0:
            print_('\nOutputs:')
        for out in self._tpl.outputs:
            self._log.debug('args: {}'.format(out.value.args))
            self._log.debug('hello_container.id: {}'.format(
                self._tpl['hello_container']))

            print_('  - ' + out.name + ":",
                   utility.get_attributes(out.value.args, self._tpl))
