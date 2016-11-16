import unittest
from tosker.deployer import Deployer
from tosker.docker_engine import Docker_engine
from tosker.utility import Logger
from .test_tosca_base import Test_Deployer
import logging


class Test_Node_Mongo_Single_Server(Test_Deployer):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.deployer = \
            Deployer('tests/TOSCA/node-mongo/node-mongo-single-server.yaml')

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()

if __name__ == '__main__':
    unittest.main()
