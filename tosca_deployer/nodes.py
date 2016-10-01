def _add_to_map(d, k, v):
    if d is None:
        d = {}
    d[k] = v
    return d


def _add_to_list(l, i):
    if l is None:
        l = []
    l.append(i)
    return l


def _str_obj(o):
    return ', '.join(["{}: {}".format(k, v) for k, v in vars(o).items()])


class Base:
    def __init__(self, name):
        self.name = name
        self.link = None
        self.host = None
        self.volume = None
        self.id = None

    def add_link(self, item):
        self.link = _add_to_list(self.link, item)

    def add_host(self, item):
        self.host = _add_to_list(self.host, item)

    def add_volume(self, key, value):
        self.volume = _add_to_map(self.volume, key, value)

    def __getitem__(self, item):
        attr = vars(self)
        if item in attr:
            return attr[item]
        else:
            return None

    def __str__(self):
        _str_obj(self)


class Container(Base):
    image = None
    dockerfile = None
    env = None
    cmd = None
    ports = None

    def to_build(self):
        return self.dockerfile is not None

    def add_env(self, name, value):
        self.env = _add_to_map(self.env, name, value)

    def add_port(self, name, value):
        self.ports = _add_to_map(self.ports, name, value)

    def __getitem__(self, item):
        attr = super().__getitem__(item)
        if attr:
            return attr
        else:
            attr = vars(self)
            if item in attr:
                return attr[item]
        return None

    def __str__(self):
        return '{}, {}'.format(super().__str__(), _str_obj(self))


class Volume(Base):
    driver = 'local'
    device = None
    type = None
    driver_opt = None

    def get_all_opt(self):
        ris = self.driver_opt.copy() if self.driver_opt else {}
        if self.device:
            ris['device'] = self.device
        if self.type:
            ris['type'] = self.type
        return ris

    def add_driver_opt(self, name, value):
        self.driver_opt = _add_to_map(self.driver_opt, name, value)

    def __str__(self):
        return '{}, {}'.format(super().__str__(), _str_obj(self))


class Software(Base):
    artifacts = None
    inputs = None
    cmd = None

    def add_artifact(self, name, value):
        self.artifacts = _add_to_map(self.artifacts, name, value)

    def add_input(self, name, value):
        self.inputs = _add_to_map(self.inputs, name, value)

    def __str__(self):
        return '{}, {}'.format(super().__str__(), _str_obj(self))
