import os
import json
import logging
from shutil import copy
from docker import Client, errors
from tosca_deployer import utility
from .TOSCA_parser import parse_TOSCA
from .docker_engine import Docker_engine
from .nodes import Software, Volume, Container
from .utility import Logger
# DEBUG
from time import sleep


class Deployer:
    def __init__(self, file_path, inputs={}, log_level=logging.ERROR):
        Logger.main_level = log_level
        self.log = Logger.get(__name__)
        self._inputs = {} if inputs is None else inputs
        self._tpl = parse_TOSCA(file_path, inputs)
        self.log.info('Deploy order: ' + str(self._tpl))
        self._docker = Docker_engine()
        # print('\nDeploy order:\n  - ' + '\n  - '.join([i.name for i in self._tpl.deploy_order]))

    def _print_outputs(self):
        if len(self._tpl.outputs) != 0:
            print ('\nOutputs:')
        for out in self._tpl.outputs:
            print ('  - ' + out.name + ":", utility.get_attributes(out.value.args, self._tpl))

    def create(self):
        for node in self._tpl.deploy_order:
            if type(node) is Container:
                node.id = self._docker.create(node)
            elif type(node) is Volume:
                self._docker.create_volume(node)

    def stop(self):
        for node in reversed(self._tpl.container_order):
            self._docker.stop(node.name)

    def start(self):
        # TODO: check if the container arleady exists
        self.create()
        for node in self._tpl.deploy_order:
            if type(node) is Container:
                self._docker.start(node.name)
            elif type(node) is Software:
                tmp = '/tmp/docker_tosca/' + node.host[0] + '/'
                copy(node.cmd, tmp)
                node.cmd = '/tmp/dt/' + node.cmd.split('/')[-1]
                for key, value in node.artifacts.items():
                    copy(value, tmp)
                    value = '/tmp/dt/' + value.split('/')[-1]
                self.log.debug('inputs {}'.format(node.inputs))
                for key, value in node.inputs.items():
                    node.inputs[key] = '/tmp/dt/' + value.split('/')[-1]
                self.log.debug('inputs: {}'.format(node.inputs))
                args = ' '.join(['--'+i[0]+' '+i[1] for i in node.inputs.items()])
                cmd = 'sh ' + node.cmd
                cmd_args = cmd + ' ' + args
                self.log.debug('cmd: {}'.format(cmd_args))

                host_container = self._tpl[node.host[0]]

                if node.link is not None:
                    def get_container(node):
                        self.log.debug('node: {}'.format(node))

                        if type(node) is Container:
                            return node
                        else:
                            return get_container(self._tpl[node.host[0]])

                    for link in node.link:
                        self.log.debug('link: {}'.format(link))
                        container_name = get_container(self._tpl[link]).name
                        host_container.add_link((container_name, link))

                try:
                    sleep(1)
                    stream = self._docker.container_exec(host_container.name,
                                                         cmd_args,
                                                         stream=True)
                    # utility.print_byte(stream)
                except errors.APIError:
                    host_container.cmd = cmd_args
                    self.log.debug('container_conf: {}'.format(host_container))
                    host_container.id = self._docker.create(host_container)
                    self._docker.start(host_container.id)

        self._print_outputs()

    def delete(self):
        self.stop()
        for node in self._tpl.container_order:
            self._docker.delete(node.name)

    # def run(self):
    #     self.create()
    #     self.start()
