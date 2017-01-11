from ..helper import Logger
from ..graph.nodes import Container


class Container_manager:

    def __init__(self, docker):
        self._log = Logger.get(__name__)
        self._docker = docker

    def create(self, node):
        assert isinstance(node, Container)
        if node.persistent:
            self._docker.create_container(node)
        else:
            if node.to_build:
                self._docker.build_image(node)
            else:
                self._docker.pull_image(node.image)

    def start(self, node):
        assert isinstance(node, Container)
        if not node.persistent:
            return
        stat = self._docker.inspect_container(node)
        if stat is not None:
            node.id = stat['Id']
            self._docker.start_container(node)
        else:
            self._log.error(
                'ERROR: Container "{}" not exists!'.format(node.name))

    def stop(self, node):
        assert isinstance(node, Container)
        self._docker.stop_container(node)
        self._docker.delete_container(node)
        self._docker.create_container(node, from_saved=True)

    def delete(self, node):
        assert isinstance(node, Container)
        self._docker.delete_container(node)
        self._docker.delete_image(self._docker.get_saved_image(node))
