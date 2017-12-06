import unittest

from .test_tosca_base import TestToscaBase


class TestNodeMongo(TestToscaBase):

    def test_csar(self):
        file = 'data/examples/node-mongo-csar/node-mongo.csar'
        up = self.read_plan(
            'data/examples/node-mongo-csar/node-mongo.up.plan'
        )
        down = self.read_plan(
            'data/examples/node-mongo-csar/node-mongo.down.plan'
        )
        self.assert_up_start(file, up)
        self.assert_down(file, down)

    def test_mix1(self):
        file = 'data/examples/node-mongo/node-mongo-mix1.yaml'
        up = self.read_plan(
            'data/examples/node-mongo/node-mongo-mix1.up.plan'
        )
        down = self.read_plan(
            'data/examples/node-mongo/node-mongo-mix1.down.plan'
        )
        self.assert_up_start(file, up)
        self.assert_down(file, down)

    def test_mix2(self):
        file = 'data/examples/node-mongo/node-mongo-mix2.yaml'
        up = self.read_plan(
            'data/examples/node-mongo/node-mongo-mix2.up.plan'
        )
        down = self.read_plan(
            'data/examples/node-mongo/node-mongo-mix2.down.plan'
        )
        self.assert_up_start(file, up)
        self.assert_down(file, down)
    
    def test_single_server(self):
        file = 'data/examples/node-mongo/node-mongo-single-server.yaml'
        up = self.read_plan(
            'data/examples/node-mongo/node-mongo-single-server.up.plan'
        )
        down = self.read_plan(
            'data/examples/node-mongo/node-mongo-single-server.down.plan'
        )
        self.assert_up_start(file, up)
        self.assert_down(file, down)
    
    def test_custom(self):
        file = 'data/examples/node-mongo/node-mongo-custom.yaml'
        up = self.read_plan(
            'data/examples/node-mongo/node-mongo-custom.up.plan'
        )
        down = self.read_plan(
            'data/examples/node-mongo/node-mongo-custom.down.plan'
        )
        self.assert_up_start(file, up)
        self.assert_down(file, down)

if __name__ == '__main__':
    unittest.main()
