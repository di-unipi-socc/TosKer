import logging
import os
import re
from glob import glob
from os import path
from sys import argv

from six import print_

from tosker.orchestrator import Orchestrator
from tosker.helper import Logger
from tosker import helper
from tosker import __version__


def _usage():
    return '''
Usage: tosker FILE COMMANDS... [OPTIONS] [INPUTS]
       tosker -h|--help
       tosker -v|--version
Orchestrate TOSCA applications on top of Docker.

FILE: TOSCA YAML file or CSAR file

COMMANDS:
  create   Create application components
  start    Start applications components
  stop     Stop application components
  delete   Delete application components (except volume)

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
    flags = {}
    file = ''
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
                _error('missing input value for', args[i])
        elif p2.match(args[i]):
            if _FLAG.get(args[i], False):
                flags[_FLAG[args[i]]] = True
            else:
                _error('known parameter.')
        elif args[i] and file:
            cmds.append(args[i])
        elif i == 0:
            file = args[i]
        else:
            _error('first argument must be a TOSCA yaml file or a '
                   'directory with in a CSAR file.')
        i += 1
    return file, cmds, flags, inputs


def _error(*str):
    print_('ERROR:', *str)
    exit(-1)


def run():
    if len(argv) < 2:
        _error('few arguments.')

    file, cmds, flags, inputs = _parse_unix_input(argv[1:])
    if flags.get('help', False):
        print_(_usage())
        exit()
    elif flags.get('version', False):
        print_('TosKer version {}'.format(__version__))
        exit()

    file_name = None
    if path.exists(file):
        if path.isdir(file):
            files = glob(path.join(argv[1], "*.csar"))
            if len(files) != 0:
                file_name = files[0]
        else:
            if file.endswith(('.yaml', '.csar', '.zip')):
                file_name = file
    if not file_name:
        _error('first argument must be a TOSCA yaml file or a '
               'directory with in a CSAR file.')

    if flags.get('debug', False):
        orchestrator = Orchestrator(file_name, inputs,
                                    log_handler=helper.get_consol_handler(),
                                    quiet=False)
    else:
        orchestrator = Orchestrator(file_name,
                                    inputs,
                                    quiet=flags.get('quiet', False))

    for c in cmds:
        {
            'create': orchestrator.create,
            'start': orchestrator.start,
            'stop': orchestrator.stop,
            'delete': orchestrator.delete,
        }.get(c, lambda: _error('command not found.'))()

    orchestrator.print_outputs()
