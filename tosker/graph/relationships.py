import six


class Relationship(object):

    def __init__(self, node):
        self.to = node

    def __str__(self):
        return 'Relationship'


def _get_str_name(obj):
    return obj if isinstance(obj, six.string_types) else obj.name


class ConnectsTo(Relationship):

    def __init__(self, node, alias=None):
        super(self.__class__, self).__init__(node)
        self.alias = alias

    def format(self):
        if self.alias is not None:
            return (_get_str_name(self.to), self.alias)
        else:
            return _get_str_name(self.to)

    def __str__(self):
        return 'ConnectsTo'


class HostedOn(Relationship):

    def __init__(self, node):
        super(self.__class__, self).__init__(node)

    def format(self):
        return _get_str_name(self.to)

    def __str__(self):
        return 'HostedOn'


class AttachesTo(Relationship):

    def __init__(self, node, folder=None):
        super(self.__class__, self).__init__(node)
        self.location = folder

    def format(self):
        if self.location is not None:
            return {self.location: _get_str_name(self.to)}
        else:
            return _get_str_name(self.to)

    def __str__(self):
        return 'AttachesTo'


class DependsOn(Relationship):

    def __init__(self, node):
        super(self.__class__, self).__init__(node)

    def format(self):
        return _get_str_name(self.to)

    def __str__(self):
        return 'DependsOn'