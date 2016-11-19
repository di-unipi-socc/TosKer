import unittest
from tosker.deployer import Deployer
from .test_tosca_base import Test_Deployer


class Test_Node_Mongo_Mix2(Test_Deployer):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.deployer = \
            Deployer('tosker/tests/TOSCA/node-mongo/node-mongo-mix2.yaml')

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()

if __name__ == '__main__':
    unittest.main()
