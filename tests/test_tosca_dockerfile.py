import unittest

from .test_tosca_base import TestOrchestrator


class TestDockerfile(TestOrchestrator):

    def setUp(self):
        super(TestDockerfile, self).setUp()
        self.file = 'data/examples/dockerfile/hello-dockerfile.yaml'

    def test(self):
        self.create()
        self.start_check_exit()
        self.stop()
        self.start_check_exit()
        self.stop()
        self.delete()


if __name__ == '__main__':
    unittest.main()
