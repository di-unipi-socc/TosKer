import os
import unittest

from tinydb import Query

from tosker.graph.nodes import Container
from tosker.graph.template import Template
from tosker.storage import Memory, Storage


class TestStorage(unittest.TestCase):
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

        Memory.update_state(cont, Memory.STATE.CREATED)
        state = Memory.get_comp_state(cont)
        self.assertEqual(state, Memory.STATE.CREATED)

        Memory.update_state(cont, Memory.STATE.STARTED)
        state = Memory.get_comp_state(cont)
        self.assertEqual(state, Memory.STATE.STARTED)

        Memory.update_state(cont, Memory.STATE.CREATED)
        state = Memory.get_comp_state(cont)
        self.assertEqual(state, Memory.STATE.CREATED)

        Memory.update_state(cont, Memory.STATE.DELETED)
        state = Memory.get_comp_state(cont)
        self.assertEqual(state, Memory.STATE.DELETED)

    def test_memory_get_comps(self):
        tpl = Template('template_test')
        cont1 = Container('container_test1')
        cont1.tpl = tpl
        cont2 = Container('container_test2')
        cont2.tpl = tpl
        cont3 = Container('container_test3')
        cont3.tpl = tpl

        Memory.update_state(cont1, Memory.STATE.CREATED)
        Memory.update_state(cont2, Memory.STATE.STARTED)
        Memory.update_state(cont3, Memory.STATE.DELETED)

        comps = Memory.get_comps()
        self.assertEqual(len(comps), 3)

        comps = Memory.get_comps(filters={'state': Memory.STATE.CREATED})
        self.assertEqual(len(comps), 1)
        self.assertEqual(comps[0]['full_name'],
                         'tosker_template_test.container_test1')

        comps = Memory.get_comps(filters={'state': Memory.STATE.STARTED})
        self.assertEqual(len(comps), 1)
        self.assertEqual(comps[0]['full_name'],
                         'tosker_template_test.container_test2')
