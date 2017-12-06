import unittest

from .test_tosca_base import TestOrchestrator


class TestSoftwareLink(TestOrchestrator):

    def test(self):
        file = 'data/examples/software-link/software-link.yaml'
        up = self.read_plan(
            'data/examples/software-link/software-link.up.plan'
        )
        down = self.read_plan(
            'data/examples/software-link/software-link.down.plan'
        )
        self.assert_up_start(file, up)
        self.assert_down(file, down)


if __name__ == '__main__':
    unittest.main()
