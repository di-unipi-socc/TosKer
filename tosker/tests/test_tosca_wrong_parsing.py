import unittest
from tosker.tosca_utility import get_tosca_template


class Test_Software_Link(unittest.TestCase):

    def setUp(self):
        pass

    def test_no_dag(self):
        self.assertRaises(Exception,
                          get_tosca_template,
                          'tosker/tests/TOSCA/nodag.yaml')

    def test_wrong_type(self):
        self.assertRaises(Exception,
                          get_tosca_template,
                          'tosker/tests/TOSCA/wrong_components.yaml')

    def test_wrong_component(self):
        self.assertRaises(Exception,
                          get_tosca_template,
                          'tosker/tests/TOSCA/wordpress.yaml',
                          {},
                          ['no_compent'])

if __name__ == '__main__':
    unittest.main()
