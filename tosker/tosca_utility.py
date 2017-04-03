import json
import re
import random  # TODO: remove this
from os import path

import toscaparser
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.prereq.csar import CSAR
from toscaparser.common.exception import ValidationError

from . import helper
from .graph.nodes import Container, Software, Volume
from .graph.template import Template


_log = None

# CUSTOM TYPE
PERSISTENT_CONTAINER = 'tosker.nodes.Container.Executable'
VOLATILE_CONTAINER = 'tosker.nodes.Container'
VOLUME = 'tosker.nodes.Volume'
SOFTWARE = 'tosker.nodes.Software'
IMAGE1 = 'tosker.artifacts.Image'
IMAGE2 = 'tosca.artifacts.Deployment.Image.Container.Docker'
DOCKERFILE1 = 'tosker.artifacts.Dockerfile'
DOCKERFILE2 = 'tosca.artifacts.File'

# REQUIREMENTS
CONNECT = 'connection'
DEPEND = 'dependency'
ATTACH = 'storage'
HOST = 'host'


def _check_requirements(node, running):
    for req in node.requirements:
        for key, value in req.items():
            value = value['node'] if type(value) is dict else value
            if value not in running:
                return False
    return True


def _parse_path(base_path, value):
    abs_path = path.abspath(
        path.join(base_path, value)
    )
    split_path = abs_path.split('/')
    return {'path': '/'.join(split_path[:-1]),
            'file': split_path[-1],
            'file_path': abs_path}


def _parse_conf(node, inputs, repos, base_path):
    conf = None

    if node.type == PERSISTENT_CONTAINER or node.type == VOLATILE_CONTAINER:
        conf = Container(node.name)
        conf.persistent = node.type == PERSISTENT_CONTAINER

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
                if value['type'] == IMAGE1 or value['type'] == IMAGE2:
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

            if 'command' in node.entity_tpl['properties']:
                conf.cmd = node.entity_tpl['properties']['command']

            if 'ports' in node.entity_tpl['properties']:
                values = node.entity_tpl['properties']['ports']
                conf.ports = _parse_map(values)

    elif node.type == VOLUME:
        conf = Volume(node.name)
        if 'properties' in node.entity_tpl:
            properties = node.entity_tpl['properties']
            conf.driver = properties.get('driver', None)
            conf.type = properties.get('type', None)
            conf.device = properties.get('device', None)
            conf.size = properties.get('size', None)
            conf.driver_opt = properties.get('driver_opt', None)

    elif node.type == SOFTWARE:
        conf = Software(node.name)
        if 'artifacts' in node.entity_tpl:
            artifacts = node.entity_tpl['artifacts']
            for key, value in artifacts.items():
                _log.debug('artifacts: {}'.format(value))
                conf.add_artifact(key, _parse_path(base_path, value))
                _log.debug('artifacts: {}'.format(conf.artifacts))

        # get interfaces
        if 'interfaces' in node.entity_tpl and \
                'Standard' in node.entity_tpl['interfaces']:
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
                    _log.debug('path: {} file: {}'
                               .format(intf[key]['cmd']['path'],
                                       intf[key]['cmd']['file']))
                if 'inputs' in value:
                    intf[key]['inputs'] = value['inputs']
                    # intf[key]['inputs'] = _parse_map(value['inputs'])

            conf.interfaces = intf

    else:
        _log.error('node type "{}" not supported!'.format(node.type))
        # TODO: collect error like as real parser..

    def add_to_list(l, value):
        if l is None:
            l = []
        l.append(value)
        return l

    # get requirements
    if 'requirements' in node.entity_tpl:
        requirements = node.entity_tpl['requirements']
        for value in requirements:
            if CONNECT in value:
                conf.add_connection(value[CONNECT])
            if DEPEND in value:
                conf.add_depend(value[DEPEND])
            if HOST in value:
                conf.host = value[HOST]
            if ATTACH in value:
                volume = value[ATTACH]
                if type(volume) is dict:
                    conf.add_volume(volume['node'], volume['relationship']
                                                          ['properties']
                                                          ['location'])
    return conf


