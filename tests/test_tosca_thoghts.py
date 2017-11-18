import unittest

from .test_tosca_base import TestOrchestrator


class TestThoughts(TestOrchestrator):

    def setUp(self):
        super(TestThoughts, self).setUp()
        self.file = 'data/examples/thoughts-app/thoughts.csar'

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()


if __name__ == '__main__':
    unittest.main()
