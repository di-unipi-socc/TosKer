import os
import json
from shutil import copy
from docker import Client, errors
from tosca_deployer import utility
from .TOSCA_parser import parse_TOSCA
from .docker_engine import Docker_engine
from .nodes import Software, Volume, Container

# DEBUG
from time import sleep


class Deployer:
    def __init__(self, file_path, inputs={}):
        self.inputs = {} if inputs is None else inputs
        self.tpl = parse_TOSCA(file_path, inputs)
        print ('\nDeploy order:\n' + str(self.tpl))
        self.docker = Docker_engine()
        # print('\nDeploy order:\n  - ' + '\n  - '.join([i.name for i in self.tpl.deploy_order]))

    def _print_outputs(self):
        if len(self.tpl.outputs) != 0:
            print ('\nOutputs:')
        for out in self.tpl.outputs:
            print ('  - ' + out.name + ":", utility.get_attributes(out.value.args, self.tpl))

    def create(self):
        for node in self.tpl.deploy_order:
            if type(node) is Container:
                node.id = self.docker.create(node)
            elif type(node) is Volume:
                print ('create_volume', self.docker.create_volume(node))

    def stop(self):
        for node in reversed(self.tpl.container_order):
            self.docker.stop(node.name)

    def start(self):
        # TODO: check if the container arleady exists
        self.create()
        for node in self.tpl.deploy_order:
            if type(node) is Container:
                self.docker.start(node.name)
            elif type(node) is Software:
                tmp = '/tmp/docker_tosca/' + node.host[0] + '/'
                copy(node.cmd, tmp)
                node.cmd = '/tmp/dt/' + node.cmd.split('/')[-1]
                for key, value in node.artifacts.items():
                    copy(value, tmp)
                    value = '/tmp/dt/' + value.split('/')[-1]
                print('inputs', node.inputs)
                for key, value in node.inputs.items():
                    node.inputs[key] = '/tmp/dt/' + value.split('/')[-1]
                print('inputs', node.inputs)
                args = ' '.join(['--'+i[0]+' '+i[1] for i in node.inputs.items()])
                cmd = 'sh ' + node.cmd
                print ('DEBUG: ', cmd + ' ' + args)

                host_container = self.tpl[node.host[0]]

                if node.link is not None:
                    def get_container(node):
                        print ('DEBUG: ', 'node', node)
                        if type(node) is Container:
                            return node
                        else:
                            return get_container(self.tpl[node.host[0]])

                    for link in node.link:
                        print ('DEBUG: ', link)
                        container_name = get_container(self.tpl[link]).name
                        host_container.add_link((container_name, link))

                try:
                    sleep(1)
                    stream = self.docker.container_exec(host_container.name,
                                                        cmd + ' ' + args,
                                                        stream=True)
                    utility.print_byte(stream)
                except errors.APIError:
                    host_container.cmd = cmd + ' ' + args
                    print ('DEBUG: ', 'container_conf ', host_container)
                    host_container.id = self.docker.create(host_container)
                    self.docker.start(host_container.id)

        self._print_outputs()

    def delete(self):
        self.stop()
        for node in self.tpl.container_order:
            self.docker.delete(node.name)

    # def run(self):
    #     self.create()
    #     self.start()
