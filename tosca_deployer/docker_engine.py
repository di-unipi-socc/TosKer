import os
from docker import Client, errors
from io import BytesIO
from . import utility
from .utility import Logger


class Docker_engine:

    def __init__(self, socket='unix://var/run/docker.sock'):
        self.log = Logger.get(__name__)
        self._cli = Client(base_url=socket)

    def create(self, conf, net_name):
        # create docker image
        def create_container():
            # TODO: why is this here?
            os.makedirs('/tmp/docker_tosca/' + conf.name, exist_ok=True)

            # if forse_up:
            #     img = self._cli.inspect_image(conf.image)
            #     if img["Config"]["Entrypoint"] is not None:
            #         entrypoint = img["Config"]["Entrypoint"]
            #     else:
            #         entrypoint = []
            #
            #     if conf.cmd is not None:
            #         cmd = [conf.cmd]
            #     elif img["Config"]["Cmd"] is not None:
            #         cmd = img["Config"]["Cmd"]
            #     else:
            #         cmd = []
            #
            #     cmd = '"{} && sh -c \\"while true; do sleep 2; done\\""'.format(
            #         ' '.join(entrypoint + cmd))
            #
            #     entrypoint = 'sh -c'
            #
            #     self.log.debug('entrypoint: {}'.format(img["Config"]["Entrypoint"]))
            #     self.log.debug('cmd: {}'.format(img["Config"]["Cmd"]))
            # else:
            #     entrypoint = None
            #     cmd = conf.cmd
            # self.log.debug('entrypoint: {}'.format(entrypoint))
            # self.log.debug('cmd: {}'.format(cmd))

            return self._cli.create_container(
                name=conf.name,
                image=conf.image,
                # entrypoint=entrypoint,
                command=conf.cmd,
                environment=conf.env,
                detach=True,
                # stdin_open=True,
                ports=[key for key in conf.ports.keys()]
                if conf.ports else None,
                volumes=['/tmp/dt'] + ([k for k, v in conf.volume.items()]
                                       if conf.volume else []),
                networking_config=self._cli.create_networking_config({
                    net_name: self._cli.create_endpoint_config(
                        links=conf.link
                    )}),
                host_config=self._cli.create_host_config(
                    port_bindings=conf.ports,
                    # links=conf.link,
                    binds=['/tmp/docker_tosca/'+conf.name+':/tmp/dt'] +
                    ([v+':'+k for k, v in conf.volume.items()]
                     if conf.volume else []),
                )
            )

        container = None
        try:
            if conf.to_build():
                # with open(conf['dockerfile']) as f:
                #     byte = BytesIO(f.read().encode('utf-8'))
                # print ('DEBUG:', conf.dockerfile)
                # print ('DEBUG:', '/'.join(conf.dockerfile.split('/')[0:-1]))
                # print ('DEBUG:', './' + conf.dockerfile.split('/')[-1])
                self._cli.build(
                    path='/'.join(conf.dockerfile.split('/')[0:-1]),
                    dockerfile='./' + conf.dockerfile.split('/')[-1],
                    tag=conf.image, stream=True
                )
            else:
                self._cli.pull(conf.image, stream=True)
            container = create_container()
        except errors.APIError:
            self.stop(conf.name)
            self.delete(conf.name)
            container = create_container()

        return container.get('Id')

    def stop(self, name):
        try:
            return self._cli.stop(name)
        except errors.NotFound as e:
            self.log.error(e)

    def start(self, name):
        return self._cli.start(name)

    def delete(self, name):
        try:
            return self._cli.remove_container(name, v=True)
        except errors.NotFound as e:
            self.log.error(e)

    def container_exec(self, name, cmd):
        # print ('DEBUG:', 'name', name, 'cmd', cmd)
        exec_id = self._cli.exec_create(name, cmd)
        return self._cli.exec_start(exec_id, stream=True)

    def create_volume(self, conf):
        self.log.debug('volume opt: {}'.format(conf.get_all_opt()))
        return self._cli.create_volume(conf.name, conf.driver, conf.get_all_opt())

    def delete_volume(self, name):
        return self._cli.remove_volume(name)

    def get_container(self, all=False):
        return self._cli.containers(all=all)

    def get_volumes(self):
        volumes = self._cli.volumes()
        return volumes['Volumes'] or []

    def container_inspect(self, name):
        try:
            return self._cli.inspect_container(name)
        except errors.NotFound:
            return None

    def volume_inspect(self, name):
        try:
            return self._cli.inspect_volume(name)
        except errors.NotFound:
            return None

    def remove_all_containers(self):
        for c in self.get_container(all=True):
            self.stop(c['Id'])
            self.delete(c['Id'])

    def remove_all_volumes(self):
        for v in self.get_volumes():
            self.delete_volume(v['Name'])

    def create_network(self, name, subnet='172.25.0.0/16'):
        # docker network create -d bridge --subnet 172.25.0.0/16 isolated_nw
        self.delete_network(name)
        self._cli.create_network(name=name,
                                driver='bridge',
                                ipam={'subnet': subnet})

    def delete_network(self, name):
        try:
            self._cli.remove_network(name)
        except errors.APIError:
            pass

    def connect_to_network(self, c, n, links):
        self._cli.connect_container_to_network(c, n, links=links)

    def wait(self, container):
        self._cli.wait(container)
