class Artifact(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Artifact'

#
# def _get_str_name(obj):
#     return obj if isinstance(obj, six.string_types) else obj.name


class File(Artifact):

    def __init__(self, name, abs_path):
        super(self.__class__, self).__init__(name)
        split_path = abs_path.split('/')
        self.path = '/'.join(split_path[:-1])
        self.file = split_path[-1]

    @property
    def file_path(self):
        return self.path + '/' + self.file

    @property
    def format(self):
        pass

    def __str__(self):
        return 'File'


class DockerImage(Artifact):

    def __init__(self, attr, dockerfile=None):
        super(DockerImage, self).__init__('')
        self.name, self.tag = attr.split(':') if ':' in attr \
            else (attr, 'latest')
        self.dockerfile = dockerfile

    @property
    def to_build(self):
        return self.dockerfile is not None

    @property
    def format(self):
        return '{}:{}'.format(self.name, self.tag)

    def __str__(self):
        return 'DockerImage'


class DockerImageExecutable(DockerImage):

    def __init__(self, name, dockerfile=None):
        super(DockerImageExecutable, self).__init__(name, dockerfile)

    def __str__(self):
        return 'DockerImageExecutable'
