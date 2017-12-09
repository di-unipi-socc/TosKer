import unittest

from .test_tosca_base import TestToscaBase


class TestSockshop(TestToscaBase):

    def test(self):
        file = 'data/examples/sockshop-app/sockshop.csar'
        up = self.read_plan(
            'data/examples/sockshop-app/sockshop.up.plan'
        )
        down = self.read_plan(
            'data/examples/sockshop-app/sockshop.down.plan'
        )
        self.assert_up_start(file, up)
        self.assert_down(file, down)
        
        # TODO: checks that the application works

if __name__ == '__main__':
    unittest.main()
