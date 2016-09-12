from sys import argv
from os import path
from toscaparser.tosca_template import ToscaTemplate
from tosca_deployer import utility


def parse_input(str):
    inputs = {}
    inputs_list = str.split(':')
    key = None
    for i, val in enumerate(inputs_list):
        val = val.strip()
        if i == 0:
            key = val
        elif i == len(inputs_list)-1:
            inputs[key] = val
        else:
            val = val.split(" ")
            inputs[key] = ' '.join(val[0:len(val)-1])
            key = val[len(val)-1]
    return inputs


def usage():
    return '''
tosca-parser <tosca_file>
    '''

if __name__ == '__main__':

    if len(argv) < 2:
        print ('error: few arguments..', usage())
        exit(-1)

    if not (path.exists(argv[1]) and argv[1].split('.')[-1] == 'yaml'):
        print ('error: first argument must be a TOSCA yaml file', usage())
        exit(-1)

    inputs = parse_input(' '.join(argv[2:]))

    tosca = ToscaTemplate(argv[1], inputs, True)

    utility.print_TOSCA(tosca)
