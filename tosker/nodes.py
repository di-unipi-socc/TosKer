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


class Base(object):

    def __init__(self, name):
        self.name = name
        self.link = None
        self.depends = None
        self._fuctions = {}

    def add_link(self, item):
        self.link = _add_to_list(self.link, item)

    def add_depends(self, item):
        self.depends = _add_to_list(self.depends, item)

    def __getitem__(self, item):
        attr = vars(self)
        if item in attr:
            return attr[item]
        else:
            return None

    def __str__(self):
        return self.name

    def get_str_obj(self):
        _str_obj(self)


class Container(Base):

    def __init__(self, name):
        # super().__init__(name)
        super(self.__class__, self).__init__(name)
        self.id = None
        self.image_name = None
        self.tag_name = None
        self.dockerfile = None
        self.env = None
        self.cmd = None
        self.entrypoint = None
        self.ports = None
        self.persistent = False
        self.volume = None
        self.saved_image = None

        self.software_layer = []  # This is not used now

    @property
    def to_build(self):
        return self.dockerfile is not None

    def add_volume(self, key, value):
        self.volume = _add_to_map(self.volume, key, value)

    def add_env(self, name, value):
        self.env = _add_to_map(self.env, name, value)

    def add_port(self, name, value):
        self.ports = _add_to_map(self.ports, name, value)

    @property
    def image(self):
        return '{}:{}'.format(self.image_name, self.tag_name)

    @image.setter
    def image(self, attr):
        if ':' in attr:
            self.image_name, self.tag_name = attr.split(':')
        else:
            self.image_name = attr
            self.tag_name = 'latest'

    def __getitem__(self, item):
        attr = super(self.__class__, self).__getitem__(item)
        if attr:
            return attr
        else:
            attr = vars(self)
            if item in attr:
                return attr[item]
        return None

    def get_str_obj(self):
        return '{}, {}'.format(super(self.__class__, self).__str__(), _str_obj(self))

    def __str__(self):
        return '{} ({})'.format(self.name, 'container')


class Volume(Base):

    def __init__(self, name):
        # super().__init__(name)
        super(self.__class__, self).__init__(name)
        self.driver = 'local'
        self.device = None
        self.type = None
        self.size = None
        self.driver_opt = None

    def get_all_opt(self):
        ris = self.driver_opt.copy() if self.driver_opt else {}
        if self.device:
            ris['device'] = self.device
        if self.type:
            ris['type'] = self.type
        if self.size:
            ris['size'] = self.size
        return ris

    def add_driver_opt(self, name, value):
        self.driver_opt = _add_to_map(self.driver_opt, name, value)

    def get_str_obj(self):
        return '{}, {}'.format(super(self.__class__, self), _str_obj(self))

    def __str__(self):
        return '{} ({})'.format(self.name, 'volume')


class Software(Base):

    def __init__(self, name):
        # super().__init__(name)
        super(self.__class__, self).__init__(name)
        self.host = None
        self.artifacts = None
        self.interfaces = {}
        self.host_container = None

    def add_artifact(self, name, value):
        self.artifacts = _add_to_map(self.artifacts, name, value)

    # def add_input(self, name, value):
    #     self.inputs = _add_to_map(self.inputs, name, value)

    def get_str_obj(self):
        return '{}, {}'.format(super(self.__class__, self), _str_obj(self))

    def __str__(self):
        return '{} ({})'.format(self.name, 'software')
