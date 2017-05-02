import unittest
from tosker.orchestrator import Orchestrator
from tosker.docker_interface import Docker_interface


class Test_Tosca_Parsing(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self._orchestrator = Orchestrator()
        self._docker = Docker_interface()

    def test_no_dag(self):
        self.assertFalse(
            self._orchestrator.orchestrate('tosker/tests/TOSCA/nodag.yaml', [])
        )

    def test_wrong_type(self):
        self.assertFalse(
            self._orchestrator.orchestrate(
                'tosker/tests/TOSCA/wrong_components.yaml', [])
        )

    def test_wrong_component(self):
        self.assertFalse(
            self._orchestrator.orchestrate(
                'tosker/tests/TOSCA/wordpress.yaml', [], ['no_compent'], {})
        )

    def test_orchestraion_error(self):
        self.assertFalse(
            self._orchestrator.orchestrate(
                'tosker/tests/TOSCA/hello.yaml',
                ['create', 'create'])
        )

        for c in self._orchestrator._tpl.container_order:
            self.assertIsNotNone(
                self._docker.inspect(c.name)
            )

        self.assertFalse(
            self._orchestrator.orchestrate(
                'tosker/tests/TOSCA/hello.yaml',
                ['delete', 'delete'])
        )

        for c in self._orchestrator._tpl.container_order:
            self.assertIsNone(
                self._docker.inspect(c.name)
            )


if __name__ == '__main__':
    unittest.main()
