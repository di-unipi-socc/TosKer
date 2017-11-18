'''
Tosca parser module
'''
import re
from os import path

import toscaparser
from toscaparser.prereq.csar import CSAR
from toscaparser.tosca_template import ToscaTemplate

from . import helper
from .graph.artifacts import (Dockerfile, DockerfileExecutable, DockerImage,
                              DockerImageExecutable, File)
from .graph.nodes import Container, Software, Volume
from .graph.template import Template
from .helper import Logger

_log = None

# CUSTOM TYPE
# PERSISTENT_CONTAINER = 'tosker.nodes.Container.Executable'
CONTAINER = 'tosker.nodes.Container'
VOLUME = 'tosker.nodes.Volume'
SOFTWARE = 'tosker.nodes.Software'
IMAGE = 'tosker.artifacts.Image'
IMAGE_EXE = 'tosker.artifacts.Image.Service'
DOCKERFILE = 'tosker.artifacts.Dockerfile'
DOCKERFILE_EXE = 'tosker.artifacts.Dockerfile.Service'

# EXECUTABLE_IMAGE = 'tosker.artifacts.ExecutableImage'
# IMAGE2 = 'tosca.artifacts.Deployment.Image.Container.Docker'
# DOCKERFILE2 = 'tosca.artifacts.File'

# REQUIREMENTS
CONNECT = 'connection'
DEPEND = 'dependency'
ATTACH = 'storage'
HOST = 'host'


# def _check_requirements(node, running):
#     for req in node.requirements:
#         for key, value in req.items():
#             value = value['node'] if type(value) is dict else value
#             if value not in running:
#                 return False
#     return True

# def _parse_path(base_path, value):
#     abs_path = path.abspath(
#         path.join(base_path, value)
#     )
#     split_path = abs_path.split('/')
#     return {'path': '/'.join(split_path[:-1]),
#             'file': split_path[-1],
#             'file_path': abs_path}


def _get_file(base_path, name, file):
    abs_path = path.abspath(
        path.join(base_path, file)
    )
    return File(name, abs_path)


def _parse_conf(tpl, node, repos, base_path):
    # TODO: split this method too may branches and to many variable
    def _parse_map(m):
        res = {}
        for key, value in m.items():
            res[key] = value
        return res

    conf = None
    if node.type == CONTAINER:
        conf = Container(node.name)

        def parse_dockerfile(name, file, executable=False):
            # dockerfile = path.abspath(path.join(base_path, art['file']))
            conf.image = DockerfileExecutable(name, file) if executable else\
                         Dockerfile(name, file)

        def parse_image(name, repo, executable=False):
            conf.image = DockerImageExecutable(name) if executable else\
                         DockerImage(name)
            if repo:
                p = re.compile('(https://|http://)')
                repo = p.sub('', repos[repo]).strip('/')
                if repo != 'registry.hub.docker.com':
                    # TODO: test private repository
                    conf.image = '/'.join([repo.strip('/'),
                                           conf.image.format.strip('/')])

        # get artifacts
        artifacts = node.entity_tpl['artifacts']
        for key, value in artifacts.items():
            if isinstance(value, dict):
                name = value['file']
                art_type = value['type']
                repo = value.get('repository', None)

                if art_type == DOCKERFILE or art_type == DOCKERFILE_EXE:
                    dockerfile = path.abspath(path.join(base_path, name))
                    _log.debug('dockerfile: %s', dockerfile)
                    # if path.isfile(dockerfile) and repo is None:
                    _log.debug('Find a Dockerfile')
                    parse_dockerfile(key, dockerfile,  # .strip('/Dockerfile'),
                                     art_type == DOCKERFILE_EXE)
                elif art_type == IMAGE or art_type == IMAGE_EXE:
                    _log.debug('Find an Immage')
                    parse_image(name, repo, art_type == IMAGE_EXE)

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

            if 'share_data' in node.entity_tpl['properties']:
                values = node.entity_tpl['properties']['share_data']
                conf.share_data = _parse_map(values)

    elif node.type == VOLUME:
        conf = Volume(node.name)

    elif node.type == SOFTWARE:
        conf = Software(node.name)
        if 'artifacts' in node.entity_tpl:
            artifacts = node.entity_tpl['artifacts']
            for key, value in artifacts.items():
                _log.debug('artifacts: %s', value)
                conf.add_artifact(_get_file(base_path, key, value))
                # TODO: parse also dictionary artifacts
                _log.debug('artifacts: %s', conf.artifacts)

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
                    # path_split = abs_path.split('/')

                    intf[key]['cmd'] = File(None, abs_path)
                    # {
                    #     'file': path_split[-1],
                    #     'path': '/'.join(path_split[:-1]),
                    #     'file_path': abs_path
                    # }
                    _log.debug('path: %s file: %s', intf[key]['cmd'].path,
                               intf[key]['cmd'].file)
                if 'inputs' in value:
                    intf[key]['inputs'] = value['inputs']
                    # intf[key]['inputs'] = _parse_map(value['inputs'])

            conf.interfaces = intf

    else:
        raise ValueError(
            'node type "{}" not supported!'.format(node.type))

    # get requirements
    if 'requirements' in node.entity_tpl:
        requirements = node.entity_tpl['requirements']
        if requirements is not None:
            for value in requirements:
                if CONNECT in value:
                    conf.add_connection(value[CONNECT])
                if DEPEND in value:
                    conf.add_depend(value[DEPEND])
                if HOST in value:
                    if isinstance(value[HOST], dict):
                        conf.host = value[HOST]['node']
                    else:
                        conf.host = value[HOST]
                if ATTACH in value:
                    volume = value[ATTACH]
                    if isinstance(volume, dict):
                        conf.add_volume(volume['node'], volume['relationship']
                                                              ['properties']
                                                              ['location'])
    conf.tpl = tpl
    return conf


