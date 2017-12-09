'''
Storage module
'''
from enum import Enum
from functools import reduce, wraps

import six
from tinydb import Query, TinyDB

from .graph.nodes import Root
from .helper import Logger


class Storage:

    def _singleton(func):
        @wraps(func)
        def func_wrapper(*args, **kwds):
            if Storage.db is not None:
                return func(*args, **kwds)
            else:
                raise Exception('First call "set_db" method')
        return func_wrapper

    @staticmethod
    def set_db(path):
        Storage.db = TinyDB('{}/db.json'.format(path))

    @staticmethod
    @_singleton
    def purge():
        return Storage.db.purge_tables()

    @staticmethod
    @_singleton
    def insert(obj):
        return Storage.db.insert(obj)

    @staticmethod
    @_singleton
    def search(condition):
        return Storage.db.search(condition)

    @staticmethod
    @_singleton
    def update(fields, condition):
        return Storage.db.update(fields, condition)

    @staticmethod
    @_singleton
    def remove(condition):
        return Storage.db.remove(condition)

    @staticmethod
    @_singleton
    def all():
        return Storage.db.all()


class Memory(Storage):

    @staticmethod
    def _comp_to_dict(comp):
        return {
            'name': comp.name,
            'full_name': comp.full_name,
            'type': type(comp).__name__,
            'app_name': comp.tpl.name,
            'state': 'deleted'
        }

    @staticmethod
    def update_state(comp, state):
        assert isinstance(comp, (six.string_types, dict, Root))
        assert isinstance(state, str)

        def _update_state(full_name, state):
            log = Logger.get(__name__)
            log.debug('update %s to %s', full_name, state)
            return Memory.update({'state': state},
                                 Query().full_name == full_name)

        if isinstance(comp, six.string_types):
            _update_state(comp, state)
        elif isinstance(comp, dict):
            res = _update_state(comp['full_name'], state)
            if len(res) < 1:
                # comp not found
                comp['state'] = state.value
                Memory.insert(comp)
        elif isinstance(comp, Root):
            res = _update_state(comp.full_name, state)
            if len(res) < 1:
                # comp not found
                comp_dict = Memory._comp_to_dict(comp)
                comp_dict['state'] = state
                Memory.insert(comp_dict)
        else:
            raise AssertionError()

    @staticmethod
    def remove(obj):
        assert isinstance(obj, (dict, Root, str))
        if isinstance(obj, Root):
            name = obj.full_name
        elif isinstance(obj, dict):
            name = obj['full_name']
        else:
            name = obj
        return Storage.remove(Query().full_name == name)

    @staticmethod
    def insert(obj):
        assert isinstance(obj, (dict, Root))
        if isinstance(obj, Root):
            obj = Memory._comp_to_dict(obj)

        return Storage.insert(obj)

    @staticmethod
    def get_comp_state(comp):
        assert isinstance(comp, Root)
        res = Memory.search(Query().full_name == comp.full_name)
        return res[0]['state'] if len(res) == 1 else None

    @staticmethod
    def get_comps(app_name=None, filters=None):
        queries = []
        if filters is not None:
            assert isinstance(filters, dict)
            for key, value in filters.items():
                queries.append(Query()[key] == value)

        if app_name is not None:
            queries.append(Query()['app_name'] == app_name)

        if queries:
            cond = reduce(lambda a, b: a & b, queries)
            return Memory.search(cond)
        else:
            return Memory.all()
