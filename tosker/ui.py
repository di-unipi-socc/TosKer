import logging
import os
import re
from glob import glob
from os import path
from sys import argv

from six import print_

from .orchestrator import Orchestrator
from .helper import Logger
from . import helper
from . import __version__


def _usage():
    return '''
Usage: tosker FILE [COMPONENTS...] COMMANDS...  [OPTIONS] [INPUTS]
       tosker -h|--help
       tosker -v|--version
Orchestrate TOSCA applications on top of Docker.

FILE: TOSCA YAML file or CSAR file

COMMANDS:
  create   Create application components
  start    Start applications components
  stop     Stop application components
  delete   Delete application components (except volume)

COMPONENTS: list of components to deploy

OPTIONS:
  -h --help      Print usage
  -q --quiet     Enable quiet mode
  --debug        Enable debugging mode (override quiet mode)
  -v --version   Print version

INPUTS: provide TOSCA inputs (syntax: --NAME VALUE)

Examples:
  tosker hello.yaml create --name mario
  tosker hello.yaml start -q
  tosker hello.yaml stop --debuug
  tosker hello.yaml delete

  tosker hello.yaml create start --name mario
  tosker hello.yaml stop delete -q

  tosker hello.yaml database api create start
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

_CMD = {'create', 'start', 'stop', 'delete'}


def _parse_unix_input(args):
    inputs = {}
    cmds = []
    comps = []
    flags = {}
    file = ''
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
        elif args[i] and file:
            if args[i] in _CMD:
                cmds.append(args[i])
            elif len(cmds) == 0:
                comps.append(args[i])
            else:
                error = '{} is not a valid command.'.format(args[i])
        elif i == 0:
            file = _check_file(args[i])
            if file is None:
                error = ('first argument must be a TOSCA yaml file, a CSAR or '
                         'a ZIP archive.')
        i += 1
    return error, file, cmds, comps, flags, inputs


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

    error, file, cmds, comps, flags, inputs = _parse_unix_input(argv[1:])
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
    orchestrator.orchestrate(file, cmds, comps, inputs)
