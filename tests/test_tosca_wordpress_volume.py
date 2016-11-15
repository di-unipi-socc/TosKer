import unittest
from tosker.deployer import Deployer
from tosker.docker_engine import Docker_engine
from tosker.utility import Logger
from .test_tosca_base import Test_Deployer


class Test_Wordpress_Volume(Test_Deployer):

    def setUp(self):
        super().setUp()
        self.deployer = Deployer('test/TOSCA/wordpress-volume.yaml')

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()

if __name__ == '__main__':
    unittest.main()
