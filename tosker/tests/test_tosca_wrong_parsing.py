import unittest
from tosker.orchestrator import Orchestrator


class Test_Software_Link(unittest.TestCase):

    def setUp(self):
        self._orchestrator = Orchestrator()

    def test_no_dag(self):
        self.assertFalse(
            self._orchestrator.parse('tosker/tests/TOSCA/nodag.yaml')
        )

    def test_wrong_type(self):
        self.assertFalse(
            self._orchestrator.parse(
                'tosker/tests/TOSCA/wrong_components.yaml')
        )

    def test_wrong_component(self):
        self.assertFalse(
            self._orchestrator.parse(
                'tosker/tests/TOSCA/wordpress.yaml', {}, ['no_compent'])
        )


if __name__ == '__main__':
    unittest.main()
