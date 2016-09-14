def _add_to_map(d, k, v):
    if d is None:
        d = {}
    d[k] = v


def _add_to_list(l, i):
    if l is None:
        l = []
    l.append(i)


class Base:
    name = None
    link = None
    host = None
    volume = None
    id = None

    def __init__(self, name):
        self.name = name

    def add_link(self, item):
        _add_to_list(self.link, item)

    def add_host(self, item):
        _add_to_list(self.host, item)

    def add_volume(self, key, value):
        _add_to_map(self.volume, key, value)


class Container(Base):
    image = None
    dockerfile = None
    env = None
    cmd = None
    ports = None

    def to_build(self):
        return self.dockerfile is not None

    def add_env(self, name, value):
        add_to_map(self.env, name, value)

    def add_port(self, name, value):
        add_to_map(self.ports, name, value)

    def __getitem__(self, item):
        if item == 'ports':
            return self.ports
        elif item == 'env':
            return self.env
        else:
            return None


class Volume(Base):
    driver = None
    driver_opt = None


class Software(Base):
    artifacts = None
    inputs = None
    cmd = None

    def add_artifact(self, name, value):
        add_to_map(self.artifacts, name, value)

    def add_input(self, name, value):
        add_to_map(self.input, name, value)
