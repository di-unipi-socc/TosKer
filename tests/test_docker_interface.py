import unittest

from tosker import docker_interface as docker
from tosker.graph.artifacts import DockerImageExecutable
from tosker.graph.nodes import Container
from tosker.graph.template import Template

# from tosker.helper import Logger


class TestDockerInterface(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Logger.set(helper.get_consol_handler(), False)
        docker.remove_all_containers()

        self._container = Container('test_container')
        self._container.image = DockerImageExecutable('alpine')
        self._container.cmd = 'ping 127.0.0.1'
        tpl = Template('test_app')
        tpl.tmp_dir = '/tmp/tosker_tests'
        self._container.tpl = tpl

        docker.create_network(self._container)

    @classmethod
    def tearDownClass(self):
        docker.delete_network(self._container)

    def setUp(self):
        pass

    def tearDown(self):
        docker.remove_all_containers()

    def test_create_container(self):
        docker.create_container(self._container, force=False)
        self.assertIsNotNone(
            docker.inspect_container(self._container)
        )
        self.assertRaises(
            Exception,
            lambda: docker.create_container(self._container, force=False)
        )
        self.assertIsNotNone(
            docker.inspect_container(self._container)
        )

    def test_start_container(self):
        docker.create_container(self._container)
        self.assertIsNotNone(
            docker.inspect_container(self._container)
        )
        docker.start_container(self._container)
        stat = docker.inspect_container(self._container)
        self.assertIsNotNone(stat)
        self.assertTrue(stat['State']['Running'])

    def test_start_container_error(self):
        self.assertRaises(
            Exception,
            lambda: docker.start_container(self._container)
        )
        self.assertIsNone(
            docker.inspect_container(self._container)
        )

    def test_stop_container(self):
        docker.create_container(self._container)
        self.assertIsNotNone(
            docker.inspect_container(self._container)
        )
        docker.start_container(self._container)

        stat = docker.inspect_container(self._container)
        self.assertIsNotNone(stat)
        self.assertTrue(stat['State']['Running'])

        docker.stop_container(self._container)
        stat = docker.inspect_container(self._container)
        self.assertIsNotNone(stat)
        self.assertFalse(stat['State']['Running'])

    def test_stop_container_error(self):
        self.assertRaises(
            Exception,
            lambda: docker.stop_container(self._container)
        )
        self.assertIsNone(
            docker.inspect_container(self._container)
        )

    def test_container_delete(self):
        docker.create_container(self._container)
        self.assertIsNotNone(
            docker.inspect_container(self._container)
        )

        docker.delete_container(self._container)
        self.assertIsNone(
            docker.inspect_container(self._container)
        )

    def test_container_delete_error(self):
        self.assertRaises(
            Exception,
            lambda: docker.delete_container(self._container)
        )
        self.assertIsNone(
            docker.inspect_container(self._container)
        )

    def test_container_exec(self):
        docker.create_container(self._container)
        self.assertIsNotNone(
            docker.inspect_container(self._container)
        )
        docker.start_container(self._container)
        docker.exec_cmd(self._container, 'echo hello!')

    def test_container_exec_error(self):
        docker.create_container(self._container)
        self.assertIsNotNone(
            docker.inspect_container(self._container)
        )
        self.assertRaises(
            Exception,
            lambda: docker.exec_cmd(self._container, 'echo hello!')
        )
        docker.delete_container(self._container)
        self.assertIsNone(
            docker.inspect_container(self._container)
        )
        self.assertRaises(
            Exception,
            lambda: docker.exec_cmd(self._container, 'echo hello!')
        )

    # def test_network(self):
    #     docker.delete_network()
    #     docker.delete_network()
    #     # TODO: assert that the network is correctlly created
    #     docker.create_network()
    #     docker.create_network()
