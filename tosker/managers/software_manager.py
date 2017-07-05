import os
from os import path
from shutil import copy
from functools import wraps

from ..graph.nodes import Software
from ..graph.artifacts import File
from ..helper import Logger
from .. import docker_interface


def _get_cmd(interface, force_exec=False):
    def _get_cmd_decorator(func):
        @wraps(func)
        def func_wrapper(*args):
            assert isinstance(args[0], Software)
            cmd = Software_manager._get_cmd_args(args[0], interface)
            return func(cmd, *args) if cmd or force_exec else None
        return func_wrapper
    return _get_cmd_decorator


class Software_manager:

    _log = Logger.get(__name__)
    # def __init__(self):
    #     self._log = Logger.get(__name__)
    #     # docker_interface = docker

    @staticmethod
    @_get_cmd('create', force_exec=True)
    def create(cmd, node):
        Software_manager._copy_files(node)
        if cmd is not None:
            docker_interface.update_container(node.host_container, cmd)

    @staticmethod
    @_get_cmd('configure')
    def configure(cmd, node):
        docker_interface.update_container(node.host_container, cmd)

    @staticmethod
    @_get_cmd('start')
    def start(cmd, node):
        try:
            docker_interface.exec_cmd(node.host_container, cmd)
        except Exception as e:
            Software_manager._log.debug('is not running!')
            # docker_interface.delete_container(node.host_container)
            docker_interface.create_container(node.host_container,
                                              cmd=cmd,
                                              entrypoint='',
                                              from_saved=True,
                                              force=True)
            docker_interface.start_container(node.host_container)

    @staticmethod
    @_get_cmd('stop')
    def stop(cmd, node):
        if docker_interface.is_running(node.host_container):
            Software_manager._log.debug('exec stop command!')
            docker_interface.exec_cmd(node.host_container, cmd)

    @staticmethod
    @_get_cmd('delete')
    def delete(cmd, node):
        Software_manager._log.debug('exec delete command!')
        docker_interface.update_container(node.host_container, cmd)

    @staticmethod
    def _copy_files(node):
        # generate path for the tmp folder
        tmp = path.join(node.tpl.tmp_dir,
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

    @staticmethod
    def _get_cmd_args(node, interface):
        def _get_inside_path(p):
            return path.join('/tmp/dt/', node.name, p.file)

        if interface not in node.interfaces:
            return None
        Software_manager._log.debug('interface: {}'
                                    ''.format(node.interfaces[interface]))
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

        Software_manager._log.debug('{} command ({}) on container {}'
                                    ''.format(interface, res,
                                              node.host_container))
        return res
