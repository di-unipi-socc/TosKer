from .nodes import Container, Volume, Software


class Template:

    def __init__(self):
        self._nodes = {}
        self.deploy_order = []
        self.outputs = []

    def push(self, node):
        self._nodes[node.name] = node
        self.deploy_order.append(node)

    def __getitem__(self, name):
        return self._nodes.get(name, None)

    @property
    def container_order(self):
        return [i for i in self.deploy_order if type(i) is Container]

    @property
    def volume_order(self):
        return [i for i in self.deploy_order if type(i) is Volume]

    @property
    def software_order(self):
        return [i for i in self.deploy_order if type(i) is Software]

    def __str__(self):
        s = ''
        for i in self.deploy_order:
            s += '- ' + i.name + '\n    ' + str(i) + '\n'
        return s
