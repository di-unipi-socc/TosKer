'''
Volume manager module
'''
# from ..helper import Logger
from .. import docker_interface
from ..graph.nodes import Volume


class VolumeManager:

    @staticmethod
    def create(node):
        assert isinstance(node, Volume)
        docker_interface.create_volume(node)

    # @staticmethod
    # def delete(self, node):
    #     assert isinstance(node, Volume)
    #     docker_interface.delete_volume(node)

    @staticmethod
    def exec_operation(component, operation):
        """Exec an operation on the component."""
        assert isinstance(component, Volume) and\
               isinstance(operation, str)
        try:
            getattr(VolumeManager, operation)(component)
        except AttributeError:
            return False
        return True
