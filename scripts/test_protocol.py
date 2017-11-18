from tosker.tosca_parser import get_tosca_template
from tosker.graph.nodes import Root
from yaml.scanner import ScannerError
from toscaparser.common.exception import ValidationError

def parse_tosca(file_path, inputs=None):
    # Parse TOSCA file
    try:
        return get_tosca_template(file_path, inputs)
    except ScannerError as e:
        print('YAML parse error\n    {}'.format(e))
        return False
    except ValidationError as e:
        print('TOSCA validation error\n    {}'.format(e))
        return False
    except ValueError as e:
        print('TosKer validation error\n    {}'.format(e))
        return False
    except Exception as e:
        print('Internal error\n    {}'.format(e))
        return False

def get_next_state(state, operation):
    transition = next((t for t in state.transitions if t.name == operation))
    return transition.target

def can_execute(operation:str, component:Root):
    assert isinstance(operation, str)
    assert isinstance(component, Root)

    # component must have the opetaion in the current state
    state = component.protocol.current_state
    # print('DEBUG:', state.name, state.transitions)
    transition = next((t for t in state.transitions if t.name == operation), None)
    print('    component "{}" is in state "{}"'. format(component.name, state.name))
    if transition is None:
        return False

    # all requirement of the next state are satisfied
    for req in transition.target.requires:
        for rel in component.relationships:
            if rel.requirement == req:
                # check that the capability needed is offered
                # by the target of the relationship
                print('    component "{}" require "{}" and "{}" offers {}'
                      ''.format(component.name, rel.requirement,
                                rel.to.name,
                                rel.to.protocol.current_state.offers))

                if not any((cap == rel.capability for cap in rel.to.protocol.current_state.offers)):
                    return False
    return True

def execute_op(operation:str, component:Root):
    assert isinstance(operation, str)
    assert isinstance(component, Root)
    next_state = get_next_state(component.protocol.current_state, operation)
    component.protocol.current_state = next_state

def check(tpl, ops):
    '''
    tpl:Template
    op:[(component:str, operation:str)]
    return Boolean
    '''
    for comp_name, operation in ops:
        component = tpl[comp_name]
        print('check op "{}" on "{}"'.format(operation, comp_name))
        
        if can_execute(operation, component):
            execute_op(operation, component)
            print('execute op "{}" on "{}"'.format(operation, comp_name))
        else:
            print('cannot execute op "{}" on "{}"'.format(operation, comp_name))
            return False
    

def run():
    # tpl = parse_tosca('data/examples/hello.yaml')
    # check(tpl, [
    #     ('hello_container', 'create'),
    #     ('hello_container', 'start'),
    #     ('hello_container', 'stop'),
    #     ('hello_container', 'delete')
    # ])
    tpl = parse_tosca('data/examples/wordpress.yaml')
    check(tpl, [
        ('mysql_volume', 'create'),
        ('mysql_container', 'create'),
        # ('mysql_container', 'start'),
        ('wordpress_container', 'create'),
        ('wordpress_container', 'start')
    ])

if __name__ == '__main__':
    run()
