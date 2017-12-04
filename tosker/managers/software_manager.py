"""
Software manager module
"""
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

    @staticmethod
    def exec_operation(comp, interface, operation):
        """Exec an operation on the component."""
        _log = Logger.get(__name__)
        assert isinstance(comp, Software) and isinstance(interface, str) and\
               isinstance(operation, str)

        if comp.protocol.is_reset():
            _log.debug('copy file inside the container')
            SoftwareManager._copy_files(comp)
        
        cmd = SoftwareManager._get_cmd_args(comp, operation, interface=interface)
        if cmd is not None:
            docker_interface.exec_cmd(comp.host_container, cmd)
        return True

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
        for _, interface in node.interfaces.items():
            for _, value in interface.items():
                copy(value['cmd'].file_path, tmp)

        # if present copy all the artifacts
        for art in node.artifacts:
            copy(art.file_path, tmp)

    @staticmethod
    def _get_cmd_args(node, operation, interface='Standard'):
        _log = Logger.get(__name__)

        def get_inside_path(p):
            if isinstance(p, File):
                p = p.file
            return path.join('/tmp/dt/', node.name, p)

        def get_cmd():
            def get_echo(string, where):
                return 'echo {} > {}'.format(string, where)

            return 'sh -x {} >> {} 2>&1'.format(
                get_inside_path(node.interfaces[interface][operation]['cmd']),
                get_inside_path('{}.{}.log'.format(interface, operation))
            )

        if interface not in node.interfaces or\
           operation not in node.interfaces[interface]:
            _log.debug('operation %s.%s not in %s', interface,
                       operation, node.interfaces)
            return None

        args = []
        args_env = []
        res = None
        if 'inputs' in node.interfaces[interface][operation]:
            for key, value in node.interfaces[interface][operation]['inputs'].items():
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

        _log.debug('%s.%s command (%s) on container %s', interface, operation,
                   res, node.host_container)
        return res
