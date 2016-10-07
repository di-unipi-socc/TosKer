import unittest
from tosca_deployer.docker_engine import Docker_engine


class Test_Deployer(unittest.TestCase):
    def setUp(self):
        self.docker = Docker_engine()
        self.docker.remove_all_containers()
        self.docker.remove_all_volumes()

    def create(self):
        self.deployer.create()
        for c in self.deployer._tpl.container_order:
            self.assertIsNotNone(
                self.docker.container_inspect(c.name)
            )

        for c in self.deployer._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.volume_inspect(c.name)
            )

        self._delete_container()

    def start(self):
        self.deployer.start()
        for c in self.deployer._tpl.container_order:
            stat = self.docker.container_inspect(c.name)
            # print('DEBUG: ', stat)
            self.assertIsNotNone(stat)
            self.assertTrue(stat['State']['Running'])

        for c in self.deployer._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.volume_inspect(c.name)
            )

        self.deployer.stop()
        for c in self.deployer._tpl.container_order:
            stat = self.docker.container_inspect(c.name)
            # print('DEBUG: ', stat)
            self.assertIsNotNone(stat)
            self.assertFalse(stat['State']['Running'])

        for c in self.deployer._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.volume_inspect(c.name)
            )

        self._delete_container()

    def _delete_container(self):
        self.deployer.delete()
        for c in self.deployer._tpl.container_order:
            self.assertIsNone(
                self.docker.container_inspect(c.name)
            )

        for c in self.deployer._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.volume_inspect(c.name)
            )
