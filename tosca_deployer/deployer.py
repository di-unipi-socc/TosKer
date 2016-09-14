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
        self.deploy_order, self.outputs = parse_TOSCA(file_path, inputs)
        self.docker = Docker_engine()
        print('\nDeploy order:\n  - ' + '\n  - '.join([i[0] for i in self.deploy_order]))

    def _print_outputs(self):
        if len(self.outputs) != 0:
            print ('\nOutputs:')
        for out in self.outputs:
            nodes = {}
            for i, j in self.deploy_order:
                nodes[i] = j
            print ('  - ' + out.name + ":", utility.get_attributes(out.value.args, nodes))

    def create(self):
        for node in self.deploy_order:
            name, conf = node
            if type(conf) is Container:
                conf.id = self.docker.create(conf)
            elif type(conf) is Volume:
                print ('create_volume', self.docker.create_volume(conf))
            #     # cp conf['artifacts'] /tmp/docker_tosca/conf['requirements']['host'][0]
            #     tmp = '/tmp/docker_tosca/' + conf['host'][0] + '/'
            #     os.makedirs(tmp, exist_ok=True)
            #     copy(conf['cmd'], tmp)
            #     conf['cmd'] = '/tmp/dt/' + conf['cmd'].split('/')[-1]
            #     for key, value in conf['artifacts'].items():
            #         copy(value, tmp)
            #         value = '/tmp/dt/' + value.split('/')[-1]
            #     for key, value in conf['inputs']:
            #         value = conf['artifacts'][key]
            #     # self.docker.container_exec(conf['host'][0],
            #     # 'sh -c \'' + conf['cmd'] + ' ' + str(conf['inputs']) + '\'')

    def stop(self):
        for node in reversed([i for i in self.deploy_order if type(i[1]) is Container]):
            name, conf = node
            self.docker.stop(name)

    def start(self):
        # TODO: check if the container arleady exists
        self.create()
        for node in self.deploy_order:
            name, conf = node
            if type(conf) is Container:
                self.docker.start(name)
            elif type(conf) is Software:
                tmp = '/tmp/docker_tosca/' + conf.host[0] + '/'
                copy(conf.cmd, tmp)
                conf.cmd = '/tmp/dt/' + conf.cmd.split('/')[-1]
                for key, value in conf.artifacts.items():
                    copy(value, tmp)
                    value = '/tmp/dt/' + value.split('/')[-1]
                print('inputs', conf.inputs)
                for key, value in conf.inputs.items():
                    conf.inputs[key] = '/tmp/dt/' + value.split('/')[-1]
                print('inputs', conf.inputs)
                args = ' '.join(['--'+i[0]+' '+i[1] for i in conf.inputs.items()])
                cmd = 'sh ' + conf.cmd
                stream = self.docker.container_exec(conf.host[0],
                                                    cmd + ' ' + args,
                                                    stream=True)
                utility.print_byte(stream)

        self._print_outputs()

    def delete(self):
        self.stop()
        for node in self.deploy_order:
            name, conf = node
            if type(conf) is Container:
                self.docker.delete(name)
            # elif conf['type'] == 'volume':
            #     self.docker.delete_volume(name)

    # def run(self):
    #     self.create()
    #     self.start()
