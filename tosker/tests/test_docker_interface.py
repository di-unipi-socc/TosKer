import unittest
from tosker.docker_interface import Docker_interface
from tosker.graph.nodes import Container
from tosker.graph.artifacts import DockerImageExecutable


class Test_DockerInterface(unittest.TestCase):

    def setUp(self):
        self._docker = Docker_interface(repo='test_repo',
                                        net_name='test_net',
                                        tmp_dir='/tmp/tosker_tests')
        self._container = Container('test_container')
        self._container.image = DockerImageExecutable('alpine')
        self._container.cmd = 'ping 127.0.0.1'

    def test_create_container(self):
        self._docker.create_container(self._container)
        self.assertIsNotNone(
            self._docker.inspect(c.name)
        )
        self._docker.create_container(self._container)
        self.assertIsNotNone(
            self._docker.inspect(c.name)
        )

    # def test_start_container(self):
    #     self._docker.create_container(self._container)
    #     self.assertIsNotNone(
    #         self._docker.inspect(self._container.name)
    #     )
    #     self.assertTrue(
    #         self._docker.start_container(self._container)
    #     )
    #     stat = self._docker.inspect_container(self._container.name)
    #     self.assertIsNotNone(stat)
    #     self.assertTrue(stat['State']['Running'])
    #
    #     # check ERROR
    #     self._docker.delete_container(self._container)
    #     res = self._docker.start_container(self._container)
    #     self.assertFalse(res)
    #     stat = self._docker.inspect_container(self._container.name)
    #     self.assertIsNone(stat)
    #
    # def test_stop_container(self):
    #     self._docker.create_container(self._container)
    #     self.assertIsNotNone(
    #         self._docker.inspect(self._container.name)
    #     )
    #     self.assertTrue(
    #         self._docker.start_container(self._container)
    #     )
    #     stat = self._docker.inspect_container(self._container.name)
    #     self.assertIsNotNone(stat)
    #     self.assertTrue(stat['State']['Running'])
    #
    #     res = self._docker.stop_container(self._container)
    #     self.assertTrue(res)
    #     stat = self._docker.inspect_container(self._container.name)
    #     self.assertIsNotNone(stat)
    #     self.assertFalse(stat['State']['Running'])
    #
    #     # check ERROR
    #     self._docker.delete_container(self._container)
    #     res = self._docker.stop_container(self._container)
    #     self.assertFalse(res)
    #     stat = self._docker.inspect_container(self._container.name)
    #     self.assertIsNone(stat)
    #
    # def test_container_delete(self):
    #     self._docker.create_container(self._container)
    #     self.assertIsNotNone(
    #         self._docker.inspect(self._container.name)
    #     )
    #
    #     self.assertTrue(
    #         self._docker.delete_container(self._container)
    #     )
    #     self.assertNone(
    #         self._docker.inspect(self._container.name)
    #     )
    #
    #     # # check ERROR
    #     # self.assertFalse(
    #     #     self._docker.delete_container(self._container)
    #     # )
    #     # self.assertNone(
    #     #     self._docker.inspect(self._container.name)
    #     # )
    #
    # def test_container_exec(self):
    #     self._docker.create_container(self._container)
    #     self.assertIsNotNone(
    #         self._docker.inspect(self._container.name)
    #     )
    #     self.assertTrue(
    #         self._docker.start_container(self._container)
    #     )
    #     self.assertTrue(
    #         self._docker.exec_cmd(self._container, 'echo hello!')
    #     )
    #
    #     # check ERROR
    #     self.assertTrue(
    #         self._docker.stop_container(self._container)
    #     )
    #     self.assertIsNotNone(
    #         self._docker.inspect(self._container.name)
    #     )
    #     self.assertFalse(
    #         self._docker.exec_cmd(self._container, 'echo hello!')
    #     )
    #     self.assertTrue(
    #         self._docker.delete_container(self._container)
    #     )
    #     self.assertIsNone(
    #         self._docker.inspect(self._container.name)
    #     )
    #     self.assertFalse(
    #         self._docker.exec_cmd(self._container, 'echo hello!')
    #    )

    # def test_network(self):
    #     self._docker.create_network()
    #     self._docker.create_network()
    #     # TODO: assert that the network is correctlly created
    #     self._docker.delete_network()
    #     self._docker.delete_network()
