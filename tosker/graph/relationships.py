'''
Relationships module
'''
import six

REQUIREMENTS = STORAGE, CONNECTION, DEPENDENCY, HOST =\
               'storage', 'connection', 'dependency', 'host'

CAPABILITIES = ENDPOINT, FEATURE, HOST, ATTACHMENT =\
               'endpoint', 'feature', 'host', 'attachement'


class Relationship(object):

    def __init__(self, origin, to, requirement=None, capability=None):
        self.origin = origin
        self.to = to
        self.requirement = requirement
        self.capability = capability

    def __str__(self):
        return 'o={0.origin},t={0.to},req={0.requirement},cap={0.capability}'.format(self)


def _get_str_name(obj):
    return obj if isinstance(obj, six.string_types) else obj.name


def _get_str_full_name(obj):
    return obj if isinstance(obj, six.string_types) else obj.full_name


class ConnectsTo(Relationship):

    def __init__(self, origin, node, alias=None,
                 requirement=CONNECTION, capability=ENDPOINT):
        super(ConnectsTo, self).__init__(origin, node, requirement, capability)
        self.alias = alias

    @property
    def format(self):
        full_name = _get_str_full_name(self.to)
        if self.alias is not None:
            return (full_name, self.alias)
        else:
            return (full_name, _get_str_name(self.to))

    def __str__(self):
        return 'ConnectsTo({})'.format(super(ConnectsTo, self).__str__())


class HostedOn(Relationship):

    def __init__(self, origin, node, requirement=HOST, capability=HOST):
        super(HostedOn, self).__init__(origin, node, requirement, capability)

    @property
    def format(self):
        return _get_str_name(self.to)

    def __str__(self):
        return 'HostedOn({})'.format(super(HostedOn, self).__str__())


class AttachesTo(Relationship):

    def __init__(self, origin, node, folder=None, requirement=STORAGE, capability=ATTACHMENT):
        super(AttachesTo, self).__init__(origin, node, requirement, capability)
        self.location = folder

    @property
    def format(self):
        if self.location is not None:
            return (self.location, _get_str_full_name(self.to))
        else:
            return _get_str_full_name(self.to)

    def __str__(self):
        return 'AttachesTo({})'.format(super(AttachesTo, self).__str__())


class DependsOn(Relationship):

    def __init__(self, origin, node, requirement=DEPENDENCY, capability=FEATURE):
        super(DependsOn, self).__init__(origin, node, requirement, capability)

    @property
    def format(self):
        return _get_str_name(self.to)

    def __str__(self):
        return 'DependsOn({})'.format(super(DependsOn, self).__str__())
