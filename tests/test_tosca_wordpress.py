import unittest

from .test_tosca_base import Test_Orchestrator


class Test_Wordpress(Test_Orchestrator):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.file = 'data/examples/wordpress.yaml'
        self.inputs = {'wp_host_port': 9000}

    def test(self):
        self.create()
        self.start()
        self.stop()
        self.start()
        self.stop()
        self.delete()


if __name__ == '__main__':
    unittest.main()
