'''
Docker interface module
'''
import os
from functools import wraps
from os import path

import six
from docker import APIClient, errors

from .graph.artifacts import Dockerfile
from .graph.nodes import Container, Root, Volume
from .helper import Logger

_cli = None


def _get_name(func):
    @wraps(func)
    def func_wrapper(*args, **kwds):
        if isinstance(args[0], six.string_types):
            return func(*args, **kwds)
        else:
            assert isinstance(args[0], (Container, Volume))
            return func(args[0].full_name, *args[1:], **kwds)
    return func_wrapper


def _inject_docker_cli(func):
    @wraps(func)
    def func_wrapper(*args, **kwds):
        global _cli
        if _cli is None:
            _cli = APIClient(base_url=os.environ.get('DOCKER_HOST'))
        return func(_cli, *args, **kwds)
    return func_wrapper


def _get_tmp_dir(node):
    assert isinstance(node, Root)
    return path.join(node.tpl.tmp_dir, node.name)


@_inject_docker_cli
def create_container(_cli,
                     con,
                     cmd=None,
                     entrypoint=None,
                     from_saved=False,
                     force=False):
    _log = Logger.get(__name__)

    def create():
        tmp_dir = _get_tmp_dir(con)
        try:
            os.makedirs(tmp_dir)
        except Exception:
            pass
        img_name = con.image.format
        _log.debug('image_name: %s', img_name)

        if from_saved:
            saved_image = get_saved_image(con)
            if inspect_image(saved_image):
                img_name = saved_image

        con.id = _cli.create_container(
            name=con.full_name,
            image=img_name,
            user='root',
            entrypoint=entrypoint,
            command=cmd if cmd else con.cmd,
            environment=con.env,
            detach=True,
            # stdin_open=True,
            ports=[key for key in con.ports.keys()]
            if con.ports else None,
            volumes=['/tmp/dt'] + [k for k, v in con.volume] +\
                    [k for k in con.share_data.keys()],
            networking_config=_cli.create_networking_config({
                _get_app_name(con): _cli.create_endpoint_config(
                    links=con.connection
                )}),
            host_config=_cli.create_host_config(
                port_bindings=con.ports,
                binds=[tmp_dir + ':/tmp/dt'] +\
                      [v + ':' + k for k, v in con.volume] +\
                      ['{}:{}'.format(v, k) for k, v in con.share_data.items()],
            )
        ).get('Id')

    assert isinstance(con, Container)

    if isinstance(con.image, Dockerfile):
        _log.debug('start building..')
        build_image(con)
        _log.debug('stop building..')
    elif not from_saved:
        _log.debug('start pulling.. %s', con.image)
        # helper.print_json(
        _cli.pull(con.image.format)
        # , _log.debug)
        _log.debug('end pulling..')

    try:
        create()
    except errors.APIError as e:
        if force:
            delete_container(con)
            create()
        else:
            _log.debug(e)
            raise e


# @_inject_docker_cli
# def pull_image(_cli, image):
#     assert isinstance(image, six.string_types)
#     _cli.pull(image)

@_get_name
@_inject_docker_cli
def stop_container(_cli, name):
    _log = Logger.get(__name__)
    try:
        _cli.stop(name)
    except errors.NotFound as e:
        _log.error(e)
        raise e


@_get_name
@_inject_docker_cli
def start_container(_cli, name, wait=False):
    _log = Logger.get(__name__)
    try:
        _cli.start(name)
        if wait:
            _log.debug('wait container..')
            _cli.wait(name)
            # helper.print_byte(
            #     _cli.logs(name, stream=True),
            #     _log.debug
            # )
            _log.debug('end wait container..')
    except errors.NotFound as e:
        _log.error(e)
        raise e


@_get_name
@_inject_docker_cli
def delete_container(_cli, name, force=False):
    _log = Logger.get(__name__)
    try:
        _cli.remove_container(name, v=True, force=force)
    except (errors.NotFound, errors.APIError) as e:
        _log.error(e)
        raise e


@_get_name
@_inject_docker_cli
def exec_cmd(_cli, name, cmd):
    _log = Logger.get(__name__)
    if not is_running(name):
        raise Exception('{} is not running'.format(name))
    try:
        exec_id = _cli.exec_create(name, cmd,
                                   stdout=False,
                                   stderr=False)
        status = _cli.exec_start(exec_id)
        _log.debug(status)

        check = 'rpc error:' != status[:10].decode("utf-8")
        _log.debug('check: %s', check)
        if not check:
            raise errors.APIError
    except errors.APIError as e:
        _log.error(e)
        raise e


