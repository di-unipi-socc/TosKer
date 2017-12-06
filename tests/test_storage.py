import os
from unittest import TestCase

from tinydb import Query
from tosker.graph.nodes import Container
from tosker.graph.protocol import (CONTAINER_STATE_CREATED,
                                   CONTAINER_STATE_DELETED,
                                   CONTAINER_STATE_RUNNING)
from tosker.graph.template import Template
from tosker.storage import Memory, Storage


class TestStorage(TestCase):
    @classmethod
    def setUpClass(self):
        pass

    def setUp(self):
        Storage.set_db('/tmp')

    def tearDown(self):
        os.remove('/tmp/db.json')

    def test_storage_insert(self):
        res = Storage.insert({'name': 'hello'})
        res = Storage.search(Query().name == 'hello')
        self.assertEqual(len(res), 1)

    def test_storage_remove(self):
        res = Storage.insert({'name': 'hello'})
        res = Storage.remove(Query().name == 'hello')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], 1)
        res = Storage.all()
        self.assertEqual(len(res), 0)

    def test_storage_update(self):
        self.test_storage_insert()

        res = Storage.update({'name': 'hello2'}, Query().name == 'hello')
        self.assertEqual(len(res), 1)

        res = Storage.search(Query().name == 'hello2')
        self.assertEqual(len(res), 1)

    def test_storage_all(self):
        self.test_storage_insert()

        res = Storage.all()
        self.assertEqual(len(res), 1)

    def test_memory_update_state(self):
        cont = Container('container_test')
        cont.tpl = Template('template_test')

        Memory.update_state(cont, CONTAINER_STATE_CREATED)
        state = Memory.get_comp_state(cont)
        self.assertEqual(state, CONTAINER_STATE_CREATED)

        Memory.update_state(cont, CONTAINER_STATE_RUNNING)
        state = Memory.get_comp_state(cont)
        self.assertEqual(state, CONTAINER_STATE_RUNNING)

        Memory.update_state(cont, CONTAINER_STATE_CREATED)
        state = Memory.get_comp_state(cont)
        self.assertEqual(state, CONTAINER_STATE_CREATED)

        Memory.update_state(cont, CONTAINER_STATE_DELETED)
        state = Memory.get_comp_state(cont)
        self.assertEqual(state, CONTAINER_STATE_DELETED)

    def test_memory_get_comps(self):
        tpl = Template('template_test')
        cont1 = Container('container_test1')
        cont1.tpl = tpl
        cont2 = Container('container_test2')
        cont2.tpl = tpl
        cont3 = Container('container_test3')
        cont3.tpl = tpl

        Memory.update_state(cont1, CONTAINER_STATE_CREATED)
        Memory.update_state(cont2, CONTAINER_STATE_RUNNING)
        Memory.update_state(cont3, CONTAINER_STATE_DELETED)

        comps = Memory.get_comps()
        self.assertEqual(len(comps), 3)

        comps = Memory.get_comps(filters={'state': CONTAINER_STATE_CREATED})
        self.assertEqual(len(comps), 1)
        self.assertEqual(comps[0]['full_name'],
                         'tosker_template_test.container_test1')

        comps = Memory.get_comps(filters={'state': CONTAINER_STATE_RUNNING})
        self.assertEqual(len(comps), 1)
        self.assertEqual(comps[0]['full_name'],
                         'tosker_template_test.container_test2')
    
    def test_memory_remove(self):
        cont = Container('container_test')
        cont.tpl = Template('template_test')

        Memory.insert(cont)
        res = Memory.get_comps()
        self.assertEqual(len(res), 1)

        Memory.remove(cont)
        res = Memory.get_comps()
        self.assertEqual(len(res), 0)
