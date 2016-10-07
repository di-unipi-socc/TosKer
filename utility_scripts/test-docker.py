from docker import Client

cli = Client(base_url='unix://var/run/docker.sock')
container = cli.create_container(
    image='ubuntu:latest',
    command="sleep 2")
response = cli.start(container=container.get('Id'))
print(cli.logs(container=container.get('Id')))

print ('\n')
print (cli.containers())
