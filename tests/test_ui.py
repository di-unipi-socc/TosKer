import unittest

from tosker import ui


class TestUi(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_args_flags(self):
        args = ['--help', '--debug', '--quiet', '--version']
        error, mod,\
            file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNone(error)
        self.assertTrue(flags.get('help', False))
        self.assertTrue(flags.get('debug', False))
        self.assertTrue(flags.get('quiet', False))
        self.assertTrue(flags.get('version', False))

        args = ['-v', '-h', '-q']
        error, mod,\
            file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNone(error)
        self.assertTrue(flags.get('quiet', False))
        self.assertTrue(flags.get('help', False))
        self.assertTrue(flags.get('version', False))

        args = ['--test']
        error, mod,\
            file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNotNone(error)

        args = ['-t']
        error, mod,\
            file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNotNone(error)

    def test_args_command(self):
        args = ['data/examples/hello.yaml',
                'create', 'start', 'stop', 'delete']
        error, mod,\
            file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNone(error)
        self.assertEqual('data/examples/hello.yaml', file)
        self.assertListEqual(['create', 'start', 'stop', 'delete'], cmds)

        args = ['data/examples/hello.yaml',
                'comp1', 'comp2', 'comp3',
                'create', 'start', 'stop', 'delete']
        error, mod,\
            file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNone(error)
        self.assertEqual('data/examples/hello.yaml', file)
        self.assertListEqual(['create', 'start', 'stop', 'delete'], cmds)
        self.assertListEqual(['comp1', 'comp2', 'comp3'], comps)

        args = ['data/examples/hello.yaml',
                'create', 'test', 'start', 'stop', 'delete']
        error, mod,\
            file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNotNone(error)

        args = ['asd',
                'comp1', 'comp2', 'comp3',
                'create', 'start', 'stop', 'delete']
        error, mod,\
            file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNotNone(error)

    def test_args_inputs(self):
        args = ['--input1', 'value1', '--input2', 'value2']
        error, mod,\
            file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNone(error)
        self.assertEqual(inputs.get('input1'), 'value1')
        self.assertEqual(inputs.get('input2'), 'value2')

        args = ['--input1', '--input2', 'value2']
        error, mod,\
            file, cmds, comps, flags, inputs = ui._parse_unix_input(args)
        self.assertIsNotNone(error)

    def test_check_file(self):
        self.assertIsNotNone(
            ui._check_file('data/examples/hello.yaml')
        )
        self.assertIsNotNone(
            ui._check_file(
                'data/examples/node-mongo-csar/node-mongo.csar')
        )
        self.assertIsNone(
            ui._check_file(
                'data/examples/node-mongo-csar')
        )
        self.assertIsNone(
            ui._check_file(
                'data/examples/node-mongo-csar/'
                'node-mongo/scripts/install_node.sh')
        )
