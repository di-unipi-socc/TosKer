import unittest
import os
import logging
from tosca_deployer.deployer import Deployer
from tosca_deployer.docker_engine import Docker_engine
from tosca_deployer.utility import Logger


class Test_Deploy(unittest.TestCase):

    def setUp(self):
        self.docker = Docker_engine()
        self.docker.remove_all_containers()
        self.docker.remove_all_volumes()

    def test_TOSCA_files(self):
        for dirName, subdirList, fileList in os.walk('TOSCA/docker'):
            # print('Found directory: %s' % dirName)
            for fname in fileList:
                if '.yaml' in fname:
                    # print('\t%s' % fname)
                    path = os.path.join(dirName, fname)
                    self._create(path)
                    self._start(path)

    def _create(self, tosca):
        deployer = Deployer(tosca)
        # Logger.main_level = logging.ERROR
        deployer.create()
        for c in deployer._tpl.container_order:
            self.assertIsNotNone(
                self.docker.container_inspect(c.name)
            )

        for c in deployer._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.volume_inspect(c.name)
            )

        self._delete_container(deployer)

    def _start(self, tosca):
        deployer = Deployer(tosca)
        deployer.start()
        for c in deployer._tpl.container_order:
            stat = self.docker.container_inspect(c.name)
            # print('DEBUG: ', stat)
            self.assertIsNotNone(stat)
            self.assertTrue(stat['State']['Running'])

        for c in deployer._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.volume_inspect(c.name)
            )

        deployer.stop()
        for c in deployer._tpl.container_order:
            stat = self.docker.container_inspect(c.name)
            # print('DEBUG: ', stat)
            self.assertIsNotNone(stat)
            self.assertFalse(stat['State']['Running'])

        for c in deployer._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.volume_inspect(c.name)
            )

        self._delete_container(deployer)

    def _delete_container(self, deployer):
        deployer.delete()
        for c in deployer._tpl.container_order:
            self.assertIsNone(
                self.docker.container_inspect(c.name)
            )

        for c in deployer._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.volume_inspect(c.name)
            )

if __name__ == '__main__':
    unittest.main()
