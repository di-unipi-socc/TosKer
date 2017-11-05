import unittest

from tosker.orchestrator import Orchestrator

# from tosker import helper


class TestToscaParsing(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self._orchestrator = Orchestrator(
            # log_handler=helper.get_consol_handler()
        )

    def test_no_dag(self):
        self.assertFalse(
            self._orchestrator.orchestrate('tosker/tests/TOSCA/nodag.yaml',
                                           ['create'])
        )

    def test_wrong_type(self):
        self.assertFalse(
            self._orchestrator.orchestrate(
                'tosker/tests/TOSCA/wrong_components.yaml', [])
        )

    def test_wrong_component(self):
        self.assertFalse(
            self._orchestrator.orchestrate(
                'tosker/tests/TOSCA/wordpress.yaml', [], ['no_compent'], {})
        )


if __name__ == '__main__':
    unittest.main()
