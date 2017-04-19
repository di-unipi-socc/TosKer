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

    def __init__(self, attr):
        super(DockerImage, self).__init__('')
        self.name, self.tag = attr.split(':') if ':' in attr \
            else (attr, 'latest')

    @property
    def format(self):
        return '{}:{}'.format(self.name, self.tag)

    def __str__(self):
        return 'DockerImage'


class DockerImageExecutable(DockerImage):

    def __init__(self, name):
        super(DockerImageExecutable, self).__init__(name)

    def __str__(self):
        return 'DockerImageExecutable'


class Dockerfile(Artifact):

    def __init__(self, attr, dockerfile):
        super(Dockerfile, self).__init__('')
        self.name, self.tag = attr.split(':') if ':' in attr \
            else (attr, 'latest')
        self.dockerfile = dockerfile

    @property
    def format(self):
        return '{}:{}'.format(self.name, self.tag)

    def __str__(self):
        return 'Dockerfile'


class DockerfileExecutable(Dockerfile):

    def __init__(self, name, dockerfile):
        super(DockerfileExecutable, self).__init__(name, dockerfile)

    def __str__(self):
        return 'DockerfileExecutable'
