import unittest

from .test_tosca_base import TestOrchestrator


class TestSoftwareLink(TestOrchestrator):

    def setUp(self):
        super(TestSoftwareLink, self).setUp()
        self.file = 'data/examples/software-link/software.yaml'

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()


if __name__ == '__main__':
    unittest.main()
