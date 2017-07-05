import unittest
from tosker import helper
from tosker.orchestrator import Orchestrator
from tosker import docker_interface as docker
from tosker.tosca_parser import get_tosca_template


class Test_Orchestrator(unittest.TestCase):

    def setUp(self):
        docker.remove_all_containers()
        docker.remove_all_volumes()
        self.orchestrator = Orchestrator(
            # log_handler=helper.get_consol_handler()
        )

    def get_tpl(self):
        if not hasattr(self, 'tpl'):
            self.tpl = get_tosca_template(self.file)
        return self.tpl

    def create(self):
        self.orchestrator.orchestrate(self.file, ['create'])
        for c in self.get_tpl().containers:
            self.assertIsNotNone(
                docker.inspect_container(c)
            )

        for c in self.get_tpl().volumes:
            self.assertIsNotNone(
                docker.inspect_volume(c)
            )

    def start(self):
        self._start(check=lambda x: x['State']['Running'])

    def start_check_exit(self):
        self._start(check=lambda x: x['State']['ExitCode'] == 0)

    def _start(self, check):
        self.orchestrator.orchestrate(self.file, ['start'])
        for c in self.get_tpl().containers:
            stat = docker.inspect_containers(c)
            # print('DEBUG: ', stat)
            self.assertIsNotNone(stat)
            self.assertTrue(check(stat))

        for c in self.get_tpl().volumes:
            self.assertIsNotNone(
                docker.inspect_volume(c)
            )

    def stop(self):
        self.orchestrator.orchestrate(self.file, ['stop'])
        for c in self.get_tpl().containers:
            stat = docker.inspect_containers(c)
            # print('DEBUG: ', stat)
            self.assertIsNotNone(stat)
            self.assertFalse(stat['State']['Running'])

        for c in self.get_tpl().volumes:
            self.assertIsNotNone(
                docker.inspect_volume(c)
            )

    def delete(self):
        self.orchestrator.orchestrate(self.file, ['delete'])
        for c in self.get_tpl().containers:
            self.assertIsNone(
                docker.inspect_container(c)
            )

        for c in self.get_tpl().volumes:
            self.assertIsNotNone(
                docker.inspect_volume(c)
            )
