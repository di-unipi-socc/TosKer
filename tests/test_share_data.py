import sys
import unittest
from contextlib import contextmanager

from six import StringIO

from tosker import docker_interface as docker
from tosker.orchestrator import Orchestrator

from .test_tosca_base import Test_Orchestrator


class Test_Hello(Test_Orchestrator):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.file = 'data/examples/container_share_data.yaml'

    def test(self):
        self.create()
        self.start_check_exit()
        self.stop()
        self.start_check_exit()

        with open('/tmp/test_share_tosker.log') as f:
            string = f.read()
            self.assertEqual(string, '123hello123\n')

if __name__ == '__main__':
    unittest.main()
