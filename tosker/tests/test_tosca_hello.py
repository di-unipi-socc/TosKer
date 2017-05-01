import unittest
from tosker.orchestrator import Orchestrator
from .test_tosca_base import Test_Orchestrator

import contextlib
from io import StringIO


class Test_Hello(Test_Orchestrator):

    def setUp(self):
        super(self.__class__, self).setUp()
        # self.orchestrator = Orchestrator(quiet=False)
        self.orchestrator.parse('tosker/tests/TOSCA/hello.yaml')

    def test(self):
        self.create()
        self.start_check_exit()
        self.stop()
        self.start_check_exit()
        self.stop()
        self.delete()

        # temp_stdout = StringIO()
        # with contextlib.redirect_stdout(temp_stdout):
        #     self.orchestrator.print_outputs()
        # output = temp_stdout.getvalue().strip()
        #
        # print(output)
        # self.assertTrue(
        #     output.endswith('''
        #     - env_variable: Luca'''))

if __name__ == '__main__':
    unittest.main()
