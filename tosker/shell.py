import logging
import os
import re
from glob import glob
from os import path
from sys import argv

from six import print_

from tosker.deployer import Deployer
from tosker.utility import Logger
from tosker import utility
from tosker import __version__


def _usage():
    return '''
Usage:
    tosker <file> (create|start|stop|delete)... [<inputs>...]
    tosker <file> (create|start|stop|delete)... -q|--quiet [<inputs>...]
    tosker <file> (create|start|stop|delete)... --debug [<inputs>...]
    tosker -h|--help

Options:
    -h --help     Show this help.
    -q --quiet    Active quiet mode.
    --debug       Active debugging mode.

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
    flag = {}
    file = ''
    p1 = re.compile('--.*')
    p2 = re.compile('-.?')
    i = 0
    while i < len(args):
        if p1.match(args[i]):
            if _FLAG.get(args[i], False):
                flag[_FLAG[args[i]]] = True
            elif not p.match(args[i + 1]):
                inputs[args[i][2:]] = args[i + 1]
                i += 2
                continue
        elif p2.match(args[i]):
            if _FLAG.get(args[i], False):
                flag[_FLAG[args[i]]] = True
        elif args[i] in _CMD:
            cmds.append(args[i])
        elif i == 0:
            file = args[i]
        else:
            _error('ERROR: known parameter.')
        i += 1
    return file, cmds, flag, inputs


def _error(str):
    print_(str)
    exit(-1)


def run():
    if len(argv) < 2:
        _error('ERROR: few arguments.')

    file, cmds, flags, inputs = _parse_unix_input(argv[1:])
    if flags.get('help', False):
        print_(_usage())
        exit()
    elif flags.get('version', False):
        print_('tosKer version {}'.format(__version__))
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
        _error('ERROR: first argument must be a TOSCA yaml file or a '
               'directory with in a CSAR file.')

    if flags.get('debug', False):
        deployer = Deployer(file_name, inputs,
                            log_handler=utility.get_consol_handler(),
                            quiet=False)
    else:
        deployer = Deployer(file_name, inputs, quiet=flags.get('quiet', False))

    for c in cmds:
        {
            'create': deployer.create,
            'start': deployer.start,
            'stop': deployer.stop,
            'delete': deployer.delete,
        }.get(c, lambda: _error('ERROR: command not found.'))()

    deployer.print_outputs()
