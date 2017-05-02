import unittest
from tosker.orchestrator import Orchestrator
from .test_tosca_base import Test_Orchestrator

import contextlib
from io import StringIO


class Test_Hello(Test_Orchestrator):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.orchestrator = Orchestrator(quiet=False)
        self.orchestrator.parse('tosker/tests/TOSCA/hello.yaml')

    def test(self):
        self.create()
        self.start_check_exit()
        self.stop()
        self.orchestrator.parse('tosker/tests/TOSCA/hello.yaml')
        self.start_check_exit()
        self.stop()
        con_id = self._docker.inspect_container('hello_container')['Id']
        self.delete()

        # verify output
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            self.orchestrator.print_outputs()
        output = temp_stdout.getvalue().strip()

        verified = '''OUTPUTS:
  - container_id: {}
  - env_variable: Luca'''.format(con_id)
        self.assertTrue(output.endswith(verified))


if __name__ == '__main__':
    unittest.main()
