import unittest
from tosker.graph.template import Template
from tosker.graph.nodes import Container, Software, Volume
from tosker.tosca_utility import get_tosca_template


class Test_Graph(unittest.TestCase):

    # TODO: add more test to be sure that the graph is as should

    def test_order(self):
        tpl = get_tosca_template(
            'tosker/tests/TOSCA/software-link/software.yaml')
        for n in tpl.deploy_order:
            print(n)

    def test_components(self):
        tpl = get_tosca_template(
            'tosker/tests/TOSCA/software-link/software.yaml',
            components=['server1'])
        for n in tpl.deploy_order:
            print(n)
