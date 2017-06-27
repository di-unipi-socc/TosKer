from functools import wraps
from enum import Enum
from tinydb import TinyDB, Query
from .graph.nodes import Root


class Storage:
    def _singleton(func):
        @wraps(func)
        def func_wrapper(*args, **kwds):
            assert Storage.db is not None
            return func(*args, **kwds)
        return func_wrapper

    @staticmethod
    def set_db(path):
        Storage.db = TinyDB('{}/db.json'.format(path))

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


class Memory:
    class STATE(Enum):
        DELETED = 'deleted'
        CREATED = 'created'
        STARTED = 'started'

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
        assert isinstance(comp, Root) and state in Memory.STATE

        if (state == Memory.STATE.DELETED):
            Storage.remove(Query().full_name == comp.full_name)
        else:
            if len(Storage.update({'state': state.value},
                                  Query().full_name == comp.full_name)) < 1:
                # comp not found
                comp_dict = Memory._comp_to_dict(comp)
                comp_dict['state'] = state.value
                Storage.insert(comp_dict)
            else:
                # comp updated
                pass

    @staticmethod
    def get_comp_state(comp):
        assert isinstance(comp, Root)
        res = Storage.search(Query().full_name == comp.full_name)
        return Memory.STATE(res[0]['state']) \
            if len(res) == 1 else Memory.STATE.DELETED

    @staticmethod
    def get_comps(state=None):
        if state is None:
            return Storage.all()
        else:
            assert state in Memory.STATE
            return Storage.search(Query().state == state.value)
