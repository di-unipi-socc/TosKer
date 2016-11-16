import json
import re
from os import path

import toscaparser
from toscaparser.tosca_template import ToscaTemplate

from . import utility
from .nodes import Container, Software, Volume
from .template import Template

log = utility.Logger.get(__name__)


def _check_requirements(node, running):
    for req in node.requirements:
        for key, value in req.items():
            value = value['node'] if type(value) is dict else value
            if value not in running:
                return False
    return True

#
# def _parse_function(value):
#     if type(value) is dict:
#         key, args = list(value.items())[0]
#
#         if key == 'get_property':
#             def f(tpl, node):
#                 if args[0] == 'SELF':
#                     return utility.get_attributes(args[1:], node)
#                 else:
#                     return utility.get_attributes(args[1:], tpl[args[0]])
#             return f
#         elif key == 'get_artifact':
#             def f(tpl, node):
#                 if args[0] == 'SELF':
#                     return node.artifacts[args[1]]
#                 else:
#                     return tpl[args[0]].artifacts[args[1]]
#             return f
#         elif key == 'get_input':
#             return tpl.inputs[args[0]]
#     else:
#         return value


def _parse_path(base_path, value):
    abs_path = path.abspath(
        path.join(base_path, value)
    )
    split_path = abs_path.split('/')
    return {'path': '/'.join(split_path[:-1]),
            'file': split_path[-1],
            'file_path': abs_path}


def _parse_conf(node, inputs, repos, file_path):
    conf = None

    base_path = '/'.join(file_path.split('/')[:-1]) + '/'

    # TODO: accept also derived type
    if node.type == 'tosker.docker.container':
        conf = Container(node.name)

        def parse_dockerfile(image, dockerfile):
            conf.image = image
            conf.dockerfile = dockerfile

        def parse_pull_image(img_name, repo_url=None):
            conf.image = img_name
            if repo_url:
                p = re.compile('(https://|http://)')
                repo = p.sub('', repos[repo_url]).strip('/')
                if repo != 'registry.hub.docker.com':
                    conf.image = '/'.join([repo.strip('/'),
                                           conf.image.strip('/')])

        # get artifacts
        artifacts = node.entity_tpl['artifacts']
        for key, value in artifacts.items():
            if type(value) is dict:
                if value['type'] == \
                   'tosca.artifacts.Deployment.Image.Container.Docker':
                    parse_pull_image(
                        value['file'], value.get('repository', None))
                else:
                    parse_dockerfile(key, path.abspath(
                        path.join(base_path, value['file'])))
            else:
                docker_dir = path.abspath(
                    path.join(base_path, value)).strip('/Dockerfile')
                if path.exists(docker_dir):
                    parse_dockerfile(key, docker_dir)
                else:
                    parse_pull_image(value)

        def _parse_map(m):
            res = {}
            for key, value in m.items():
                # if type(value) is dict and 'get_input' in value:
                #     res[key] = tpl.inputs[value['get_input']]
                # else:
                #     res[key] = value
                res[key] = value
            return res

        # get properties
        if 'properties' in node.entity_tpl:
            if 'env_variable' in node.entity_tpl['properties']:
                values = node.entity_tpl['properties']['env_variable']
                conf.env = _parse_map(values)

            if 'cmd' in node.entity_tpl['properties']:
                conf.cmd = node.entity_tpl['properties']['cmd']

            if 'ports' in node.entity_tpl['properties']:
                values = node.entity_tpl['properties']['ports']
                conf.ports = _parse_map(values)

    elif node.type == 'tosker.docker.volume':
        conf = Volume(node.name)
        if 'properties' in node.entity_tpl:
            properties = node.entity_tpl['properties']
            conf.driver = properties.get('driver', None)
            conf.type = properties.get('type', None)
            conf.device = properties.get('device', None)
            conf.driver_opt = properties.get('driver_opt', None)
    elif node.type == 'tosker.software':
        conf = Software(node.name)
        if 'artifacts' in node.entity_tpl:
            artifacts = node.entity_tpl['artifacts']
            for key, value in artifacts.items():
                log.debug('artifacts: {}'.format(value))
                conf.add_artifact(key, _parse_path(base_path, value))
                log.debug('artifacts: {}'.format(conf.artifacts))

        # get interfaces
        # try:
        if 'interfaces' in node.entity_tpl and \
                'Standard' in node.entity_tpl['interfaces']:
            # TODO: implimement all the standard cycle
            interfaces = node.entity_tpl['interfaces']['Standard']
            intf = {}
            for key, value in interfaces.items():
                intf[key] = {}
                if 'implementation' in value:
                    abs_path = path.abspath(
                        path.join(base_path, value['implementation'])
                    )
                    path_split = abs_path.split('/')
                    intf[key]['cmd'] = {
                        'file': path_split[-1],
                        'path': '/'.join(path_split[:-1]),
                        'file_path': abs_path
                    }
                    log.debug('path: {} file: {}'.format(intf[key]['cmd']['path'],
                                                         intf[key]['cmd']['file']))
                if 'inputs' in value:
                    intf[key]['inputs'] = value['inputs']
                    # intf[key]['inputs'] = _parse_map(value['inputs'])

            conf.interfaces = intf

        # except:
        #     print ('error:')
    else:
        log.error('node type "{}" not supported!'.format(node.type))
        # TODO: collect error like a real parser..

    def add_to_list(l, value):
        if l is None:
            l = []
        l.append(value)
        return l

    # get requirements
    if 'requirements' in node.entity_tpl:
        requirements = node.entity_tpl['requirements']
        for value in requirements:
            if 'link' in value:
                conf.add_link((value['link'], value['link']))
            # if 'connectTo' in value:
            #     conf.add_link(value['connectTo'])
            if 'host' in value:
                # log.debug('here ' + str(value))
                conf.host = value['host']
            if 'volume' in value:
                volume = value['volume']
                if type(volume) is dict:
                    conf.add_volume(volume['relationship']['properties'][
                                    'location'], volume['node'])
    return conf


