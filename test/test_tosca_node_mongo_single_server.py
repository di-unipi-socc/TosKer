import unittest
from tosca_deployer.deployer import Deployer
from tosca_deployer.docker_engine import Docker_engine
from tosca_deployer.utility import Logger
from .test_tosca_base import Test_Deployer
import logging


class Test_Node_Mongo_Single_Server(Test_Deployer):

    def setUp(self):
        super().setUp()
        self.deployer = \
            Deployer('test/TOSCA/node-mongo/node-mongo-single-server.yaml')

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()

if __name__ == '__main__':
    unittest.main()
