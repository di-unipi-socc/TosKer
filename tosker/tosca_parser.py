"""
Tosca parser module
"""
import re
from os import path

import toscaparser
from toscaparser.prereq.csar import CSAR
from toscaparser.tosca_template import ToscaTemplate

from . import helper
from .graph.artifacts import (Dockerfile, DockerfileExecutable, DockerImage,
                              DockerImageExecutable, File)
from .graph.nodes import Container, Software, Volume
from .graph.protocol import ALIVE, Protocol, State, Transition
from .graph.relationships import HOST
from .graph.template import Template
from .helper import Logger

_log = None

# CUSTOM TYPE
CONTAINER = 'tosker.nodes.Container'
VOLUME = 'tosker.nodes.Volume'
SOFTWARE = 'tosker.nodes.Software'
IMAGE = 'tosker.artifacts.Image'
IMAGE_EXE = 'tosker.artifacts.Image.Service'
DOCKERFILE = 'tosker.artifacts.Dockerfile'
DOCKERFILE_EXE = 'tosker.artifacts.Dockerfile.Service'
PROTOCOL_POLICY = 'tosker.policies.Protocol'
# EXECUTABLE_IMAGE = 'tosker.artifacts.ExecutableImage'
# IMAGE2 = 'tosca.artifacts.Deployment.Image.Container.Docker'
# DOCKERFILE2 = 'tosca.artifacts.File'

# PROTOCOL NAMES
PROT_STATES = 'states'
PROT_INITIAL_STATE = 'initial_state'
PROT_TRANSITIONS = 'transitions'
PROT_STATE_PROP = PROT_REQUIRES, PROT_OFFERS = 'requires', 'offers'
PROT_TRANSITION_PROP = PROT_SOURCE, PROT_TARGET, PROT_INTERFACE, PROT_OPERATION, PROT_REQUIRES =\
                       'source', 'target', 'interface', 'operation', 'requires'

# REQUIREMENTS
REL_CONNECT = 'tosca.relationships.ConnectsTo'
REL_DEPEND = 'tosca.relationships.DependsOn'
REL_ATTACH = 'tosca.relationships.AttachesTo'
REL_HOST = 'tosca.relationships.HostedOn'


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
    if node.is_derived_from(CONTAINER):
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

    elif node.is_derived_from(VOLUME):
        conf = Volume(node.name)

    elif node.is_derived_from(SOFTWARE):
        conf = Software(node.name)
        if 'artifacts' in node.entity_tpl:
            artifacts = node.entity_tpl['artifacts']
            for key, value in artifacts.items():
                _log.debug('artifacts: %s', value)
                conf.add_artifact(_get_file(base_path, key, value))
                # TODO: parse also dictionary artifacts
                _log.debug('artifacts: %s', conf.artifacts)

        # get interfaces
        if 'interfaces' in node.entity_tpl:
            interfaces = {}
            for name, tpl_interface in node.entity_tpl['interfaces'].items():
                interfaces[name] = interface = {}
                for key, value in tpl_interface.items():
                    interface[key] = operation = {}
                    if 'implementation' in value:
                        abs_path = path.abspath(
                            path.join(base_path, value['implementation'])
                        )
                        operation['cmd'] = File(None, abs_path)
                        _log.debug('path: %s file: %s', operation['cmd'].path,
                                   operation['cmd'].file)
                    if 'inputs' in value:
                        operation['inputs'] = value['inputs']

            conf.interfaces = interfaces

    else:
        raise ValueError(
            'node type "{}" not supported!'.format(node.type))

    def get_req_type(req):
        return next((n[req] for n in node.type_definition.requirements if req in n))['relationship']

    # get requirements
    for req in node.requirements:
        name, value = list(req.items())[0]
        target = value['node'] if isinstance(value, dict) else value

        req_type = get_req_type(name)
        _log.debug('%s %s', target, req_type)

        if req_type == REL_CONNECT:
            conf.add_connection(target)
        if req_type == REL_DEPEND:
            conf.add_depend(target)
        if req_type == REL_HOST:
            conf.host = target
        if req_type == REL_ATTACH:
            location = value['relationship']['properties']['location']
            _log.debug('location: %s', location)
            conf.add_volume(target, location)

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

    if hasattr(tosca, 'topology_template'):
        if hasattr(tosca, 'outputs'):
            tpl.outputs = tosca.outputs

        if hasattr(tosca, 'nodetemplates'):
            for node in tosca.nodetemplates:
                tpl.push(_parse_conf(tpl, node,
                                     repositories,
                                     base_path))
            _add_pointer(tpl)
            _add_back_links(tpl)
            _add_extension(tpl)

        if hasattr(tosca, 'policies'):
            for policy in tosca.policies:
                if not policy.is_derived_from(PROTOCOL_POLICY):
                    raise ValueError('policy of type "{}" not supported.'.format(policy.type))
                # policy.name
                # policy.properties
                # policy.targets
                _validate_protocol(policy.properties)
                protocol = _parse_protocol(policy.properties)
                _log.debug(protocol)
                for target in policy.targets:
                    comp = tpl[target]
                    if not isinstance(comp, Software):
                        raise ValueError('Only software support custom protocol')
                    comp.protocol = protocol

    return tpl


