from .utility import Logger


class Volume_manager:

    def __init__(self, docker):
        self._log = Logger.get(__name__)
        self._docker = docker

    def create(self, node):
        self._docker.create_volume(node)

    def delete(self, node):
        self._docker.delete_volume(node)
