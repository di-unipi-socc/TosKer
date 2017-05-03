import unittest
from tosker import helper
from tosker.orchestrator import Orchestrator
from tosker.docker_interface import Docker_interface


class Test_Orchestrator(unittest.TestCase):

    def setUp(self):
        self._docker = Docker_interface()
        self._docker.remove_all_containers()
        self._docker.remove_all_volumes()
        self.orchestrator = Orchestrator(
            # log_handler=helper.get_consol_handler()
        )

    def create(self):
        self.orchestrator._create()
        for c in self.orchestrator._tpl.container_order:
            self.assertIsNotNone(
                self._docker.inspect(c.name)
            )

        for c in self.orchestrator._tpl.volume_order:
            self.assertIsNotNone(
                self._docker.inspect(c.name)
            )

    def start(self):
        self._start(check=lambda x: x['State']['Running'])

    def start_check_exit(self):
        self._start(check=lambda x: x['State']['ExitCode'] == 0)

    def _start(self, check):
        self.orchestrator._start()
        for c in self.orchestrator._tpl.container_order:
            stat = self._docker.inspect_container(c.name)
            # print('DEBUG: ', stat)
            self.assertIsNotNone(stat)
            self.assertTrue(check(stat))

        for c in self.orchestrator._tpl.volume_order:
            self.assertIsNotNone(
                self._docker.inspect_volume(c.name)
            )

    def stop(self):
        self.orchestrator._stop()
        for c in self.orchestrator._tpl.container_order:
            stat = self._docker.inspect_container(c.name)
            # print('DEBUG: ', stat)
            self.assertIsNotNone(stat)
            self.assertFalse(stat['State']['Running'])

        for c in self.orchestrator._tpl.volume_order:
            self.assertIsNotNone(
                self._docker.inspect_volume(c.name)
            )

    def delete(self):
        self.orchestrator._delete()
        for c in self.orchestrator._tpl.container_order:
            self.assertIsNone(
                self._docker.inspect(c.name)
            )

        for c in self.orchestrator._tpl.volume_order:
            self.assertIsNotNone(
                self._docker.inspect(c.name)
            )