@_inject_docker_cli
def build_image(_cli, node):
    assert isinstance(node, Container)
    # helper.print_json(
    return _cli.build(
        path='/'.join(node.image.dockerfile.split('/')[0:-1]),
        dockerfile='./' + node.image.dockerfile.split('/')[-1],
        tag=node.image.name,
        pull=True,
        quiet=True
    )
    # )


@_inject_docker_cli
def create_volume(_cli, volume):
    assert isinstance(volume, Volume)
    _log = Logger.get(__name__)
    _log.debug('volume opt: %s', volume.get_all_opt())
    return _cli.create_volume(
        volume.full_name, 'local', volume.get_all_opt()
    )


@_get_name
@_inject_docker_cli
def delete_volume(_cli, name):
    return _cli.remove_volume(name)


@_inject_docker_cli
def get_containers(_cli, all=False):
    return _cli.containers(all=all)


@_inject_docker_cli
def get_volumes(_cli):
    volumes = _cli.volumes()
    return volumes['Volumes'] or []

@_inject_docker_cli
def get_images(_cli, name=None):
    return _cli.images(name=name)

def inspect(item):
    return (inspect_image(item) or
            inspect_container(item) or
            inspect_volume(item))


@_inject_docker_cli
def inspect_image(_cli, name):
    assert isinstance(name, six.string_types)
    try:
        return _cli.inspect_image(name)
    except errors.NotFound:
        return None


@_get_name
@_inject_docker_cli
def inspect_container(_cli, name):
    try:
        return _cli.inspect_container(name)
    except errors.NotFound:
        return None


@_get_name
@_inject_docker_cli
def inspect_volume(_cli, name):
    try:
        return _cli.inspect_volume(name)
    except errors.NotFound:
        return None


def remove_all_containers():
    for c in get_containers(all=True):
        stop_container(c['Id'])
        delete_container(c['Id'])


def remove_all_volumes():
    for v in get_volumes():
        delete_volume(v['Name'])


@_inject_docker_cli
def create_network(_cli, name, subnet='172.25.0.0/16'):
    _log = Logger.get(__name__)
    # docker network create -d bridge --subnet 172.25.0.0/16 isolated_nw
    # self.delete_network(name)
    try:
        _cli.create_network(name=_get_app_name(name),
                            driver='bridge',
                            ipam={'subnet': subnet},
                            check_duplicate=True)
    except errors.APIError:
        _log.debug('network already exists!')


@_inject_docker_cli
def delete_network(_cli, name):
    _log = Logger.get(__name__)
    try:
        _cli.remove_network(_get_app_name(name))
    except errors.APIError:
        _log.debug('network not exists!')


@_inject_docker_cli
def delete_image(_cli, name):
    assert isinstance(name, six.string_types)
    try:
        _cli.remove_image(name)
    except errors.NotFound:
        pass


@_inject_docker_cli
def update_container(_cli, node, cmd):
    assert isinstance(node, Container)
    stat = inspect_image(node.image.format)
    old_cmd = stat['Config']['Cmd'] or None
    old_entry = stat['Config']['Entrypoint'] or None

    # if is_running(node):
    #     stop_container(node)
    #     delete_container(node)

    create_container(node,
                     cmd=cmd,
                     entrypoint='',
                     from_saved=True,
                     force=True)

    start_container(node.id, wait=True)
    # stop_container(node.id)

    _cli.commit(node.id, get_saved_image(node))

    # stop_container(node)
    # delete_container(node)
    create_container(node,
                     cmd=node.cmd or old_cmd,
                     entrypoint=old_entry,
                     from_saved=True,
                     force=True)

    _cli.commit(node.id, get_saved_image(node))


def is_running(container):
    _log = Logger.get(__name__)
    stat = inspect_container(container)
    stat = stat is not None and stat['State']['Running'] is True
    _log.debug('State: %s', stat)
    return stat


def get_saved_image(node):
    assert isinstance(node, Container)
    return '{}/{}'.format(_get_app_name(node), node.name.lower())


def _get_app_name(node):
    assert isinstance(node, (six.string_types, Container))
    if isinstance(node, Container):
        node = node.tpl.name
    return 'tosker_{}'.format(node.lower())


# @property
# def tmp_dir(self):
#     return self._tmp_dir
