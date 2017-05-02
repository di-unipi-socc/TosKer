import unittest
from tosker.orchestrator import Orchestrator
from .test_tosca_base import Test_Orchestrator


class Test_Thoughts(Test_Orchestrator):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.orchestrator._parse(
            'tosker/tests/TOSCA/thoughts-app/thoughts.csar')

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()


if __name__ == '__main__':
    unittest.main()
