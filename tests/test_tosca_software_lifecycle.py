import unittest

from .test_tosca_base import TestOrchestrator


class TestSoftwareLinkcycle(TestOrchestrator):

    def setUp(self):
        super(TestSoftwareLinkcycle, self).setUp()
        self.file = 'data/examples/software-lifecycle/lifecycle.yaml'

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()


if __name__ == '__main__':
    unittest.main()
