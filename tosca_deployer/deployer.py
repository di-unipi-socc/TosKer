import os
import json
from shutil import copy
from docker import Client, errors
from tosca_deployer import utility
from .TOSCA_parser import parse_TOSCA
from .docker_engine import Docker_engine
from .nodes import Software, Volume, Container


class Deployer:
    def __init__(self, file_path, inputs={}):
        self.inputs = {} if inputs is None else inputs
        self.tpl = parse_TOSCA(file_path, inputs)
        self.docker = Docker_engine()
        print('\nDeploy order:\n  - ' + '\n  - '.join([i.name for i in self.tpl.deploy_order]))

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
                stream = self.docker.container_exec(node.host[0],
                                                    cmd + ' ' + args,
                                                    stream=True)
                utility.print_byte(stream)

        self._print_outputs()

    def delete(self):
        self.stop()
        for node in self.tpl.container_order:
            self.docker.delete(node.name)

    # def run(self):
    #     self.create()
    #     self.start()
