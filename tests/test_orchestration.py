import unittest

from tosker.orchestrator import Orchestrator

# from tosker import helper


class TestToscaParsing(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self._orchestrator = Orchestrator(
            # log_handler=helper.get_consol_handler()
        )

    def test_wrong_type(self):
        self.assertFalse(
            self._orchestrator.orchestrate(
                'data/examples/wrong_components.yaml', [])
        )

if __name__ == '__main__':
    unittest.main()
