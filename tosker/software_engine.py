import os
from os import path
from shutil import copy

from .nodes import Container
from .utility import Logger


class Software_engine:

    def __init__(self, docker, tpl, tmp_dir):
        self._log = Logger.get(__name__)
        self._docker = docker
        self._tpl = tpl
        self._tmp_dir = tmp_dir

    def create(self, node):
        self._copy_files(node)

        cmd = self._get_cmd_args(node, 'create')

        if cmd is None:
            return

        self._docker.update_container(node.host_container, cmd)

    def configure(self, node):
        cmd = self._get_cmd_args(node, 'configure')

        if cmd is None:
            return

        self._docker.update_container(node.host_container, cmd)

    def start(self, node):
        cmd = self._get_cmd_args(node, 'start')

        if cmd is None:
            return

        status = self._docker.exec_cmd(node.host_container, cmd)
        if not status:
            self._log.debug('is not running!')
            self._docker.delete(node.host_container)
            self._docker.create(node.host_container,
                                cmd=cmd,
                                entrypoint='',
                                saved_image=True)
            self._docker.start(node.host_container)

    def stop(self, node):
        cmd = self._get_cmd_args(node, 'stop')

        if cmd is None:
            return

        if self._docker.is_running(node.host_container):
            self._log.debug('exec stop command!')
            self._docker.exec_cmd(node.host_container, cmd)

    def delete(self, node):
        cmd = self._get_cmd_args(node, 'delete')

        if cmd is None:
            return

        if self._docker.is_running(node.host_container):
            self._log.debug('exec delete command!')
            self._docker.exec_cmd(node.host_container, cmd)

    def _copy_files(self, node):
        tmp = path.join(self._tmp_dir, node.host_container.name, node.name)
        try:
            os.makedirs(tmp)
        except os.error:
            pass

        for key, value in node.interfaces.items():
            copy(value['cmd']['file_path'], tmp)

        if node.artifacts:
            for key, value in node.artifacts.items():
                copy(value['file_path'], tmp)

    def _get_cmd_args(self, node, interface):
        def _get_inside_path(p):
            return path.join('/tmp/dt/', node.name, p['file'])

        # self._log.debug('interface: {}'.format(node.interfaces))
        if interface not in node.interfaces:
            return None
        self._log.debug('interface: {}'.format(node.interfaces[interface]))
        args = []
        args_env = []
        res = None
        if 'inputs' in node.interfaces[interface]:
            for key, value in node.interfaces[interface]['inputs'].items():
                if type(value) is dict:
                    value = _get_inside_path(value)
                args.append('--{} {}'.format(key, value))
                args_env.append(
                    'export INPUT_{}={}'.format(key.upper(), value))

            res = 'sh -c \'{};sh {} {}\''.format(
                ';'.join(args_env),
                _get_inside_path(node.interfaces[interface]['cmd']),
                ' '.join(args)
            )
        else:
            res = 'sh {}'.format(
                _get_inside_path(node.interfaces[interface]['cmd']),
            )

        self._log.debug('{} command ({}) on container {}'
                        .format(interface, res, node.host_container))
        return res
