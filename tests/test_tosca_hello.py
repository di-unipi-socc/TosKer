import sys
import unittest
from contextlib import contextmanager

from six import StringIO

from tosker import docker_interface as docker
from tosker.orchestrator import Orchestrator

from .test_tosca_base import TestOrchestrator


@contextmanager
def redirect_stdout(new_target):
    old_target, sys.stdout = sys.stdout, new_target  # replace sys.stdout
    try:
        yield new_target  # run some code with the replaced stdout
    finally:
        sys.stdout = old_target  # restore to the previous value


class TestHello(TestOrchestrator):

    def setUp(self):
        super(TestHello, self).setUp()
        with redirect_stdout(StringIO()):
            self.orchestrator = Orchestrator(quiet=False)
        self.file = 'data/examples/hello.yaml'

    def test(self):
        with redirect_stdout(StringIO()):
            self.create()
            self.start_check_exit()
            self.stop()
            self.start_check_exit()

        # verify output
        temp_stdout = StringIO()
        with redirect_stdout(temp_stdout):
            self.stop()

        con_id = docker.inspect_container('tosker_hello.hello_container')['Id']

        output = temp_stdout.getvalue().strip()
        self.assertIn('- container_id: {}'.format(con_id), output)
        self.assertIn('- env_variable: Luca', output)

        with redirect_stdout(StringIO()):
            self.delete()


if __name__ == '__main__':
    unittest.main()
