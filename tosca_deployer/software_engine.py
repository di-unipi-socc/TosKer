from .utility import Logger
from shutil import copy


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

        # TODO: node.host[0] can be another software node
        host_container = self._tpl[node.host[0]]
        if node.link is not None:
            def get_container(node):
                self._log.debug('node: {}'.format(node))
                if type(node) is Container:
                    return node
                else:
                    return get_container(self._tpl[node.host[0]])

            for link in node.link:
                self._log.debug('link: {}'.format(link))
                container_name = get_container(self._tpl[link]).name
                host_container.add_link((container_name, link))

        host_container.cmd = cmd
        self._log.debug('container_conf: {}'.format(host_container))
        self._docker.create(host_container)
        self._docker.start(host_container.id, wait=True)
        self._docker.stop(host_container.id)

        self._docker.commit(host_container)
        self._docker.create(host_container)

    def start(self, node):
        # TODO: node.host[0] can be another software node
        host_container = self._tpl[node.host[0]]
        cmd = self._get_cmnd_args(node, 'start')
        if cmd is None:
            return

        if self._docker.is_running(host_container.name):
            self._docker.container_exec(host_container.name, cmd)
        else:
            host_container.cmd = cmd
            self._docker.create(host_container)
            self._docker.start(host_container.id)

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
        self._log.debug('interface: {}'.format(node.interfaces[interface]))
        args = []
        for key, value in node.interfaces[interface]['inputs'].items():
            if type(value) is dict:
                if 'get_artifact' in value:
                    self._log.debug('artifacts: {}'.format(node.artifacts))
                    value = node.artifacts[value['get_artifact'][1]]
            args.append('--{} {}'.format(key, value))

        return 'sh {} {}'.format(node.interfaces[interface]['cmd'], ' '.join(args))
