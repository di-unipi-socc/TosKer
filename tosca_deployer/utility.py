import json

def get_attributes(args, nodes):
    get = nodes
    for a in args:
        get = get[a]
    return get


def print_TOSCA(tosca, indent=2):
    space = ' ' * indent

    def _rec_print(item, tab):
        if type(item) is dict:
            for key, value in item.items():
                if type(value) is str or (type(value) is dict and 'get_input' in value):
                    print(tab + str(key) + ': ' + str(value))
                else:
                    print(tab + str(key) + ':')
                    _rec_print(value, tab + space)
        elif type(item) is list:
            for value in item:
                if type(value) is str:
                    print(tab + '- ' + value)
                else:
                    # print ('DEBUG:', value)
                    key, value = list(value.items())[0]
                    print(tab + '- ' + key + ':')
                    _rec_print(value, tab + space + '  ')

    if hasattr(tosca, 'nodetemplates'):
        if tosca.inputs:
            print ("\ninputs:")
            for input in tosca.inputs:
                print (space + input.name)

        nodetemplates = tosca.nodetemplates
        if nodetemplates:
            print ("\nnodetemplates:")
            for node in nodetemplates:
                print (space + node.name)
                _rec_print(node.entity_tpl, space + space)
                print()


def print_json(stream):
    for line in stream:
        print(json.dumps(json.loads(line.decode("utf-8")), indent=2))
    # print()


def print_byte(stream):
    for line in stream:
        print(line.decode("utf-8"))
    # print()
