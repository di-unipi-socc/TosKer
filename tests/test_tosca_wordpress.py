import unittest

from .test_tosca_base import TestToscaBase


class TestWordpress(TestToscaBase):

    def test(self):
        file = 'data/examples/wordpress/wordpress.yaml'
        up = self.read_plan(
            'data/examples/wordpress/wordpress.up.plan'
        )
        down = self.read_plan(
            'data/examples/wordpress/wordpress.down.plan'
        )
        self.assert_up_start(file, up)
        self.assert_down(file, down)


if __name__ == '__main__':
    unittest.main()
