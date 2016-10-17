from .utility import Logger
from .nodes import Container
from shutil import copy
import os


class Software_engine:

    def __init__(self, docker, tpl):
        self._log = Logger.get(__name__)
        self._docker = docker
        self._tpl = tpl

    def create(self, node):
        self._copy_files(node)

        cmd = self._get_cmnd_args(node, 'create')
        self._log.debug('cmd: {}'.format(cmd))

        if cmd is None:
            return

        self._docker.update_container(node.host_container, cmd)
        # node.host_container.cmd, old_cmd = cmd, node.host_container.cmd
        # # self._log.debug('container_conf: {}'.format(node.host_container))
        # self._docker.create(node.host_container)
        # self._docker.start(node.host_container.id, wait=True)
        # self._docker.stop(node.host_container.id)
        # node.host_container.cmd = old_cmd
        # self._log.debug('old_cmd: {}'.format(node.host_container.cmd))
        # self._docker.update_container(node.host_container)

    def start(self, node):
        # TODO: here only to update artifact path inside the Container
        # self._copy_files(node)

        host_container = node.host_container
        cmd = self._get_cmnd_args(node, 'start')

        if cmd is None:
            return
        self._log.debug('start cmd: {}'.format(cmd))

        if self._docker.is_running(host_container.name):
            self._log.debug('is running!')
            self._docker.container_exec(host_container.name, cmd)
        else:
            self._log.debug('is not running!')
            self._docker.create(host_container,
                                cmd=cmd,
                                entrypoint='',
                                saved_image=True)
            self._docker.start(host_container.id)

    def _copy_files(self, node):
        tmp = '/tmp/docker_tosca/' + node.host_container.name + '/' + node.name
        os.makedirs(tmp, exist_ok=True)

        for key, value in node.interfaces.items():
            copy(value['cmd']['file_path'], tmp)
            # node.interfaces[key]['cmd'] = '/tmp/dt/' + value['cmd'].split('/')[-1]

        if node.artifacts:
            for key, value in node.artifacts.items():
                copy(value['file_path'], tmp)
                # node.artifacts[key] = '/tmp/dt/' + value.split('/')[-1]

    def _get_cmnd_args(self, node, interface):
        def _get_inside_path(path):
            return '/tmp/dt/' + node.name + '/' + path['file']

        self._log.debug('interface: {}'.format(node.interfaces))
        if interface not in node.interfaces:
            return None
        self._log.debug('interface: {}'.format(node.interfaces[interface]))
        args = []
        args_env = []
        if 'inputs' in node.interfaces[interface]:
            for key, value in node.interfaces[interface]['inputs'].items():
                if type(value) is dict:
                    if 'get_artifact' in value:
                        self._log.debug('artifacts: {}'.format(node.artifacts))
                        value = _get_inside_path(
                            node.artifacts[value['get_artifact'][1]]
                        )
                args.append('--{} {}'.format(key, value))
                args_env.append('export INPUT_{}={}'.format(key.upper(), value))

        # TODO: generate an incorrect comand when there aren't inputs
        return 'sh -c \'{};sh {} {}\''.format(
            ';'.join(args_env),
            _get_inside_path(node.interfaces[interface]['cmd']),
            ' '.join(args)
        )
