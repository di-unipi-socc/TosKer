import unittest
from tosker.deployer import Deployer
from .test_tosca_base import Test_Deployer


class Test_Hello(Test_Deployer):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.deployer = Deployer('tosker/tests/TOSCA/hello.yaml')

    def test(self):
        self.create()
        self.start_check_exit()
        self.stop()
        self.start_check_exit()
        self.stop()
        self.delete()
        # TODO: check outputs

if __name__ == '__main__':
    unittest.main()
