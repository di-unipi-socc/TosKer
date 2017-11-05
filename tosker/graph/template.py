'''
Template module
'''
import six

from .nodes import Container, Root, Software, Volume


class Template:

    def __init__(self, name):
        self._nodes = {}
        self.name = name
        self.outputs = []
        self.tmp_dir = None

    @property
    def nodes(self):
        return (v for k, v in self._nodes.items())

    @property
    def containers(self):
        return (v for k, v in self._nodes.items() if isinstance(v, Container))

    @property
    def volumes(self):
        return (v for k, v in self._nodes.items() if isinstance(v, Volume))

    @property
    def software(self):
        return (v for k, v in self._nodes.items() if isinstance(v, Software))

    def push(self, node):
        self._nodes[node.name] = node

    def __getitem__(self, name):
        return self._nodes.get(name, None)

    def __contains__(self, item):
        if isinstance(item, six.string_types):
            return self[item] is not None
        if isinstance(item, Root):
            return self[item.name] is not None
        return False

    def __str__(self):
        return ', '.join((i.name for i in self.nodes))