def parse_TOSCA(file_path, inputs):
    tosca = ToscaTemplate(file_path, inputs, True)
    base_path = '/'.join(file_path.split('/')[:-1]) + '/'

    _parse_functions(tosca, inputs, base_path)
    # print(utility.print_TOSCA(tosca))

    tpl = Template(tosca.input_path.split('/')[-1][:-5])

    if hasattr(tosca, 'nodetemplates'):
        if tosca.outputs:
            tpl.outputs = tosca.outputs
        if tosca.nodetemplates:
            running_container = set()
            nodes = tosca.nodetemplates
            i = 0
            while len(running_container) < len(nodes):
                if i >= len(nodes):
                    i = 0
                node = nodes[i]
                if node.name in running_container:
                    i += 1
                    continue

                if not _check_requirements(node, running_container):
                    i += 1
                    continue

                tpl_node = _parse_conf(node, inputs, tosca.tpl.get(
                    'repositories', None), file_path)
                tpl.push(tpl_node)
                running_container.add(node.name)

    _post_computation(tpl)
    return tpl


# - add pointer host_container pointer on software
# - add pointer on host property
# - add software links to the corrisponding container
# - pack together installation scripts
def _post_computation(tpl):
    for node in tpl.software_order:
        if type(node.host) is str:
            node.host = tpl[node.host]

    # add property host_container
    for node in tpl.software_order:
        if type(node.host) is Container:
            node.host_container = node.host
        elif type(node.host) is Software:
            node.host_container = node.host.host_container

    # manage the case when a software node is connected to a software node or a container
    for node in tpl.software_order:
        if node.link is not None:
            for link in node.link:
                link = link[0]
                if type(tpl[link]) is Container:
                    container_name = tpl[link].name
                else:
                    container_name = tpl[link].host_container.name
                log.debug('link: {}'.format((container_name, link)))
                node.host_container.add_link((container_name, link))

    # manage the case when the container is connected to a softeware node
    for node in tpl.container_order:
        log.debug(node)
        if node.link is not None:
            for i, link in enumerate(node.link):
                link = link[0]
                if type(tpl[link]) is Software:
                    container_name = tpl[link].host_container.name
                    log.debug('link: {}'.format((container_name, link)))
                    node.link[i] = (container_name, link)

    # TODO: si puo togliere, visto che per ora non viene utilizzato!
    # for node in tpl.software_order:
    #     node.host_container.software_layer.append(node)


def _parse_functions(tosca, inputs, base_path):
    tpl = tosca.topology_template.tpl['node_templates']
    if 'inputs' in tosca.topology_template.tpl:
        tosca_inputs = tosca.topology_template.tpl['inputs']

    if 'outputs' in tosca.topology_template.tpl:
        pass
        # for k, v in tosca.topology_template.tpl['outputs'].items():
            # print(type(v['value']))
            # print(dir(v['value']))
            # print(dir(v['value'].result().result()))

            # print(v.result())

    def _parse_node(name, node):
        for k, v in node.items():
            if type(v) is dict:
                if 'get_property' in v:
                    node[k] = _get(name, 'properties', v['get_property'])
                elif 'get_artifact' in v:
                    node[k] = _parse_path(base_path, _get(
                        name, 'artifacts', v['get_artifact']))
                elif 'get_input' in v:
                    if v['get_input'] in inputs:
                        node[k] = inputs[v['get_input']]
                    else:
                        node[k] = tosca_inputs[v['get_input']]['default']
                else:
                    _parse_node(name, v)
            elif type(v) is toscaparser.functions.GetProperty:
                node[k] = v.result()

    def _get(name, value, args):
        if 'SELF' == args[0]:
            args[0] = name
        return utility.get_attributes(args[1:], tpl[args[0]][value])

    for k, v in tpl.items():
        _parse_node(k, v)
