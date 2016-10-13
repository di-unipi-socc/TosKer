import os
import json
import logging
from docker import Client, errors
from tosca_deployer import utility
from .TOSCA_parser import parse_TOSCA
from .docker_engine import Docker_engine
from .software_engine import Software_engine
from .nodes import Software, Volume, Container
from .utility import Logger
# DEBUG
from time import sleep


class Deployer:
    def __init__(self, file_path, inputs={}, log_level=logging.ERROR):
        Logger.main_level = log_level
        self._log = Logger.get(__name__)
        self._inputs = {} if inputs is None else inputs
        self._tpl = parse_TOSCA(file_path, inputs)
        print ('Deploy order: ' + str(self._tpl))
        self._docker = Docker_engine(self._tpl.name)
        self._software = Software_engine(self._docker, self._tpl)
        self._docker.create_network(self._tpl.name)
        # print('\nDeploy order:\n  - ' + '\n  - '.join([i.name for i in self._tpl.deploy_order]))

    def create(self):
        for node in self._tpl.deploy_order:
            if type(node) is Container:
                self._docker.create(node)
            elif type(node) is Volume:
                self._docker.create_volume(node)
            elif type(node) is Software:
                self._software.create(node)

    def stop(self):
        for node in reversed(self._tpl.container_order):
            self._docker.stop(node.name)

    def start(self):
        # TODO: check if the container arleady exists
        self.create()
        for node in self._tpl.deploy_order:
            if type(node) is Container:
                self._docker.start(node.name)
                # self._docker.wait(node.name)

            elif type(node) is Software:
                self._software.start(node)

        self._print_outputs()

    def delete(self):
        self.stop()
        for node in self._tpl.container_order:
            self._docker.delete(node.name)

    # def run(self):
    #     self.create()
    #     self.start()

    def _print_outputs(self):
        if len(self._tpl.outputs) != 0:
            print ('\nOutputs:')
        for out in self._tpl.outputs:
            print ('  - ' + out.name + ":", utility.get_attributes(out.value.args, self._tpl))
