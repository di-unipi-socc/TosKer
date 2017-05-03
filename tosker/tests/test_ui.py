import unittest
from tosker import ui


class Test_Ui(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_args_flags(self):
        args = ['--help', '--debug', '--quiet', '--version']
        error, file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNone(error)
        self.assertTrue(flags.get('help', False))
        self.assertTrue(flags.get('debug', False))
        self.assertTrue(flags.get('quiet', False))
        self.assertTrue(flags.get('version', False))

        args = ['-v', '-h', '-q']
        error, file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNone(error)
        self.assertTrue(flags.get('quiet', False))
        self.assertTrue(flags.get('help', False))
        self.assertTrue(flags.get('version', False))

        args = ['--test']
        error, file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNotNone(error)

        args = ['-t']
        error, file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNotNone(error)

    def test_args_command(self):
        args = ['tosker/tests/TOSCA/hello.yaml',
                'create', 'start', 'stop', 'delete']
        error, file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNone(error)
        self.assertEqual('tosker/tests/TOSCA/hello.yaml', file)
        self.assertListEqual(['create', 'start', 'stop', 'delete'], cmds)

        args = ['tosker/tests/TOSCA/hello.yaml',
                'comp1', 'comp2', 'comp3',
                'create', 'start', 'stop', 'delete']
        error, file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNone(error)
        self.assertEqual('tosker/tests/TOSCA/hello.yaml', file)
        self.assertListEqual(['create', 'start', 'stop', 'delete'], cmds)
        self.assertListEqual(['comp1', 'comp2', 'comp3'], comps)

        args = ['tosker/tests/TOSCA/hello.yaml',
                'create', 'test', 'start', 'stop', 'delete']
        error, file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNotNone(error)

        args = ['asd',
                'comp1', 'comp2', 'comp3',
                'create', 'start', 'stop', 'delete']
        error, file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNotNone(error)

    def test_args_inputs(self):
        args = ['--input1', 'value1', '--input2', 'value2']
        error, file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNone(error)
        self.assertEqual(inputs.get('input1'), 'value1')
        self.assertEqual(inputs.get('input2'), 'value2')

        args = ['--input1', '--input2', 'value2']
        error, file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNotNone(error)

    def test_check_file(self):
        self.assertIsNotNone(
            ui._check_file('tosker/tests/TOSCA/hello.yaml')
        )

        self.assertIsNotNone(
            ui._check_file(
                'tosker/tests/TOSCA/node-mongo-csar/node-mongo.csar')
        )

        self.assertIsNone(
            ui._check_file(
                'tosker/tests/TOSCA/node-mongo-csar')
        )

        self.assertIsNone(
            ui._check_file(
                'tosker/tests/TOSCA/node-mongo-csar/'
                'node-mongo/scripts/install_node.sh')
        )
