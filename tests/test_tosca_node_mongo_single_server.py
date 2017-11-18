import unittest

from .test_tosca_base import TestOrchestrator


class TestNodeMongoSingleServer(TestOrchestrator):

    def setUp(self):
        super(TestNodeMongoSingleServer, self).setUp()
        self.file = 'data/examples/node-mongo/node-mongo-single-server.yaml'

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()


if __name__ == '__main__':
    unittest.main()
