import os
import unittest
from time import sleep

from .test_tosca_base import TestOrchestrator


class TestHello(TestOrchestrator):

    def setUp(self):
        super(TestHello, self).setUp()
        self.file = 'data/examples/share-data-container/share-data.yaml'
        self.up_plan = self.read_plan(
            'data/examples/share-data-container/share-data.up.plan'
        )
        self.down_plan = self.read_plan(
            'data/examples/share-data-container/share-data.down.plan'
        )

    def test(self):
        self.assertTrue(
            self.o.orchestrate(self.file, self.up_plan)
        )
        self.assert_create(self.file)
        self.assert_exit(self.file)

        sleep(1)
        
        self.assertTrue(
            self.o.orchestrate(self.file, self.down_plan)
        )
        self.assert_delete(self.file)

        self.assertTrue(os.path.isfile('/tmp/tosker_share_data_test'))

if __name__ == '__main__':
    unittest.main()
