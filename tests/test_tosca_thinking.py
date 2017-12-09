import unittest

from .test_tosca_base import TestToscaBase


class TestThinking(TestToscaBase):

    def test(self):
        file = 'data/examples/thinking-app/thinking.csar'
        up = self.read_plan(
            'data/examples/thinking-app/thinking.up.plan'
        )
        down = self.read_plan(
            'data/examples/thinking-app/thinking.down.plan'
        )
        self.assert_up_start(file, up)
        self.assert_down(file, down)


if __name__ == '__main__':
    unittest.main()
