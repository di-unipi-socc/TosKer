from sys import argv
from os import path
import re
import glob
import os
import logging
from tosca_deployer.deployer import Deployer
from tosca_deployer.utility import Logger


def usage():
    return '''
deployer <tosca_file> <cmd> <inputs>

cmd:
    create
    start
    stop
    delete

example:
    deployer hello.yaml start --name mario
    '''


def parse_input(args):
    string = ' '.join(args)
    inputs = {}
    inputs_list = string.split(':')
    key = None
    for i, val in enumerate(inputs_list):
        val = val.strip()
        if i == 0:
            key = val
        elif i == len(inputs_list) - 1:
            inputs[key] = val
        else:
            val = val.split(" ")
            inputs[key] = ' '.join(val[0:len(val) - 1])
            key = val[len(val) - 1]
    return inputs


def parse_unix_input(args):
    inputs = {}
    cmds = []
    p = re.compile('--.*')
    i = 0
    while i < len(args):
        if p.match(args[i]):
            if not p.match(args[i + 1]):
                inputs[args[i][2:]] = args[i + 1]
                i += 2
                continue
        else:
            cmds.append(args[i])
        i += 1
    return (cmds, inputs)


if __name__ == '__main__':
    if len(argv) < 3:
        print('error: few arguments..', usage())
        exit(-1)

    file_name = None
    if path.exists(argv[1]):
        if path.isdir(argv[1]):
            files = glob.glob(path.join(argv[1], "*.yaml"))
            if len(files) != 0:
                file_name = files[0]
        else:
            if argv[1].split('.')[-1] == 'yaml':
                file_name = argv[1]
    if not file_name:
        print('error: first argument must be a TOSCA yaml file or a directory with a TOSCA yaml file', usage())
        exit(-1)

    cmds, inputs = parse_unix_input(argv[2:])
    deployer = Deployer(file_name, inputs, logging.DEBUG)

    for c in cmds:
        {
            # 'run': deployer.run,
            'create': deployer.create,
            'start': deployer.start,
            'stop': deployer.stop,
            'delete': deployer.delete,
        }.get(c, lambda: print('error: command not found..', usage()))()
