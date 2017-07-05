from ..helper import Logger
from ..graph.nodes import Volume
from .. import docker_interface


class Volume_manager:

    _log = Logger.get(__name__)
    # def __init__(self):
    #     self._log = Logger.get(__name__)
    #     # self._docker = docker

    @staticmethod
    def create(node):
        assert isinstance(node, Volume)
        docker_interface.create_volume(node)

    # @staticmethod
    # def delete(self, node):
    #     assert isinstance(node, Volume)
    #     docker_interface.delete_volume(node)
