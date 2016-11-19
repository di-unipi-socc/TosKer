import unittest
from tosker.deployer import Deployer
from .test_tosca_base import Test_Deployer


class Test_Csar(Test_Deployer):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.deployer = \
            Deployer('tosker/tests/TOSCA/csar/node-mongo.csar')

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()

if __name__ == '__main__':
    unittest.main()