# def filter_components(tpl, components):
#     if all(tpl[i] is not None for i in components):
#         res = Template(tpl.name)
#         for c in reversed(tpl.deploy_order):
#             # print(c)
#             if c.name in components:
#                 _filter_components_rec(tpl, c, res)
#         return res
#
#
# def _filter_components_rec(tpl, c, new):
#     if c not in new:
#         if hasattr(c, 'volume') and c.volume is not None:
#             # new.push(c.volume)
#             for v in c.volume.values():
#                 _filter_components_rec(tpl, v, new)
#         if hasattr(c, 'connection') and c.connection is not None:
#             for con in c.connection:
#                 _filter_components_rec(tpl, con, new)
#         if hasattr(c, 'depend') and c.depend is not None:
#             # new.push(c.depend)
#             for dep in c.depend:
#                 _filter_components_rec(tpl, dep, new)
#         if hasattr(c, 'host') and c.host is not None:
#             # new.push(c.host)
#             _filter_components_rec(tpl, c.host, new)
#         new.push(c)


def get_tosca_template(file_path, inputs={}, components=[]):
    global _log
    _log = helper.Logger.get(__name__)

    # Work around bug validation csar of toscaparser
    if file_path.endswith(('.zip', '.csar')):
        csar = CSAR(file_path)
        try:
            csar.validate()
        except ValueError as e:
            _log.debug(e)
            if not str(e).startswith("The resource") or \
               not str(e).endswith("does not exist."):
                raise e

        csar.decompress()
        file_path = path.join(csar.temp_dir, csar.get_main_template())

    tosca = ToscaTemplate(file_path, inputs)

    base_path = '/'.join(tosca.path.split('/')[:-1]) + '/'
    _log.debug('base_path: {}'.format(base_path))
    _parse_functions(tosca, inputs, base_path)
    # print(helper.print_TOSCA(tosca))

    repositories = tosca.tpl.get('repositories', None)

    tpl = Template(tosca.input_path.split('/')[-1][:-5])

    if hasattr(tosca, 'nodetemplates'):
        if tosca.outputs:
            tpl.outputs = tosca.outputs
        if tosca.nodetemplates:
            for node in tosca.nodetemplates:
                if len(components) == 0 or node.name in components:
                    tpl.push(_parse_conf(node,
                                         inputs,
                                         repositories,
                                         base_path))
            print('DEBUG', tpl)

            if len(components) > 0:
                for node in _get_dependency_nodes(tpl, tosca):
                    tpl.push(_parse_conf(node,
                                         inputs,
                                         repositories,
                                         base_path))

            _add_pointer(tpl)

            _sort(tpl)
            # while len(nodes) > 0:
            #     for node in nodes:
            #         if node
            #     if i >= len(nodes):
            #         i = 0
            #     node = nodes[i]
            #     if node.name in running_container:
            #         i += 1
            #         continue
            #
            #     if not _check_requirements(node, running_container):
            #         i += 1
            #         continue
            #
            #     tpl_node = _parse_conf(node, inputs, tosca.tpl.get(
            #         'repositories', None), base_path)
            #     tpl.push(tpl_node)
            #     running_container.add(node.name)

            _post_computation(tpl)
    return tpl


def _get_dependency_nodes(tpl, tosca):
    for n in tpl.deploy_order:
        for r in n.relationships:
            if r.to not in tpl:
                tosca_node = next((n for n in tosca.nodetemplates
                                   if n.name == r.to))
                yield tosca_node


def _sort(tpl):
    nodes = list((i.name for i in tpl.deploy_order))
    # TODO: remove this
    random.shuffle(nodes)
    tpl.deploy_order = []
    while len(nodes) > 0:
        n = nodes.pop(0)
        print("DEBUG", n)
        if all((r.to.name not in nodes for r in tpl[n].relationships)):
            print("DEBUG", 'good')
            tpl.deploy_order.append(tpl[n])
        else:
            print("DEBUG", 'put back')
            nodes.append(n)


