import unittest
from tosker.deployer import Deployer
from .test_tosca_base import Test_Deployer


class Test_Dockerfile(Test_Deployer):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.deployer = Deployer('tosker/tests/TOSCA/dockerfile/hello-dockerfile.yaml')

    def test(self):
        self.create()
        self.start_check_exit()
        self.stop()
        self.start_check_exit()
        self.stop()
        self.delete()

if __name__ == '__main__':
    unittest.main()
