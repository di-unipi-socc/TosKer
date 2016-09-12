import os
from docker import Client, errors
from io import BytesIO
from . import utility


class Docker_engine:

    def __init__(self, socket='unix://var/run/docker.sock'):
        self.cli = Client(base_url=socket)

    def create(self, conf):

        # create docker image
        def create_container():
            os.makedirs('/tmp/docker_tosca/' + conf['name'], exist_ok=True)
            return self.cli.create_container(
                name=conf['name'],
                image=conf['image'],
                command=conf['cmd'],
                environment=conf['env'],
                detach=True,
                ports=[key for key in conf['ports'].keys()]
                if conf['ports'] else None,
                volumes=['/tmp/dt'] + ([k for k, v in conf['volumes'].items()]
                                       if conf['volumes'] else []),
                host_config=self.cli.create_host_config(
                    port_bindings=conf['ports'],
                    links=conf['link'],
                    volumes_from=conf['volumeFrom'],
                    binds=['/tmp/docker_tosca/'+conf['name']+':/tmp/dt'] +
                    ([v+':'+k for k, v in conf['volumes'].items()]
                     if conf['volumes'] else []),
                )
            )

        def remove_container():
            self.cli.stop(container=conf['name'])
            self.cli.remove_container(container=conf['name'], v=True)

        container = None
        try:
            if conf['dockerfile']:
                # with open(conf['dockerfile']) as f:
                #     byte = BytesIO(f.read().encode('utf-8'))
                print ('DEBUG:', conf['dockerfile'])
                print ('DEBUG:', '/'.join(conf['dockerfile'].split('/')[0:-1]))
                print ('DEBUG:', './' + conf['dockerfile'].split('/')[-1])
                utility.print_json(
                    self.cli.build(
                        path='/'.join(conf['dockerfile'].split('/')[0:-1]),
                        dockerfile='./' + conf['dockerfile'].split('/')[-1],
                        tag=conf['image'], stream=True
                    )
                )
            else:
                utility.print_json(
                    self.cli.pull(conf['image'], stream=True)
                )
            container = create_container()
        except errors.APIError:
            remove_container()
            container = create_container()

        return container.get('Id')

    def stop(self, name):
        try:
            return self.cli.stop(name)
        except errors.NotFound as e:
            print(e)

    def start(self, name):
        return self.cli.start(name)

    def delete(self, name):
        try:
            return self.cli.remove_container(name)
        except errors.NotFound as e:
            print (e)

    def container_exec(self, name, cmd, stream=False):
        print ('DEBUG:', 'name', name, 'cmd', cmd)
        exec_id = self.cli.exec_create(name, cmd)
        return self.cli.exec_start(exec_id, stream=stream)

    def create_volume(self, conf):
        return self.cli.create_volume(conf['name'], conf['driver'], conf['driver_opt'])

    def delete_volume(self, name):
        return self.cli.remove_volume(name)
