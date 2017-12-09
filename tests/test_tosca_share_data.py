import os
import unittest
from time import sleep

from .test_tosca_base import TestToscaBase


class TestShareData(TestToscaBase):

    def test(self):

        file = 'data/examples/share-data-container/share-data.yaml'
        up_plan = self.read_plan(
            'data/examples/share-data-container/share-data.up.plan'
        )
        down_plan = self.read_plan(
            'data/examples/share-data-container/share-data.down.plan'
        )

        self.assert_up_exit(file, up_plan)
        sleep(1)
        self.assert_down(file, down_plan)

        self.assertTrue(os.path.isfile('/tmp/tosker_share_data_test'))

if __name__ == '__main__':
    unittest.main()
