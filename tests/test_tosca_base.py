import sys
import os
from unittest import TestCase
from contextlib import contextmanager

from tosker import docker_interface as docker
# from tosker import helper
from tosker.orchestrator import Orchestrator
from tosker.storage import Memory
from tosker.tosca_parser import get_tosca_template


class TestToscaBase(TestCase):
    @staticmethod
    def setUpClass():
        pass

    def setUp(self):
        self.o = Orchestrator(
            # log_handler=helper.get_consol_handler()
        )
        self.o.prune()

    def get_tpl(self, file):
        self.assertTrue(os.path.isfile(file))
        tpl = get_tosca_template(file)
        self.assertIsNotNone(tpl)
        return tpl

    def read_plan(self, file):
        self.assertTrue(os.path.isfile(file))
        with open(file, 'r') as plan:
            plan_list = [l.strip() for l in plan.readlines() if l.strip()]
            self.assertTrue(plan_list)
            return plan_list

    def assert_create(self, tpl):
        for c in tpl.containers:
            self.assertIsNotNone(
                docker.inspect_container(c)
            )

        for c in tpl.volumes:
            self.assertIsNotNone(
                docker.inspect_volume(c)
            )

    def assert_start(self, tpl):
        self._assert_start(tpl, check=lambda x: x['State']['Running'])

    def assert_exit(self, tpl):
        self._assert_start(tpl, check=lambda x: x['State']['ExitCode'] == 0)

    def _assert_start(self, tpl, check):
        for c in tpl.containers:
            stat = docker.inspect_container(c)
            self.assertIsNotNone(stat)
            self.assertTrue(check(stat))

    # def assert_stop(self, file):
    #     for c in self.get_tpl(file).containers:
    #         stat = docker.inspect_container(c)
    #         self.assertIsNotNone(stat)
    #         self.assertFalse(stat['State']['Running'])

    #     for c in self.get_tpl().volumes:
    #         self.assertIsNotNone(
    #             docker.inspect_volume(c)
    #         )

    def assert_delete(self, tpl):
        for c in tpl.containers:
            self.assertIsNone(
                docker.inspect_container(c)
            )

        for c in tpl.volumes:
            self.assertIsNotNone(
                docker.inspect_volume(c)
            )

    def assert_up_start(self, file, up):
        tpl = self.get_tpl(file)
        self.assertTrue(
            self.o.orchestrate(file, up)
        )
        self.assert_create(tpl)
        self.assert_start(tpl)


    def assert_up_exit(self, file, up):
        tpl = self.get_tpl(file)
        self.assertTrue(
            self.o.orchestrate(file, up)
        )
        self.assert_create(tpl)
        self.assert_exit(tpl)

    def assert_down(self, file, down):
        tpl = self.get_tpl(file)
        self.assertTrue(
            self.o.orchestrate(file, down)
        )
        self.assert_delete(tpl)

    @contextmanager
    def redirect_stdout(self, new_target):
        old_target, sys.stdout = sys.stdout, new_target  # replace sys.stdout
        try:
            yield new_target  # run some code with the replaced stdout
        finally:
            sys.stdout = old_target  # restore to the previous value
