import json
import re
from os import path

import toscaparser
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.prereq.csar import CSAR
from toscaparser.common.exception import ValidationError

from . import helper
from .graph.nodes import Container, Software, Volume
from .graph.artifacts import DockerImage, DockerImageExecutable, File, \
                             Dockerfile, DockerfileExecutable
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


def _parse_conf(node, repos, base_path):
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
                    dockerfile = path.abspath(
                                    path.join(base_path, name)
                                 )
                    _log.debug('dockerfile: {}'.format(dockerfile))
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

    elif node.type == VOLUME:
        conf = Volume(node.name)
        # if 'properties' in node.entity_tpl:
        #     properties = node.entity_tpl['properties']
        #     conf.size = properties.get('size', None)

    elif node.type == SOFTWARE:
        conf = Software(node.name)
        if 'artifacts' in node.entity_tpl:
            artifacts = node.entity_tpl['artifacts']
            for key, value in artifacts.items():
                _log.debug('artifacts: {}'.format(value))
                conf.add_artifact(_get_file(base_path, key, value))
                # TODO: parse also dictionary artifacts
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
                    # path_split = abs_path.split('/')

                    intf[key]['cmd'] = File(None, abs_path)
                    # {
                    #     'file': path_split[-1],
                    #     'path': '/'.join(path_split[:-1]),
                    #     'file_path': abs_path
                    # }
                    _log.debug('path: {} file: {}'
                               .format(intf[key]['cmd'].path,
                                       intf[key]['cmd'].file))
                if 'inputs' in value:
                    intf[key]['inputs'] = value['inputs']
                    # intf[key]['inputs'] = _parse_map(value['inputs'])

            conf.interfaces = intf

    else:
        raise Exception(
            'ERROR: node type "{}" not supported!'.format(node.type))

    # get requirements
    if 'requirements' in node.entity_tpl:
        requirements = node.entity_tpl['requirements']
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

    tosca_name = tosca.input_path.split('/')[-1][:-5]
    tpl = Template(tosca_name)

    if hasattr(tosca, 'nodetemplates'):
        if tosca.outputs:
            tpl.outputs = tosca.outputs
        if tosca.nodetemplates:
            if not _components_exists(tosca.nodetemplates, components):
                raise Exception('ERROR: a selected component do not exists')

            for node in tosca.nodetemplates:
                if len(components) == 0 or node.name in components:
                    tpl.push(_parse_conf(node,
                                         repositories,
                                         base_path))

            if len(components) > 0:
                for node in _get_dependency_nodes(tpl, tosca):
                    tpl.push(_parse_conf(node,
                                         repositories,
                                         base_path))

            _add_pointer(tpl)

            _sort(tpl)

            _add_extension(tpl)

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

    return tpl


def _get_dependency_nodes(tpl, tosca):
    for n in tpl.deploy_order:
        for r in n.relationships:
            if r.to not in tpl:
                tosca_node = next((n for n in tosca.nodetemplates
                                   if n.name == r.to))
                yield tosca_node


def _components_exists(tosca_tpl, components):
    for c in components:
        if not any(c == n.name for n in tosca_tpl):
            return False
    return True


def _sort(tpl):
    unmarked = set(tpl.deploy_order)
    tpl.deploy_order = []

    def visit(n):
        if n._mark == 'temp':
            raise Exception('ERROR: the TOSCA file is not a DAG')
        elif n._mark == '':
            n._mark = 'temp'
            if n in unmarked:
                unmarked.remove(n)
            for r in n.relationships:
                visit(r.to)
            n._mark = 'perm'
            tpl.deploy_order.append(n)

    while len(unmarked) > 0:
        n = unmarked.pop()
        visit(n)


def _add_pointer(tpl):
    for node in tpl.deploy_order:
        for rel in node.relationships:
            rel.to = tpl[rel.to]


# - add pointer host_container pointer on software
# - add pointer on host property
# - add software links to the corrisponding container
def _add_extension(tpl):
    # Add the host_container property
    for node in tpl.software_order:
        if node.host is not None:
            if isinstance(node.host.to, Container):
                node.host_container = node.host.to
            elif isinstance(node.host.to, Software):
                node.host_container = node.host.to.host_container

    # Manage the case when a Software is connected
    # to a Container or a Software
    for node in tpl.software_order:
        for con in node._connection:
            if isinstance(con.to, Container):
                container = con.to
            if isinstance(con.to, Software):
                container = con.to.host_container
            node.host_container.add_overlay(container, con.to.name)

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
