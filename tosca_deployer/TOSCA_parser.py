from os import path
import re
from collections import defaultdict
from toscaparser.tosca_template import ToscaTemplate
from . import utility
from .nodes import Container, Software, Volume


def _check_requirements(node, running):
    for req in node.requirements:
        for key, value in req.items():
            value = value['node'] if type(value) is dict else value
            if value not in running:
                return False
    return True


def _parse_conf(node, inputs, repos, file_path):
    # conf = defaultdict(lambda: None)
    conf = None

    base_path = '/'.join(file_path.split('/')[:-1]) + '/'

    if node.type == 'in.lucar.docker.container':
        conf = Container(node.name)

        def parse_dockerfile(image, dockerfile):
            conf.image = image
            conf.dockerfile = dockerfile

        def parse_pull_image(img_name, repo_url=None):
            if ':' in img_name:
                conf.image = img_name
            else:
                conf.image = img_name + ':latest'
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
                if value['type'] == 'tosca.artifacts.Deployment.Image.Container.Docker':
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

        def parse_map(map):
            res = {}
            for key, value in map.items():
                if type(value) is dict:
                    res[key] = inputs[value['get_input']]
                else:
                    res[key] = value
            return res

        # get properties
        if 'properties' in node.entity_tpl:
            if 'env_variable' in node.entity_tpl['properties']:
                values = node.entity_tpl['properties']['env_variable']
                conf.env = parse_map(values)

            if 'cmd' in node.entity_tpl['properties']:
                conf.cmd = node.entity_tpl['properties']['cmd']

            if 'ports' in node.entity_tpl['properties']:
                values = node.entity_tpl['properties']['ports']
                conf.ports = parse_map(values)

            # if 'volumes' in node.entity_tpl['properties']:
            #     values = node.entity_tpl['properties']['volumes']
            #     conf.volumes = parse_map(values)
            #     # check if is a relative_path
            #     for key, value in conf.volumes.items():
            #         if '/' in value and value[0] != '/':
            #             conf.volumes.[key] = path.abspath(
            #                 path.join(base_path, value)
            #             )

        # # get requirements
        # if 'requirements' in node.entity_tpl:
        #     requirements = node.entity_tpl['requirements']
        #     for value in requirements:
        #         for key, value in value.items():
        #             if key == 'link':
        #                 if conf['link'] is list:
        #                     conf['link'].append(
        #                         (value, value))
        #                 else:
        #                     conf['link'] = [(value, value)]

    elif node.type == 'in.lucar.docker.volume':
        conf = Volume(node.name)
        if 'properties' in node.entity_tpl:
            properties = node.entity_tpl['properties']
            conf.driver = properties.get('driver', None)
            conf.type = properties.get('type', None)
            conf.device = properties.get('device', None)
            conf.driver_opt = properties.get('driver_opt', None)
    else:
        conf = Software(node.name)
        if 'artifacts' in node.entity_tpl:
            artifacts = node.entity_tpl['artifacts']
            for key, value in artifacts.items():
                # print ('artifacts', value)
                abs_path = path.abspath(
                    path.join(base_path, value)
                )
                conf.add_artifact(key, abs_path)

        # get interfaces
        # try:
            interfaces = node.entity_tpl['interfaces']['Standard']
            for key, value in interfaces.items():
                conf.cmd = path.abspath(
                    path.join(base_path, value['implementation'])
                )
                for key, value in value['inputs'].items():
                    if type(value) is dict:
                        if 'get_artifact' in value:
                            conf.add_input(key, conf['artifacts'][
                                           value['get_artifact'][1]])
                    else:
                        conf.add_input(key, value)
        # except:
        #     print ('error:')

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
            if 'host' in value:
                conf.add_host(value['host'])
            if 'volume' in value:
                volume = value['volume']
                if type(volume) is dict:
                    conf.add_volume(volume['relationship']['properties'][
                                    'location'], volume['node'])
    print ('\nContainer_conf:\n', conf.name, conf)
    return conf


def parse_TOSCA(file_path, inputs):
    tosca = ToscaTemplate(file_path, inputs, True)
    print (dir(tosca))
    print (dir(tosca.tpl))

    utility.print_TOSCA(tosca)
    deploy_order = []
    outputs = []

    if hasattr(tosca, 'nodetemplates'):

        # get inputs
        if tosca.inputs:
            for input in tosca.inputs:
                if input.name not in inputs:
                    inputs[input.name] = input.default

        if tosca.outputs:
            for out in tosca.outputs:
                print('DEBUG: ', out)
                outputs.append(out)

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

                # print('requirements:', node.requirements)
                # print('running_container:', running_container)

                if not _check_requirements(node, running_container):
                    i += 1
                    continue

                # if node.type == 'tosca.nodes.SoftwareComponent':
                #     docker = Docker_engine()
                #     conf = deploy_order[node.requirements[0]['host']]
                #     conf['name'] += '_before_' + node.name
                #     docker.create(conf)
                #     docker.container_exec(conf['name'], )
                # else:
                deploy_order.append((node.name, _parse_conf(
                    node, inputs, tosca.tpl.get('repositories', None), file_path)))
                running_container.add(node.name)

    return (deploy_order, outputs)
