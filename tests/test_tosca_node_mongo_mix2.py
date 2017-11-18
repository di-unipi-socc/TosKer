import unittest

from .test_tosca_base import TestOrchestrator


class TestNodeMongoMix2(TestOrchestrator):

    def setUp(self):
        super(TestNodeMongoMix2, self).setUp()
        self.file = 'data/examples/node-mongo/node-mongo-mix2.yaml'

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()


if __name__ == '__main__':
    unittest.main()
