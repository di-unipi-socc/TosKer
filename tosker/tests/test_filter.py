import unittest
from tosker.graph.template import Template
from tosker.graph.nodes import Container, Software, Volume
from tosker.tosca_utility import filter_components


class Test_Filter(unittest.TestCase):
    def setUp(self):
        self._tpl = Template('test')
        c1 = Container('c1')
        self._tpl.push(c1)
        c2 = Container('c2')
        self._tpl.push(c2)
        s1 = Software('s1')
        self._tpl.push(s1)
        s2 = Software('s2')
        self._tpl.push(s2)
        s3 = Software('s3')
        self._tpl.push(s3)
        v1 = Volume('v1')
        self._tpl.push(v1)
        s3.host = s2
        s2.host = c2
        s2.add_connection(s1)
        s1.host = c1
        c2.add_volume('/asd', v1)

    def test_single(self):
        new = filter_components(self._tpl, ['s3'])
        self.assertListEqual(
            [i.name for i in new.deploy_order],
            ['c1', 's1', 'v1', 'c2', 's2', 's3']
        )

        new = filter_components(self._tpl, ['s2'])
        self.assertListEqual(
            [i.name for i in new.deploy_order],
            ['c1', 's1', 'v1', 'c2', 's2']
        )

        new = filter_components(self._tpl, ['s1'])
        self.assertListEqual(
            [i.name for i in new.deploy_order],
            ['c1', 's1']
        )

        new = filter_components(self._tpl, ['c2'])
        self.assertListEqual(
            [i.name for i in new.deploy_order],
            ['v1', 'c2']
        )

        new = filter_components(self._tpl, ['c1'])
        self.assertListEqual(
            [i.name for i in new.deploy_order],
            ['c1']
        )

        new = filter_components(self._tpl, ['v1'])
        self.assertListEqual(
            [i.name for i in new.deploy_order],
            ['v1']
        )

    def test_couple(self):
        new = filter_components(self._tpl, ['s1', 's2'])
        self.assertListEqual(
            [i.name for i in new.deploy_order],
            ['c1', 's1', 'v1', 'c2', 's2']
        )

        new = filter_components(self._tpl, ['c2', 's1'])
        self.assertListEqual(
            [i.name for i in new.deploy_order],
            ['c1', 's1', 'v1', 'c2']
        )
