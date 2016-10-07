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
        print ('Deploy order: ' + str(self._tpl))
        self._docker = Docker_engine()
        self._net_name = self._tpl.name
        self._docker.create_network(self._net_name)
        # print('\nDeploy order:\n  - ' + '\n  - '.join([i.name for i in self._tpl.deploy_order]))

    def create(self):
        for node in self._tpl.deploy_order:
            if type(node) is Container:
                node.id = self._docker.create(node, self._net_name)
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
                # self._docker.wait(node.name)

            elif type(node) is Software:
                self._copy_files(node)

                if self._get_cmnd_args(node, 'create'):
                    cmd = 'sh -c "{} ; {}"'.format(
                        self._get_cmnd_args(node, 'create'),
                        self._get_cmnd_args(node, 'start'))
                else:
                    cmd = self._get_cmnd_args(node, 'start')

                self.log.debug('cmd: {}'.format(cmd))

                # TODO: node.host[0] can be another software node
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
                    # sleep(1)
                    self._docker.container_exec(host_container.name, cmd)
                except errors.APIError:
                    self.log.info('The cointainer {} is not running'.format(host_container.name))
                    host_container.cmd = cmd
                    self.log.debug('container_conf: {}'.format(host_container))
                    host_container.id = self._docker.create(host_container, self._net_name)
                    self._docker.start(host_container.id)

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

    def _copy_files(self, node):
        # TODO: node.host[0] is not correct if a solftware is hosted on another software
        tmp = '/tmp/docker_tosca/' + node.host[0] + '/'
        for key, value in node.interfaces.items():
            copy(value['cmd'], tmp)
            node.interfaces[key]['cmd'] = '/tmp/dt/' + value['cmd'].split('/')[-1]

        for key, value in node.artifacts.items():
            copy(value, tmp)
            node.artifacts[key] = '/tmp/dt/' + value.split('/')[-1]

    def _get_cmnd_args(self, node, interface):
        if interface not in node.interfaces:
            return None
        self.log.debug('interface: {}'.format(node.interfaces[interface]))
        args = []
        for key, value in node.interfaces[interface]['inputs'].items():
            if type(value) is dict:
                if 'get_artifact' in value:
                    self.log.debug('artifacts: {}'.format(node.artifacts))
                    value = node.artifacts[value['get_artifact'][1]]
            args.append('--{} {}'.format(key, value))

        return 'sh {} {}'.format(node.interfaces[interface]['cmd'], ' '.join(args))
