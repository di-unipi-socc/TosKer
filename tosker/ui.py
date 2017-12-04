'''
UI module
'''
import re
from os import path
from sys import argv

from six import print_

from . import __version__, helper
from .orchestrator import Orchestrator


def _usage():
    return '''
Usage: tosker FILE COMPONENT:INTERFACE.OPERATION... [OPTIONS] [INPUTS]
       tosker FILE _ [OPTIONS] [INPUTS]
       tosker ls [APPLICATION] [FILTES]
       tosker log APPLICATION.COMPONENT INTERFACE.OPERATION
       tosker prune
       tosker -h|--help
       tosker -v|--version
Orchestrate TOSCA applications on top of Docker.

FILE: TOSCA YAML file or CSAR file

OPTIONS:
  -h --help      Print usage
  -q --quiet     Enable quiet mode
  --debug        Enable debugging mode (override quiet mode)
  -v --version   Print version

INPUTS: provide TOSCA inputs (syntax: --NAME VALUE)

APPLICATION: the application name (CSAR or YAML file without the extension)

COMPONENT: Name of a component in the application

FILTER:
  --name <name>    filter by the component name
  --state <state>  filter by the state (created, started, deleted)
  --type <type>    filter by the type (Container, Volume, Software)

Examples:
  tosker hello.yaml component1:Standard.create component1:Standard.start --name mario
  tosker hello.yaml component1:Standard.stop component1:Standard.delete -q
  cat hello_run.plan | tosker hello.yaml _

  tosker ls
  tosker ls hello
  tosker ls hello --type Software --state running

  tosker log my_app.my_component Standard.create
'''


_FLAG = {
    '--debug': 'debug',
    '-q': 'quiet',
    '--quiet': 'quiet',
    '--help': 'help',
    '-h': 'help',
    '-v': 'version',
    '--version': 'version'
}

def _parse_unix_input(args):
    inputs = {}
    comps = []
    flags = {}
    file = ''
    mod = ''
    error = None
    p1 = re.compile('--.*')
    p2 = re.compile('-.?')
    i = 0
    while i < len(args):
        if p1.match(args[i]):
            if _FLAG.get(args[i], False):
                flags[_FLAG[args[i]]] = True
            elif (i + 1 < len(args) and
                  not p1.match(args[i + 1]) and
                  not p2.match(args[i + 1])):
                inputs[args[i][2:]] = args[i + 1]
                i += 2
                continue
            else:
                error = 'missing input value for {}'.format(args[i])
        elif p2.match(args[i]):
            if _FLAG.get(args[i], False):
                flags[_FLAG[args[i]]] = True
            else:
                error = 'known parameter.'
        elif mod == 'deploy':
            comps.append(args[i])
        elif mod == 'ls' or mod == 'log':
            comps.append(args[i])
        elif i == 0:
            file = _check_file(args[i])
            if file is not None:
                mod = 'deploy'
            elif args[i] == 'ls':
                mod = 'ls'
            elif args[i] == 'log':
                mod = 'log'
            elif args[i] == 'prune':
                mod = 'prune'
            else:
                error = ('first argument must be a TOSCA yaml file, a CSAR or '
                         'a ZIP archive.')
        i += 1
    return error, mod, file, comps, flags, inputs


def _check_file(file):
    file_name = None
    if path.isfile(file):
        if file.endswith(('.yaml', '.csar', '.CSAR', '.YAML')):
            file_name = file
    return file_name


def _error(*str):
    print_('ERROR:', *str)
    exit(-1)


def run():
    if len(argv) < 2:
        _error('few arguments.', '\n', _usage())

    error, mod, file, comps, flags, inputs = _parse_unix_input(argv[1:])

    if error is not None:
        _error(error)

    if flags.get('help', False):
        print_(_usage())
        exit()
    elif flags.get('version', False):
        print_('TosKer version {}'.format(__version__))
        exit()

    if flags.get('debug', False):
        orchestrator = Orchestrator(log_handler=helper.get_consol_handler(),
                                    quiet=False)
    else:
        orchestrator = Orchestrator(quiet=flags.get('quiet', False))

    if mod == 'deploy':
        if comps and comps[0] == '_':
            import sys
            comps = [line.strip() for line in sys.stdin if line.strip()]
        orchestrator.orchestrate(file, comps, inputs)
    elif mod == 'ls':
        if len(comps) > 1:
            _error('too many arguments, ls take an "application name"'
                   'and a "state"')
        else:
            app = comps[0] if comps else None
            orchestrator.ls_components(app, inputs)
    elif mod == 'log':
        if len(comps) != 2:
            _error('log take a component full name and a interface name')
            return
        comp, interface = comps
        orchestrator.log(comp, interface)
    elif mod == 'prune':
        orchestrator.prune()
