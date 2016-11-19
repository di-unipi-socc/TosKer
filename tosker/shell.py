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


def _usage():
    return '''
tosker <tosca_file> <cmds> <inputs>

cmd:
    create
    start
    stop
    delete

example:
    tosker hello.yaml create start --name mario
    '''


_FLAG = {
    '--debug': 'debug',
    '-q': 'quiet',
    '--quiet': 'quiet'
}


def _parse_unix_input(args):
    inputs = {}
    cmds = []
    flag = {}
    p1 = re.compile('--.*')
    p2 = re.compile('-.?')
    i = 0
    while i < len(args):
        if p1.match(args[i]):
            if _FLAG[args[i]]:
                flag[_FLAG[args[i]]] = True
            elif not p.match(args[i + 1]):
                inputs[args[i][2:]] = args[i + 1]
                i += 2
                continue
        elif p2.match(args[i]):
            if _FLAG[args[i]]:
                flag[_FLAG[args[i]]] = True
        else:
            cmds.append(args[i])
        i += 1
    return cmds, flag, inputs


def run():
    if len(argv) < 3:
        print_('error: few arguments..', _usage())
        exit(-1)

    file_name = None
    if path.exists(argv[1]):
        if path.isdir(argv[1]):
            files = glob(path.join(argv[1], "*.yaml"))
            if len(files) != 0:
                file_name = files[0]
        else:
            if argv[1].endswith(('.yaml', '.csar', '.zip')):
                file_name = argv[1]
    if not file_name:
        print_('error: first argument must be a TOSCA yaml file or a directory \
                with a TOSCA yaml file', _usage())
        exit(-1)

    cmds, flags, inputs = _parse_unix_input(argv[2:])
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
        }.get(c, lambda: print_('error: command not found..', _usage()))()

    deployer.print_outputs()
