import unittest
from tosker.docker_interface import Docker_interface


class Test_Orchestrator(unittest.TestCase):

    def setUp(self):
        self.docker = Docker_interface()
        self.docker.remove_all_containers()
        self.docker.remove_all_volumes()

    def create(self):
        self.orchestrator.create()
        for c in self.orchestrator._tpl.container_order:
            self.assertIsNotNone(
                self.docker.inspect(c.name)
            )

        for c in self.orchestrator._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.inspect(c.name)
            )

    def start(self):
        self._start(check=lambda x: x['State']['Running'])

    def start_check_exit(self):
        self._start(check=lambda x: x['State']['ExitCode'] == 0)

    def _start(self, check):
        self.orchestrator.start()
        for c in self.orchestrator._tpl.container_order:
            stat = self.docker.inspect(c.name)
            # print('DEBUG: ', stat)
            self.assertIsNotNone(stat)
            self.assertTrue(check(stat))

        for c in self.orchestrator._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.inspect(c.name)
            )

    def stop(self):
        self.orchestrator.stop()
        for c in self.orchestrator._tpl.container_order:
            stat = self.docker.inspect(c.name)
            # print('DEBUG: ', stat)
            self.assertIsNotNone(stat)
            self.assertFalse(stat['State']['Running'])

        for c in self.orchestrator._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.inspect(c.name)
            )

    def delete(self):
        self.orchestrator.delete()
        for c in self.orchestrator._tpl.container_order:
            self.assertIsNone(
                self.docker.inspect(c.name)
            )

        for c in self.orchestrator._tpl.volume_order:
            self.assertIsNotNone(
                self.docker.inspect(c.name)
            )
