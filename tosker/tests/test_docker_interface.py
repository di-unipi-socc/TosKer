import unittest
from tosker import helper
from tosker.docker_interface import Docker_interface
from tosker.graph.nodes import Container
from tosker.graph.artifacts import DockerImageExecutable
from tosker.helper import Logger


class Test_DockerInterface(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Logger.set(helper.get_consol_handler(), False)
        self._docker = Docker_interface(repo='test_repo',
                                        net_name='test_net',
                                        tmp_dir='/tmp/tosker_tests')
        self._docker.create_network()
        self._docker.remove_all_containers()

        self._container = Container('test_container')
        self._container.image = DockerImageExecutable('alpine')
        self._container.cmd = 'ping 127.0.0.1'

    def setUp(self):
        pass

    def tearDown(self):
        self._docker.remove_all_containers()

    def test_create_container(self):
        self._docker.create_container(self._container, force=False)
        self.assertIsNotNone(
            self._docker.inspect(self._container.name)
        )
        self.assertRaises(
            Exception,
            lambda: self._docker.create_container(self._container, force=False)
        )
        self.assertIsNotNone(
            self._docker.inspect(self._container.name)
        )

    def test_start_container(self):
        self._docker.create_container(self._container)
        self.assertIsNotNone(
            self._docker.inspect(self._container.name)
        )
        self._docker.start_container(self._container)
        stat = self._docker.inspect_container(self._container.name)
        self.assertIsNotNone(stat)
        self.assertTrue(stat['State']['Running'])

    def test_start_container_error(self):
        self.assertRaises(
            Exception,
            lambda: self._docker.start_container(self._container)
        )
        self.assertIsNone(
            self._docker.inspect_container(self._container.name)
        )

    def test_stop_container(self):
        self._docker.create_container(self._container)
        self.assertIsNotNone(
            self._docker.inspect(self._container.name)
        )
        self._docker.start_container(self._container)

        stat = self._docker.inspect_container(self._container.name)
        self.assertIsNotNone(stat)
        self.assertTrue(stat['State']['Running'])

        self._docker.stop_container(self._container)
        stat = self._docker.inspect_container(self._container.name)
        self.assertIsNotNone(stat)
        self.assertFalse(stat['State']['Running'])

    def test_stop_container_error(self):
        self.assertRaises(
            Exception,
            lambda: self._docker.stop_container(self._container)
        )
        self.assertIsNone(
            self._docker.inspect_container(self._container.name)
        )

    def test_container_delete(self):
        self._docker.create_container(self._container)
        self.assertIsNotNone(
            self._docker.inspect(self._container.name)
        )

        self._docker.delete_container(self._container)
        self.assertIsNone(
            self._docker.inspect(self._container.name)
        )

    def test_container_delete_error(self):
        self.assertRaises(
            Exception,
            lambda: self._docker.delete_container(self._container)
        )
        self.assertIsNone(
            self._docker.inspect(self._container.name)
        )

    def test_container_exec(self):
        self._docker.create_container(self._container)
        self.assertIsNotNone(
            self._docker.inspect(self._container.name)
        )
        self._docker.start_container(self._container)
        self._docker.exec_cmd(self._container, 'echo hello!')

    def test_container_exec_error(self):
        self._docker.create_container(self._container)
        self.assertIsNotNone(
            self._docker.inspect(self._container.name)
        )
        self.assertRaises(
            Exception,
            lambda: self._docker.exec_cmd(self._container, 'echo hello!')
        )
        self._docker.delete_container(self._container)
        self.assertIsNone(
            self._docker.inspect(self._container.name)
        )
        self.assertRaises(
            Exception,
            lambda: self._docker.exec_cmd(self._container, 'echo hello!')
        )

    def test_network(self):
        self._docker.delete_network()
        self._docker.delete_network()
        # TODO: assert that the network is correctlly created
        self._docker.create_network()
        self._docker.create_network()