def _add_pointer(tpl):
    for node in tpl.deploy_order:
        for rel in node.relationships:
            rel.to = tpl[rel.to]


# - add pointer host_container pointer on software
# - add pointer on host property
# - add software links to the corrisponding container
def _post_computation(tpl):
    # Add the host_container property
    for node in tpl.software_order:
        if node.host is not None:
            if isinstance(node.host.to, Container):
                node.host_container = node.host.to
            elif isinstance(node.host.to, Software):
                node.host_container = node.host.host_container

    # Manage the case when a Software is connected
    # to a Container or a Software
    for node in tpl.software_order:
        for con in node._connection:
            if isinstance(con.to, Container):
                container = con.to
            if isinstance(con.to, Software):
                container = con.to.host_container
            node.host_container.add_connection(container, con.to.name)

    # Manage the case whene a Container is connected to a Software
    for node in tpl.container_order:
        for con in node._connection:
                if isinstance(con.to, Software):
                    con.alias = con.to.name
                    con.to = con.to.host_container


# def _parse_functions(tosca, inputs, base_path):
#     # Get the template nodes
#     tpl = tosca.topology_template.tpl['node_templates']
#
#     # Get the inputs of the TOSCA file
#     if 'inputs' in tosca.topology_template.tpl:
#         tosca_inputs = tosca.topology_template.tpl['inputs']
#
#     # Recurvive function searching for TOSCA function in the node
#     def parse_node(name, node):
#
#         # This function return the result of the TOSCA function
#         def execute_function(value, args):
#             if 'SELF' == args[0]:
#                 args[0] = name
#             return helper.get_attributes(args[1:], tpl[args[0]][value])
#
#         for k, v in node.items():
#             # If the function is already parse by toscaparser use the result
#             if isinstance(v, toscaparser.functions.Function):
#                 node[k] = v.result()
#             elif type(v) is dict:
#                 # Found a get_property function
#                 if 'get_property' == v:
#                     node[k] = execute_function('properties', v['get_property'])
#                 # Found a get_artifact function
#                 if 'get_artifact' == v:
#                     art = execute_function('artifacts', v['get_artifact'])
#                     node[k] = _parse_path(base_path, art)
#                 # Found a get_input function
#                 elif 'get_input' == v:
#                     if v['get_input'] in inputs:
#                         node[k] = inputs[v['get_input']]
#                     else:
#                         node[k] = tosca_inputs[v['get_input']]['default']
#                 else:
#                     parse_node(name, v)
#
#     # Scan each component of the application to find TOSCA funcions
#     for k, v in tpl.items():
#         parse_node(k, v)
def _parse_functions(tosca, inputs, base_path):
    tpl = tosca.topology_template.tpl['node_templates']
    if 'inputs' in tosca.topology_template.tpl:
        tosca_inputs = tosca.topology_template.tpl['inputs']

    if 'outputs' in tosca.topology_template.tpl:
        pass

    def parse_node(name, node):
        for k, v in node.items():
            # If the function is already parsed by toscaparser,
            # then use the result
            if isinstance(v, toscaparser.functions.Function):
                node[k] = v.result()
            elif isinstance(v, dict):
                # Found a get_property function
                if 'get_property' in v:
                    node[k] = get(name, 'properties', v['get_property'])
                # Found a get_artifact function
                elif 'get_artifact' in v:
                    art = get(name, 'artifacts', v['get_artifact'])
                    node[k] = _parse_path(base_path, art)
                # Found a get_input function
                elif 'get_input' in v:
                    if v['get_input'] in inputs:
                        node[k] = inputs[v['get_input']]
                    else:
                        node[k] = tosca_inputs[v['get_input']]['default']
                else:
                    parse_node(name, v)

    # This function returns the result of the TOSCA function
    def get(name, value, args):
        if 'SELF' == args[0]:
            args[0] = name
        return helper.get_attributes(args[1:], tpl[args[0]][value])

    for k, v in tpl.items():
        parse_node(k, v)