def _validate_protocol(properties):
    # TODO: check that the declared initial_state is a valid state
    if PROT_INITIAL_STATE not in properties:
        raise ValueError('Attribute {}, is required in policy properties')
    if not isinstance(properties[PROT_INITIAL_STATE], str):
        raise ValueError('Attribute {}, must be string')

    if PROT_STATES not in properties:
        raise ValueError('Attribute {}, is required in policy properties')
    if not isinstance(properties[PROT_STATES], dict):
        raise ValueError('Attribute {}, must be dictionary')

    if PROT_TRANSITIONS not in properties:
        raise ValueError('Attribute {}, is required in policy properties')
    if not isinstance(properties[PROT_TRANSITIONS], list):
        raise ValueError('Attribute {}, must be list')

    for name, value in properties[PROT_STATES].items():
        if value is not None :
            for name, value in value.items():
                if name not in PROT_STATE_PROP:
                    raise ValueError('State must contains only {} and {}'
                                     ''.format(PROT_OFFERS, PROT_REQUIRES))
                if not isinstance(value, list):
                    raise ValueError('{} and {} must be list'.format(PROT_OFFERS, PROT_REQUIRES))

    req_prop = (PROT_SOURCE, PROT_TARGET, PROT_INTERFACE, PROT_OPERATION)
    for transition in properties[PROT_TRANSITIONS]:
        if any((p not in transition for p in req_prop)):
            raise ValueError('Transition require the properties {}'
                             ''.format(', '.join(req_prop)))
        for name, value in transition.items():
            if name not in PROT_TRANSITION_PROP:
                raise ValueError('Transition must contains only {}'
                                 ''.format(', '.join(PROT_TRANSITION_PROP)))


def _parse_protocol(properties):
    """
    Parse and return the protocol to manage the Software compnent from the TOSCA policy.
    
    This function also add the ALIVE requirements on all the state except the initial one
    and the HOST requirements on all the transition. This permits to always have a container
    underneed the Software componets.
    """
    protocol = Protocol()
    
    for name, value in properties[PROT_STATES].items():
        value = value if value is not None else {}
        state = State(name,
                      requires=value.get(PROT_REQUIRES, None),
                      offers=value.get(PROT_OFFERS, None))
        protocol.states.append(state)
        if name == properties[PROT_INITIAL_STATE]:
            protocol.initial_state = state
        else:
            state.requires.append(ALIVE)
            state.offers.append(ALIVE)

    for transition in properties[PROT_TRANSITIONS]:
        source = protocol.find_state(transition[PROT_SOURCE])
        target = protocol.find_state(transition[PROT_TARGET])
        transition = Transition(source, target,
                                transition[PROT_INTERFACE],
                                transition[PROT_OPERATION],
                                [HOST] + transition.get(PROT_REQUIRES, []))
        protocol.transitions.append(transition)
        source.transitions.append(transition)
    return protocol


def _add_pointer(tpl):
    for node in tpl.nodes:
        for rel in node.relationships:
            rel.to = tpl[rel.to]


def _add_back_links(tpl):
    for node in tpl.nodes:
        for rel in node.relationships:
            rel.to.up_requirements.append(rel)



def _add_extension(tpl):
    """
    This function add the following extension on the template:
      - add pointer host_container pointer on software
      - add pointer on host property
      - add software links to the corrisponding container
    """
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
