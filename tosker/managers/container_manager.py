'''
Container manager module
'''
# from ..helper import Logger
# from ..graph.artifacts import Dockerfile
from .. import docker_interface
from ..graph.nodes import Container

class ContainerManager:

    @staticmethod
    def create(node):
        assert isinstance(node, Container)
        # if node.executable:
        docker_interface.create_container(node)
        # else:
        #     if isinstance(node.image, Dockerfile):
        #         docker_interface.build_image(node)
        #     else:
        #         docker_interface.pull_image(node.image.format)

    @staticmethod
    def start(node):
        assert isinstance(node, Container)
        if not node.executable:
            return
        stat = docker_interface.inspect_container(node)
        if stat is not None:
            node.id = stat['Id']
            docker_interface.start_container(node)

    @staticmethod
    def stop(node):
        assert isinstance(node, Container)
        docker_interface.stop_container(node)
        # docker_interface.delete_container(node)
        docker_interface.create_container(node, from_saved=True, force=True)

    @staticmethod
    def delete(node):
        assert isinstance(node, Container)
        docker_interface.delete_container(node)
        docker_interface.delete_image(docker_interface.get_saved_image(node))

    @staticmethod
    def exec_operation(component, operation):
        """Exec an operation on the component."""
        assert isinstance(component, Container)
        assert isinstance(operation, str)
        try:
            getattr(ContainerManager, operation)(component)
        except AttributeError:
            return False
        return True
