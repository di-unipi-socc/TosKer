import unittest

from six import StringIO
from tosker import docker_interface as docker
from tosker.orchestrator import Orchestrator

from .test_tosca_base import TestToscaBase


class TestNcServer(TestToscaBase):

    def setUp(self):
        super(TestNcServer, self).setUp()
        with self.redirect_stdout(StringIO()):
            self.o = Orchestrator(quiet=False)


    def test_dockerfile(self):
        file = 'data/examples/nc-server/nc-dockerfile.yaml'
        up_plan = self.read_plan(
            'data/examples/nc-server/nc-dockerfile.up.plan'
        )
        down_plan = self.read_plan(
            'data/examples/nc-server/nc-dockerfile.down.plan'
        )
        tpl = self.get_tpl(file)

        temp_stdout = StringIO()
        with self.redirect_stdout(temp_stdout):
            self.assertTrue(
                self.o.orchestrate(file, up_plan)
            )
        self.assert_create(tpl)
        self.assert_start(tpl)

        con_id = docker.inspect_container('tosker_nc-dockerfile.server')['Id']
        output = temp_stdout.getvalue().strip()
        self.assertIn('- container_id: {}'.format(con_id), output)
        self.assertIn('- env_variable: hello_world', output)

        with self.redirect_stdout(StringIO()):
            self.assertTrue(
                self.o.orchestrate(file, down_plan)
            )
        self.assert_delete(tpl)

    def test_image(self):
        file = 'data/examples/nc-server/nc-image.yaml'
        up_plan = self.read_plan(
            'data/examples/nc-server/nc-image.up.plan'
        )
        down_plan = self.read_plan(
            'data/examples/nc-server/nc-image.down.plan'
        )
        tpl = self.get_tpl(file)
        
        temp_stdout = StringIO()
        with self.redirect_stdout(temp_stdout):
            self.assertTrue(
                self.o.orchestrate(file, up_plan)
            )
        self.assert_create(tpl)
        self.assert_start(tpl)

        con_id = docker.inspect_container('tosker_nc-image.server')['Id']
        output = temp_stdout.getvalue().strip()
        self.assertIn('- container_id: {}'.format(con_id), output)
        self.assertIn('- env_variable: hello_world', output)

        with self.redirect_stdout(StringIO()):
            self.assertTrue(
                self.o.orchestrate(file, down_plan)
            )
        self.assert_delete(tpl)


if __name__ == '__main__':
    unittest.main()
