from ..helper import Logger
from ..graph.nodes import Volume


class Volume_manager:

    def __init__(self, docker):
        self._log = Logger.get(__name__)
        self._docker = docker

    def create(self, node):
        assert isinstance(node, Volume)
        self._docker.create_volume(node)

    # def delete(self, node):
    #     assert isinstance(node, Volume)
    #     self._docker.delete_volume(node)
