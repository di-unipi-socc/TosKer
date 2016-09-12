from sys import argv
from os import path
import re
from tosca_deployer.deployer import Deployer


def usage():
    return '''
deployer <tosca_file> <cmd> <inputs>

cmd:
    run
    create
    start
    stop
    delete

example:
    deployer hello.yaml run --name mario
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
    p = re.compile('--.*')
    i = 0
    while i < len(args):
        if p.match(args[i]):
            if not p.match(args[i + 1]):
                inputs[args[i][2:]] = args[i + 1]
                i += 2
                continue
        i += 1
    return inputs


if __name__ == '__main__':

    if len(argv) < 3:
        print('error: few arguments..', usage())
        exit(-1)

    if not (path.exists(argv[1]) and argv[1].split('.')[-1] == 'yaml'):
        print('error: first argument must be a TOSCA yaml file', usage())
        exit(-1)

    inputs = parse_unix_input(argv[3:])

    deployer = Deployer(argv[1], inputs)

    {
        'run': deployer.run,
        'create': deployer.create,
        'start': deployer.start,
        'stop': deployer.stop,
        'delete': deployer.delete,
    }.get(argv[2], lambda: print('error: command not found..', usage()))()
