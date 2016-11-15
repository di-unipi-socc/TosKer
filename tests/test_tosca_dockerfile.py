import unittest
from tosker.deployer import Deployer
from tosker.docker_engine import Docker_engine
from tosker.utility import Logger
from .test_tosca_base import Test_Deployer


class Test_Dockerfile(Test_Deployer):

    def setUp(self):
        super().setUp()
        self.deployer = Deployer('test/TOSCA/dockerfile/hello-dockerfile.yaml')

    def test(self):
        self.create()
        self.start_check_exit()
        self.stop()
        self.start_check_exit()
        self.stop()
        self.delete()

if __name__ == '__main__':
    unittest.main()
