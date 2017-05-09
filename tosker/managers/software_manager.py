import os
from os import path
from shutil import copy
from functools import wraps

from ..graph.nodes import Software
from ..graph.artifacts import File
from ..helper import Logger


def _get_cmd(interface, force_exec=False):
    def _get_cmd_decorator(func):
        @wraps(func)
        def func_wrapper(self, *args):
            assert isinstance(args[0], Software)
            cmd = self._get_cmd_args(args[0], interface)
            return func(self, cmd, *args) if cmd or force_exec else None
        return func_wrapper
    return _get_cmd_decorator


class Software_manager:

    def __init__(self, docker):
        self._log = Logger.get(__name__)
        self._docker = docker

    @_get_cmd('create', force_exec=True)
    def create(self, cmd, node):
        self._copy_files(node)
        if cmd is not None:
            self._docker.update_container(node.host_container, cmd)

    @_get_cmd('configure')
    def configure(self, cmd, node):
        self._docker.update_container(node.host_container, cmd)

    @_get_cmd('start')
    def start(self, cmd, node):
        try:
            self._docker.exec_cmd(node.host_container, cmd)
        except Exception as e:
            self._log.debug('is not running!')
            # self._docker.delete_container(node.host_container)
            self._docker.create_container(node.host_container,
                                          cmd=cmd,
                                          entrypoint='',
                                          from_saved=True,
                                          force=True)
            self._docker.start_container(node.host_container)

    @_get_cmd('stop')
    def stop(self, cmd, node):
        if self._docker.is_running(node.host_container):
            self._log.debug('exec stop command!')
            self._docker.exec_cmd(node.host_container, cmd)

    @_get_cmd('delete')
    def delete(self, cmd, node):
        self._log.debug('exec delete command!')
        self._docker.update_container(node.host_container, cmd)

    def _copy_files(self, node):
        # generate path for the tmp folder
        tmp = path.join(self._docker.tmp_dir,
                        node.host_container.name,
                        node.name)

        # create the folder for the software
        try:
            os.makedirs(tmp)
        except os.error:
            pass

        # copy all the interfaces scripts
        for key, value in node.interfaces.items():
            copy(value['cmd'].file_path, tmp)

        # if present copy all the artifacts
        for art in node.artifacts:
            copy(art.file_path, tmp)

    def _get_cmd_args(self, node, interface):
        def _get_inside_path(p):
            return path.join('/tmp/dt/', node.name, p.file)

        if interface not in node.interfaces:
            return None
        self._log.debug('interface: {}'.format(node.interfaces[interface]))
        args = []
        args_env = []
        res = None
        if 'inputs' in node.interfaces[interface]:
            for key, value in node.interfaces[interface]['inputs'].items():
                if isinstance(value, File):
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
