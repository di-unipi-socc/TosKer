'''
Software manager module
'''
import os
from functools import wraps
from os import path
from shutil import copy

from .. import docker_interface
from ..graph.artifacts import File
from ..graph.nodes import Software
from ..helper import Logger
from ..storage import Memory


class SoftwareManager:

    def _get_cmd(interface, force_exec=False):
        def _get_cmd_decorator(func):
            @wraps(func)
            def func_wrapper(*args):
                assert isinstance(args[0], Software)
                cmd = SoftwareManager._get_cmd_args(args[0], interface)
                if cmd or force_exec:
                    return func(cmd, *args)
            return func_wrapper
        return _get_cmd_decorator

    @staticmethod
    @_get_cmd('create', force_exec=True)
    def create(cmd, node):
        SoftwareManager._copy_files(node)
        if cmd is not None:
            docker_interface.update_container(node.host_container, cmd)

    @staticmethod
    @_get_cmd('configure')
    def configure(cmd, node):
        docker_interface.update_container(node.host_container, cmd)

    @staticmethod
    @_get_cmd('start')
    def start(cmd, node):
        _log = Logger.get(__name__)
        try:
            docker_interface.exec_cmd(node.host_container, cmd)
        except Exception:
            _log.debug('is not running!')
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
        _log = Logger.get(__name__)
        if docker_interface.is_running(node.host_container):
            _log.debug('exec stop command!')
            docker_interface.exec_cmd(node.host_container, cmd)

    @staticmethod
    @_get_cmd('delete')
    def delete(cmd, node):
        _log = Logger.get(__name__)
        _log.debug('exec delete command!')
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
        for _, value in node.interfaces.items():
            copy(value['cmd'].file_path, tmp)

        # if present copy all the artifacts
        for art in node.artifacts:
            copy(art.file_path, tmp)

    @staticmethod
    def _get_cmd_args(node, interface):
        _log = Logger.get(__name__)

        def get_inside_path(p):
            if isinstance(p, File):
                p = p.file
            return path.join('/tmp/dt/', node.name, p)

        def get_cmd():
            def get_echo(string, where):
                return 'echo {} > {}'.format(string, where)

            def set_in_state():
                if interface == 'start':
                    return get_echo(Memory.STATE.STARTED.value,
                                    get_inside_path('state')) + ';'
                return ''

            def set_out_state():
                if interface == 'create':
                    return ';' + get_echo(Memory.STATE.CREATED.value,
                                          get_inside_path('state'))
                elif interface == 'start':
                    return ';' + get_echo(Memory.STATE.CREATED.value,
                                          get_inside_path('state'))
                elif interface == 'stop':
                    return ';' + get_echo(Memory.STATE.CREATED.value,
                                          get_inside_path('state'))
                elif interface == 'delete':
                    return ';' + get_echo(Memory.STATE.DELETED.value,
                                          get_inside_path('state'))
                return ''

            return '{}sh -x {} >> {} 2>&1{}'.format(
                set_in_state(),
                get_inside_path(node.interfaces[interface]['cmd']),
                get_inside_path('{}.log'.format(interface)),
                set_out_state()
            )

        if interface not in node.interfaces:
            return None

        args = []
        args_env = []
        res = None
        if 'inputs' in node.interfaces[interface]:
            for key, value in node.interfaces[interface]['inputs'].items():
                if isinstance(value, File):
                    value = get_inside_path(value)
                args.append('--{} {}'.format(key, value))
                args_env.append(
                    'export INPUT_{}={}'.format(key.upper(), value))

            res = "sh -c '{};{}'".format(
                ';'.join(args_env),
                get_cmd()  # ,
                # ' '.join(args)
            )
        else:
            res = "sh -c '{}'".format(get_cmd())

        _log.debug('%s command (%s) on container %s', interface,
                   res, node.host_container)
        return res
