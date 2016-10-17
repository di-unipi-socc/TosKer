import os
from docker import Client, errors
from io import BytesIO
from . import utility
from .utility import Logger


class Docker_engine:

    def __init__(self, net_name='tosker_net',
                 socket='unix://var/run/docker.sock'):
        self._log = Logger.get(__name__)
        self._net_name = net_name
        self._cli = Client(base_url=socket)

    def create(self, conf, cmd=None, entrypoint=None, saved_image=False):
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
            #     self._log.debug('entrypoint: {}'.format(img["Config"]["Entrypoint"]))
            #     self._log.debug('cmd: {}'.format(img["Config"]["Cmd"]))
            # else:
            #     entrypoint = None
            #     cmd = conf.cmd
            # self._log.debug('entrypoint: {}'.format(entrypoint))
            # self._log.debug('cmd: {}'.format(cmd))
            saved_img_name = '{}/{}'.format(self._net_name, conf.name)
            img_name = conf.image
            if saved_image and self.image_inspect(saved_img_name):
                img_name = saved_img_name

            self._log.debug('image name: {}'.format(img_name))

            conf.id = self._cli.create_container(
                name=conf.name,
                image=img_name,
                entrypoint=entrypoint if entrypoint else conf.entrypoint,
                command=cmd if cmd else conf.cmd,
                environment=conf.env,
                detach=True,
                # stdin_open=True,
                ports=[key for key in conf.ports.keys()]
                if conf.ports else None,
                volumes=['/tmp/dt'] + ([k for k, v in conf.volume.items()]
                                       if conf.volume else []),
                networking_config=self._cli.create_networking_config({
                    self._net_name: self._cli.create_endpoint_config(
                        links=conf.link,
                        # aliases=['db']
                    )}),
                host_config=self._cli.create_host_config(
                    port_bindings=conf.ports,
                    # links=conf.link,
                    binds=['/tmp/docker_tosca/' + conf.name + ':/tmp/dt'] +
                    ([v + ':' + k for k, v in conf.volume.items()]
                     if conf.volume else []),
                )
            ).get('Id')

        try:
            if conf.to_build:
                self._log.debug('to build!')
                # utility.print_json(
                self._cli.build(
                    path='/'.join(conf.dockerfile.split('/')[0:-1]),
                    dockerfile='./' + conf.dockerfile.split('/')[-1],
                    tag=conf.image, stream=True
                )
                # )
            else:
                # utility.print_json(
                self._cli.pull(conf.image, stream=True)
                # )
            create_container()
        except errors.APIError as e:
            # self._log.debug(e)
            self.stop(conf.name)
            self.delete(conf.name)
            create_container()

    def stop(self, name):
        try:
            return self._cli.stop(name)
        except errors.NotFound as e:
            self._log.error(e)

    def start(self, name, wait=False):
        self._cli.start(name)
        if wait:
            self._log.debug('start waiting!')
            self._cli.wait(name)
            self._log.debug('stop waiting!')
            utility.print_byte(
                self._cli.logs(name, stream=True)
            )

    def delete(self, name):
        try:
            return self._cli.remove_container(name, v=True)
        except errors.NotFound as e:
            self._log.error(e)

    def container_exec(self, name, cmd):
        # print ('DEBUG:', 'name', name, 'cmd', cmd)
        exec_id = self._cli.exec_create(name, cmd)
        # utility.print_byte(
        self._cli.exec_start(exec_id, stream=True)
        # )

    def create_volume(self, conf):
        self._log.debug('volume opt: {}'.format(conf.get_all_opt()))
        return self._cli.create_volume(
            conf.name, conf.driver, conf.get_all_opt()
        )

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

    def image_inspect(self, name):
        try:
            return self._cli.inspect_image(name)
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
        # self.delete_network(name)
        try:
            self._cli.create_network(name=name,
                                     driver='bridge',
                                     ipam={'subnet': subnet},
                                     check_duplicate=True)
        except errors.APIError:
            self._log.info('network already exists!')

    def delete_network(self, name):
        try:
            self._cli.remove_network(name)
        except errors.APIError:
            self._log.info('network not exists!')
            pass

    def delete_image(self, name):
        try:
            self._cli.remove_image(name)
        except errors.NotFound:
            pass

    def connect_to_network(self, c, n, links):
        self._cli.connect_container_to_network(c, n, links=links)

    def update_container(self, node, cmd):
        # self._log.debug('container_conf: {}'.format(node.host_container))
        stat = self.image_inspect(node.image)
        old_cmd = stat['Config']['Cmd'] or ''
        old_entry = stat['Config']['Entrypoint'] or ''

        self.create(node, cmd=cmd, entrypoint='', saved_image=True)
        self.start(node.id, wait=True)
        utility.print_byte(
            self._cli.logs(node.id, stream=True)
        )
        self.stop(node.id)

        name = '{}/{}'.format(self._net_name, node.name)

        # changes = 'CMD {}\nENTRYPOINT {}'.format(
        #     (' '.join(old_cmd) if old_cmd else 'null'),
        #     (' '.join(old_entry) if old_entry else 'null')
        # )
        # self._log.debug('commit changes: {}'.format(changes))
        self._cli.commit(node.id, name)
        self.create(node, cmd=old_cmd, entrypoint=old_entry, saved_image=True,)
        self._cli.commit(node.id, name)

    def is_running(self, name):
        stat = self.container_inspect(name)
        self._log.debug('State.Running: {}'.format(stat['State']['Running']))
        return stat is not None and stat['State']['Running'] is True