def get_tosca_template(file_path, inputs=None):
    if inputs is None:
        inputs = {}
    global _log
    _log = Logger.get(__name__)

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

    base_path = '/'.join(tosca.path.split('/')[:-1])
    _log.debug('base_path: %s', base_path)
    _parse_functions(tosca, inputs, base_path)
    # print(helper.print_TOSCA(tosca))

    repositories = tosca.tpl.get('repositories', None)

    tosca_name = tosca.input_path.split('/')[-1][:-5]
    tpl = Template(tosca_name)

    if hasattr(tosca, 'nodetemplates'):
        if tosca.outputs:
            tpl.outputs = tosca.outputs
        if tosca.nodetemplates:

            for node in tosca.nodetemplates:
                tpl.push(_parse_conf(tpl, node,
                                     repositories,
                                     base_path))

            _add_pointer(tpl)
            _add_back_links(tpl)
            _add_extension(tpl)

    return tpl


def _add_pointer(tpl):
    for node in tpl.nodes:
        for rel in node.relationships:
            rel.to = tpl[rel.to]


def _add_back_links(tpl):
    for node in tpl.nodes:
        for rel in node.relationships:
            rel.to.up_requirements.append(rel)


# - add pointer host_container pointer on software
# - add pointer on host property
# - add software links to the corrisponding container
def _add_extension(tpl):
    # Add the host_container property
    for node in tpl.software:
        def find_container(node):
            if isinstance(node, Container):
                return node
            elif node.host_container is not None:
                return node.host_container
            elif node.host is None:
                raise ValueError('Software component must have the "host"'
                                'requirements')
            else:
                return find_container(node.host.to)

        node.host_container = find_container(node)
        _log.debug('%s .host %s, .host_container %s', node, node.host.to,
                   node.host_container)

    # Manage the case when a Software is connected
    # to a Container or a Software
    for node in tpl.software:
        for con in node._connection:
            if isinstance(con.to, Container):
                container = con.to
            if isinstance(con.to, Software):
                container = con.to.host_container
            _log.debug('mange connection of %s to %s', node, container)
            node.host_container.add_overlay(container, con.to.name)

    # Manage the case whene a Container is connected to a Software
    for node in tpl.containers:
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
#                     node[k] = execute_function('properties',
#                                                v['get_property'])
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
                    node[k] = _get_file(base_path, None, art)
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

    if 'outputs' in tosca.topology_template.tpl:
        for k, v in tosca.topology_template.tpl['outputs'].items():
            parse_node(k, v)
