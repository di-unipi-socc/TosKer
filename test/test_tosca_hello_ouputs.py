import unittest
from tosca_deployer.deployer import Deployer
from tosca_deployer.docker_engine import Docker_engine
from tosca_deployer.utility import Logger
from .test_tosca_base import Test_Deployer


class Test_Hello_Outputs(Test_Deployer):
    def setUp(self):
        super().setUp()
        self.deployer = Deployer('test/TOSCA/hello-outputs.yaml')

    def test(self):
        self.create()
        self.start()
        # TODO: check outputs

if __name__ == '__main__':
    unittest.main()
