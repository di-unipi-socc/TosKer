from os import path
from sys import argv

from toscaparser.tosca_template import ToscaTemplate
from tosker import helper
if len(argv) < 2:
    print('Error: the first parameter must be a TOSCA YAML file')
    exit(1)

if not path.isfile(argv[1]) and not argv[1].endswith('.yaml'):
    print('Error: the parameter is not a valid TOSCA YAML file')
    exit(2)

tosca = ToscaTemplate(argv[1])
print(helper.print_TOSCA(tosca))


# TEST parent discovery
for node in tosca.nodetemplates:
    print(node.name, node.is_derived_from('tosker.nodes.Software'))