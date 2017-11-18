import unittest

from .test_tosca_base import TestOrchestrator


class TestNodeMongo(TestOrchestrator):

    def setUp(self):
        super(TestNodeMongo, self).setUp()
        self.file = 'data/examples/node-mongo-csar/node-mongo.csar'

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()


if __name__ == '__main__':
    unittest.main()
