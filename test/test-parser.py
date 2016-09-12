from sys import argv
from collections import defaultdict
import json
from toscaparser.tosca_template import ToscaTemplate
from docker import Client, errors


def print_json(stream):
    for line in stream:
        print(json.dumps(json.loads(line.decode("utf-8")), indent=2), end='')


def print_byte(stream):
    for line in stream:
        print(line.decode("utf-8"), end='')


inputs = {'your_name': 'luca'}
if __name__ == '__main__':
    file_path = argv[1] if len(argv) == 2 else 'tosca-docker.yaml'

    tosca = ToscaTemplate(file_path, inputs, True)
    cli = Client(base_url='unix://var/run/docker.sock')

    if hasattr(tosca, 'nodetemplates'):
        if tosca.inputs:
            print ("\ninputs:")
            for input in tosca.inputs:
                print ("\t" + input.name)
                if input.name not in inputs:
                    inputs[input.name] = input.default

        nodetemplates = tosca.nodetemplates
        if nodetemplates:
            print ("\nnodetemplates:")
            for node in nodetemplates:
                container_conf = defaultdict(lambda: None)
                print ("\t" + node.name)
                container_conf['name'] = node.name

                # get artifacts
                artifacts = node.entity_tpl['artifacts']
                for key, value in artifacts.items():
                    print ("\t\t" + key)
                    print ("\t\t\t" + value['file'])

                    container_conf['image'] = value['file']

                # get properties
                if 'properties' in node.entity_tpl:
                    for key, value in node.entity_tpl['properties'].items():
                        print ("\t\t" + key)

                    if 'env_variable' in node.entity_tpl['properties']:
                        values = node.entity_tpl['properties']['env_variable']
                        env = {}
                        for key, value in values.items():
                            print ("\t\t\t" + str(value))
                            if type(value) is dict:
                                env[key] = inputs[value['get_input']]
                            else:
                                env[key] = value
                        container_conf['env'] = env

                    if 'cmd' in node.entity_tpl['properties']:
                        container_conf['cmd'] = node.entity_tpl[
                            'properties']['cmd']

                    if 'ports' in node.entity_tpl['properties']:
                        values = node.entity_tpl['properties']['ports']
                        ports = {}
                        for key, value in values.items():
                            print ("\t\t\t" + str(value))
                            if type(value) is dict:
                                ports[key] = inputs[value['get_input']]
                            else:
                                ports[key] = value
                        container_conf['ports'] = ports

                # get requirements
                if 'requirements' in node.entity_tpl:
                    requirements = node.entity_tpl['requirements']
                    for value in requirements:
                        print ("\t\t" + str(value))

                        for key, value in value.items():
                            if key == 'link':
                                if container_conf['link'] is list:
                                    container_conf['link'].append(
                                        (value, value))
                                else:
                                    container_conf['link'] = [(value, value)]

                # get interfaces
                try:
                    interfaces = node.entity_tpl['interfaces']['Standard']
                    for key, value in interfaces.items():
                        print ("\t\t" + key)
                        print ("\t\t\t" + str(value['inputs']))

                        container_conf['command'] = ' '.join(
                            value for value in value['inputs'].values())
                except:
                    pass

                print ('\nContainer_conf:\n' + str(container_conf))

                # create network
                # if container_conf['link'] is not None:
                #     net_config = cli.create_networking_config(
                #         {'bridge': cli.create_endpoint_config(
                #             links=container_conf['link']
                #         )}
                #     )
                # else:
                #     net_config = None

                # create docker image
                def create_container():
                    return cli.create_container(
                        name=container_conf['name'],
                        image=container_conf['image'],
                        command=container_conf['cmd'],
                        environment=container_conf['env'],
                        detach=True,
                        ports=[key for key in container_conf['ports'].keys()] if container_conf[
                            'ports'] else None,
                        host_config=cli.create_host_config(
                            port_bindings=container_conf['ports'],
                            links=container_conf['link']
                        )
                        #, networking_config=net_config
                    )
                container = None
                try:
                    container = create_container()
                except errors.NotFound:
                    print_json(
                        cli.pull(container_conf['image']+':latest', stream=True)
                    )

                    container = create_container()
                except errors.APIError:
                    cli.stop(container=container_conf['name'])
                    cli.remove_container(container=container_conf['name'])
                    container = create_container()

                cli.start(container=container.get('Id'))

    print ("\nDocker output: ")
    print_byte(
        cli.logs(container=container.get('Id'), stream=True)
    )
