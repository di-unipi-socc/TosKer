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


class Root(object):

    def __init__(self, name):
        self.name = name
        self._ATTRIBUTE = {}

    def __str__(self):
        return self.name

    def __getitem__(self, item):
        return self._ATTRIBUTE.get(item, lambda: None)()

    def get_str_obj(self):
        _str_obj(self)


class Container(Root):

    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        # attributes
        self.id = None
        self.env = None
        self.cmd = None
        self.ports = None
        self._ATTRIBUTE = {
            'id': lambda: self.id,
            'ports': lambda: self.ports,
            'env_variable': lambda: self.env,
            'command': lambda: self.cmd
        }

        # artifacts
        self.image_name = None
        self.tag_name = None
        self.dockerfile = None

        # flags
        # TODO: create two distint classes and remove this flag
        self.persistent = False

        # requirements
        self.depend = None
        self.connection = None
        self.volume = None

    @property
    def to_build(self):
        return self.dockerfile is not None

    @property
    def image(self):
        return '{}:{}'.format(self.image_name, self.tag_name)

    @image.setter
    def image(self, attr):
        self.image_name, self.tag_name = attr.split(':') if ':' in attr \
                                                         else (attr, 'latest')

    def add_env(self, name, value):
        self.env = _add_to_map(self.env, name, value)

    def add_port(self, name, value):
        self.ports = _add_to_map(self.ports, name, value)

    def add_depend(self, item):
        self.depend = _add_to_list(self.depend, item)

    def add_connection(self, item):
        self.connection = _add_to_list(self.connection, item)

    def add_volume(self, key, value):
        self.volume = _add_to_map(self.volume, key, value)

    def get_str_obj(self):
        return '{}, {}'.format(
            super(self.__class__, self).__str__(), _str_obj(self)
        )

    def __str__(self):
        return '{} ({})'.format(self.name, 'container')


class Volume(Root):

    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.id = None
        self.size = None
        self._ATTRIBUTE = {
            'id': lambda: self.id,
            'size': lambda: self.size
        }

        self.driver_opt = None

    def get_all_opt(self):
        ris = self.driver_opt.copy() if self.driver_opt else {}
        if self.size:
            ris['size'] = self.size
        return ris

    def add_driver_opt(self, name, value):
        self.driver_opt = _add_to_map(self.driver_opt, name, value)

    def __str__(self):
        return '{} ({})'.format(self.name, 'volume')

    def get_str_obj(self):
        return '{}, {}'.format(super(self.__class__, self), _str_obj(self))


class Software(Root):

    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.artifacts = None
        self.interfaces = {}

        # requirements
        self.host = None
        self.host_container = None
        self.depend = None
        self.connection = None

    def add_depend(self, item):
        self.depend = _add_to_list(self.depend, item)

    def add_connection(self, item):
        self.connection = _add_to_list(self.connection, item)

    def add_artifact(self, name, value):
        self.artifacts = _add_to_map(self.artifacts, name, value)

    def get_str_obj(self):
        return '{}, {}'.format(super(self.__class__, self), _str_obj(self))

    def __str__(self):
        return '{} ({})'.format(self.name, 'software')
