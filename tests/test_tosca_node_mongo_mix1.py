import unittest

from .test_tosca_base import TestOrchestrator


class TestNodeMongoMix1(TestOrchestrator):

    def setUp(self):
        super(TestNodeMongoMix1, self).setUp()
        self.file = 'data/examples/node-mongo/node-mongo-mix1.yaml'

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()


if __name__ == '__main__':
    unittest.main()
