import unittest

# from tosker.graph.template import Template
# from tosker.graph.nodes import Container, Software, Volume
# from tosker.tosca_parser import get_tosca_template


class TestGraph(unittest.TestCase):
    pass
    # TODO: the test must target the orchestrator

    # def _assert_sorting(self, tpl):
    #     running = set()
    #     for c in tpl.nodes:
    #         for r in c.relationships:
    #             self.assertIn(r.to.name, running)
    #         running.add(c.name)

    # def test_deployment_order(self):
    #     tpl = get_tosca_template(
    #         'tosker/tests/TOSCA/software-link/software.yaml')
    #     self._assert_sorting(tpl)
    #
    # def test_components_1(self):
    #     tpl = get_tosca_template(
    #         'tosker/tests/TOSCA/software-link/software.yaml',
    #         components=['server1'])
    #
    #     self._assert_sorting(tpl)
    #     self.assertEqual(len(tpl.nodes), 2)
    #     for c in tpl.nodes:
    #         self.assertIn(c.name, ('server1', 'nodejs1'))
    #
    # def test_components_2(self):
    #     tpl = get_tosca_template(
    #         'tosker/tests/TOSCA/software-link/software.yaml',
    #         components=['server2'])
    #
    #     self._assert_sorting(tpl)
    #     self.assertEqual(len(tpl.nodes), 2)
    #     for c in tpl.nodes:
    #         self.assertIn(c.name, ('server2', 'nodejs2'))
    #
    # def test_components_3(self):
    #     tpl = get_tosca_template(
    #         'tosker/tests/TOSCA/software-link/software.yaml',
    #         components=['server3'])
    #
    #     self._assert_sorting(tpl)
    #     self.assertEqual(len(tpl.nodes), 6)
    #     for c in tpl.nodes:
    #         self.assertIn(c.name, ('server1', 'nodejs1',
    #                                'server2', 'nodejs2',
    #                                'server3', 'nodejs3'))
    #
    # def test_components_1_2(self):
    #     tpl = get_tosca_template(
    #         'tosker/tests/TOSCA/software-link/software.yaml',
    #         components=['server1', 'server2'])
    #
    #     self._assert_sorting(tpl)
    #     self.assertEqual(len(tpl.nodes), 4)
    #     for c in tpl.nodes:
    #         self.assertIn(c.name, ('server1', 'nodejs1',
    #                                'server2', 'nodejs2'))
    #
    # def test_components_1_3(self):
    #     tpl = get_tosca_template(
    #         'tosker/tests/TOSCA/software-link/software.yaml',
    #         components=['server1', 'server3'])
    #     self._assert_sorting(tpl)
    #     self.assertEqual(len(tpl.nodes), 6)
    #     for c in tpl.nodes:
    #         self.assertIn(c.name, ('server1', 'nodejs1',
    #                                'server2', 'nodejs2',
    #                                'server3', 'nodejs3'))
    #
    # def test_components_2_3(self):
    #     tpl = get_tosca_template(
    #         'tosker/tests/TOSCA/software-link/software.yaml',
    #         components=['server2', 'server3'])
    #
    #     self._assert_sorting(tpl)
    #     self.assertEqual(len(tpl.nodes), 6)
    #     for c in tpl.nodes:
    #         self.assertIn(c.name, ('server1', 'nodejs1',
    #                                'server2', 'nodejs2',
    #                                'server3', 'nodejs3'))
    #
    # def test_components_n1(self):
    #     tpl = get_tosca_template(
    #         'tosker/tests/TOSCA/software-link/software.yaml',
    #         components=['nodejs1'])
    #
    #     self._assert_sorting(tpl)
    #     self.assertEqual(len(tpl.nodes), 1)
    #     for c in tpl.nodes:
    #         self.assertIn(c.name, ('nodejs1'))
    #
    # def test_components_n2(self):
    #     tpl = get_tosca_template(
    #         'tosker/tests/TOSCA/software-link/software.yaml',
    #         components=['nodejs2'])
    #
    #     self._assert_sorting(tpl)
    #     self.assertEqual(len(tpl.nodes), 1)
    #     for c in tpl.nodes:
    #         self.assertIn(c.name, ('nodejs2'))
    #
    # def test_components_n3(self):
    #     tpl = get_tosca_template(
    #         'tosker/tests/TOSCA/software-link/software.yaml',
    #         components=['nodejs3'])
    #
    #     self._assert_sorting(tpl)
    #     self.assertEqual(len(tpl.nodes), 1)
    #     for c in tpl.nodes:
    #         self.assertIn(c.name, ('nodejs3'))
