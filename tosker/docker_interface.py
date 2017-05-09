import os
from os import path

import requests.exceptions
import six
from functools import wraps
from docker import APIClient, errors

from . import helper
from .graph.nodes import Container, Volume
from .graph.artifacts import Dockerfile
from .helper import Logger


def _get_name(func):
    @wraps(func)
    def func_wrapper(self, *args, **kwds):
        if isinstance(args[0], six.string_types):
            return func(self, *args, **kwds)
        else:
            assert isinstance(args[0], (Container, Volume))
            return func(self, args[0].name, *args[1:], **kwds)
    return func_wrapper


class Docker_interface:

    def __init__(self,
                 repo=None,
                 net_name=None,
                 tmp_dir=None,
                 socket='unix://var/run/docker.sock'):
        self._log = Logger.get(__name__)
        self._repo = repo.lower() if repo is not None else None
        self._net_name = net_name
        self._tmp_dir = tmp_dir
        self._cli = APIClient(base_url=os.environ.get('DOCKER_HOST') or socket)

    def create_container(self,
                         con,
                         cmd=None,
                         entrypoint=None,
                         from_saved=False,
                         force=False):
        def create():
            tmp_dir = path.join(self._tmp_dir, con.name)
            try:
                os.makedirs(tmp_dir)
            except Exception:
                pass
            img_name = con.image.format
            self._log.debug('image_name: {}'.format(img_name))

            if from_saved:
                saved_image = self.get_saved_image(con)
                if self.inspect_image(saved_image):
                    img_name = saved_image

            self._log.debug('container: {}'.format(con.get_str_obj()))

            con.id = self._cli.create_container(
                name=con.name,
                image=img_name,
                entrypoint=entrypoint,
                command=cmd if cmd else con.cmd,
                environment=con.env,
                detach=True,
                # stdin_open=True,
                ports=[key for key in con.ports.keys()]
                if con.ports else None,
                volumes=['/tmp/dt'] + ([k for k, v in con.volume]),
                networking_config=self._cli.create_networking_config({
                    self._net_name: self._cli.create_endpoint_config(
                        links=con.connection
                    )}),
                host_config=self._cli.create_host_config(
                    port_bindings=con.ports,
                    binds=[tmp_dir + ':/tmp/dt'] +
                    ([v + ':' + k for k, v in con.volume]),
                )
            ).get('Id')

        assert isinstance(con, Container)

        if isinstance(con.image, Dockerfile):
            self._log.debug('start building..')
            self.build_image(con)
            self._log.debug('stop building..')
        elif not from_saved:
            self._log.debug('start pulling.. {}'.format(con.image))
            # helper.print_json(
            self._cli.pull(con.image.format)
            # , self._log.debug)
            self._log.debug('end pulling..')

        try:
            create()
        except errors.APIError as e:
            self._log.debug(e)
            if force:
                self.delete_container(con)
                create()
            else:
                raise e

    # def pull_image(self, image):
    #     assert isinstance(image, six.string_types)
    #     self._cli.pull(image)

    @_get_name
    def stop_container(self, name):
        try:
            self._cli.stop(name)
        except errors.NotFound as e:
            self._log.error(e)
            raise e

    @_get_name
    def start_container(self, name, wait=False):
        try:
            self._cli.start(name)
            if wait:
                self._log.debug('wait container..')
                self._cli.wait(name)
                helper.print_byte(
                    self._cli.logs(name, stream=True),
                    self._log.debug
                )
        except errors.NotFound as e:
            self._log.error(e)
            raise e

    @_get_name
    def delete_container(self, name):
        try:
            self._cli.remove_container(name, v=True)
        except (errors.NotFound, errors.APIError) as e:
            self._log.error(e)
            raise e

    @_get_name
    def exec_cmd(self, name, cmd):
        if not self.is_running(name):
            raise e
        try:
            exec_id = self._cli.exec_create(name, cmd,
                                            stdout=False,
                                            stderr=False)
            status = self._cli.exec_start(exec_id)
            self._log.debug(status)

            check = 'rpc error:' != status[:10].decode("utf-8")
            self._log.debug('check: {}'.format(check))
            if not check:
                raise errors.APIError
        except errors.APIError as e:
            self._log.error(e)
            raise e

    def create_volume(self, volume):
        assert isinstance(volume, Volume)
        self._log.debug('volume opt: {}'.format(volume.get_all_opt()))
        return self._cli.create_volume(
            volume.name, 'local', volume.get_all_opt()
        )

    @_get_name
    def delete_volume(self, name):
        return self._cli.remove_volume(name)

    def get_containers(self, all=False):
        return self._cli.containers(all=all)

    def get_volumes(self):
        volumes = self._cli.volumes()
        return volumes['Volumes'] or []

    def inspect(self, item):
        return (self.inspect_image(item) or
                self.inspect_container(item) or
                self.inspect_volume(item))

    def inspect_image(self, name):
        assert isinstance(name, six.string_types)
        try:
            return self._cli.inspect_image(name)
        except errors.NotFound:
            return None

    @_get_name
    def inspect_container(self, name):
        try:
            return self._cli.inspect_container(name)
        except errors.NotFound:
            return None

    @_get_name
    def inspect_volume(self, name):
        try:
            return self._cli.inspect_volume(name)
        except errors.NotFound:
            return None

    def remove_all_containers(self):
        for c in self.get_containers(all=True):
            self.stop_container(c['Id'])
            self.delete_container(c['Id'])

    def remove_all_volumes(self):
        for v in self.get_volumes():
            self.delete_volume(v['Name'])

    def create_network(self, name='', subnet='172.25.0.0/16'):
        # docker network create -d bridge --subnet 172.25.0.0/16 isolated_nw
        # self.delete_network(name)
        try:
            self._cli.create_network(name=name or self._net_name,
                                     driver='bridge',
                                     ipam={'subnet': subnet},
                                     check_duplicate=True)
        except errors.APIError:
            self._log.debug('network already exists!')

    def delete_network(self, name=''):
        assert isinstance(name, six.string_types)
        try:
            self._cli.remove_network(name or self._net_name)
        except errors.APIError:
            self._log.debug('network not exists!')

    def delete_image(self, name):
        assert isinstance(name, six.string_types)
        try:
            self._cli.remove_image(name)
        except errors.NotFound:
            pass

    def update_container(self, node, cmd):
        assert isinstance(node, Container)
        stat = self.inspect_image(node.image.format)
        old_cmd = stat['Config']['Cmd'] or None
        old_entry = stat['Config']['Entrypoint'] or None

        # if self.is_running(node):
        #     self.stop_container(node)
        #     self.delete_container(node)

        self.create_container(node,
                              cmd=cmd,
                              entrypoint='',
                              from_saved=True,
                              force=True)

        self.start_container(node.id, wait=True)
        # self.stop_container(node.id)

        self._cli.commit(node.id, self.get_saved_image(node))

        # self.stop_container(node)
        # self.delete_container(node)
        self.create_container(node,
                              cmd=node.cmd or old_cmd,
                              entrypoint=old_entry,
                              from_saved=True,
                              force=True)

        self._cli.commit(node.id, self.get_saved_image(node))

    def is_running(self, container):
        stat = self.inspect_container(container)
        stat = stat is not None and stat['State']['Running'] is True
        self._log.debug('State: {}'.format(stat))
        return stat

    @_get_name
    def get_saved_image(self, name):
        return '{}/{}'.format(self._repo, name.lower())

    def build_image(self, node):
        assert isinstance(node, Container)
        # helper.print_json(
        return self._cli.build(
            path='/'.join(node.image.dockerfile.split('/')[0:-1]),
            dockerfile='./' + node.image.dockerfile.split('/')[-1],
            tag=node.image.name,
            pull=True,
            quiet=True
        )
        # )

    @property
    def tmp_dir(self):
        return self._tmp_dir
