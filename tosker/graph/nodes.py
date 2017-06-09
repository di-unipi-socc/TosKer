from .relationships import HostedOn, ConnectsTo, AttachesTo, DependsOn
from .artifacts import File, DockerImage, DockerImageExecutable, \
                       DockerfileExecutable, Dockerfile


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

        # requirements
        self._depend = []
        self._connection = []
        self._volume = []
        self.artifacts = []

        # need by the topological sorting algorithm
        self._mark = ''

    @property
    def depend(self):
        return (i.format for i in self._depend)

    @property
    def connection(self):
        return (i.format for i in self._connection)

    @property
    def volume(self):
        return (i.format for i in self._volume)

    @property
    def relationships(self):
        return self._connection + self._volume + self._depend

    def add_depend(self, item):
        if not isinstance(item, DependsOn):
            item = DependsOn(item)
        self._depend.append(item)

    def add_connection(self, item, alias=None):
        if not isinstance(item, ConnectsTo):
            item = ConnectsTo(item, alias)
        self._connection.append(item)

    def add_volume(self, item, location=None):
        if not isinstance(item, AttachesTo):
            item = AttachesTo(item, location)
        self._volume.append(item)

    def add_artifact(self, art):
        assert isinstance(art, Artifact)
        self.artifacts.append(art)

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
        self._overlay = []

    @property
    def image(self):
        return self.artifacts[0]

    @image.setter
    def image(self, img):
        assert isinstance(img, (DockerImage, Dockerfile))
        self.artifacts = [img]

    @property
    def executable(self):
        return isinstance(self.image, (DockerImageExecutable,
                                       DockerfileExecutable))

    @property
    def connection(self):
        return (i.format for i in self._connection + self._overlay)

    def add_overlay(self, item, alias=None):
        if not isinstance(item, ConnectsTo):
            item = ConnectsTo(item, alias)
        self._overlay.append(item)

    def add_env(self, name, value):
        self.env = _add_to_map(self.env, name, value)

    def add_port(self, name, value):
        self.ports = _add_to_map(self.ports, name, value)

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
        self.artifacts = []
        self.interfaces = {}

        # requirements
        self._host = None
        self.host_container = None
        # self.depend = None
        # self.connection = None

    # def add_depend(self, item):
    #     self.depend = _add_to_list(self.depend, item)
    #
    # def add_connection(self, item):
    #     self.connection = _add_to_list(self.connection, item)
    @property
    def relationships(self):
        return super(self.__class__, self).relationships + \
               ([self._host] if self._host is not None else [])

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, item):
        if not isinstance(item, HostedOn):
            item = HostedOn(item)
        self._host = item

    def add_artifact(self, file):
        assert isinstance(file, File)
        self.artifacts.append(file)

    def get_str_obj(self):
        return '{}, {}'.format(super(self.__class__, self), _str_obj(self))

    def __str__(self):
        return '{} ({})'.format(self.name, 'software')
