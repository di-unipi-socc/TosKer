'''
A set of function to help the implementation of the protocols
'''
from .graph.protocol import Protocol, State, Transition
from .graph.relationships import HOST, STORAGE, CONNECTION,\
                                 DEPENDENCY, ATTACHMENT, ENDPOINT, FEATURE


def get_container_protocol():
    '''
    Return the default protocol for the Container components
    '''
    protocol = Protocol()
    protocol.states = deleted, created, running = [
        State('deleted'),
        State('created', offers={HOST}),
        State('running',
              requires={STORAGE, CONNECTION, DEPENDENCY},
              offers={HOST, ENDPOINT, FEATURE})
    ]
    protocol.initial_state = protocol.current_state = deleted

    protocol.transitions = create, start, stop, delete = [
        Transition('create', deleted, created, 'create'),
        Transition('start', created, running, 'start'),
        Transition('stop', running, created, 'stop'),
        Transition('delete', created, deleted, 'delete')
    ]

    deleted.transitions = [create]
    created.transitions = [delete, start]
    running.transitions = [stop]

    return protocol


def get_software_protocol():
    '''
    Return the default protocol for the Software components
    '''
    protocol = Protocol()
    protocol.states = deleted, created, running = [
        State('deleted'),
        State('created', requires={HOST}, offers={HOST}),
        State('running',
              requires={HOST, CONNECTION, DEPENDENCY},
              offers={HOST, ENDPOINT, FEATURE})
    ]
    protocol.initial_state = protocol.current_state = deleted

    protocol.transitions = create, start, stop, delete = [
        Transition('create', deleted, created, 'create'),
        Transition('start', created, running, 'start'),
        Transition('stop', running, created, 'stop'),
        Transition('delete', created, deleted, 'delete')
    ]

    deleted.transitions = [create]
    created.transitions = [delete, start]
    running.transitions = [stop]

    return protocol

def get_volume_protocol():
    '''
    Return the default protocol for the Volume components
    '''
    protocol = Protocol()
    protocol.states = deleted, created = [
        State('deleted'),
        State('created', offers={ATTACHMENT})
    ]
    protocol.initial_state = protocol.current_state = deleted

    protocol.transitions = create, delete = [
        Transition('create', deleted, created, 'create'),
        Transition('delete', created, deleted, 'delete')
    ]

    deleted.transitions = [create]
    created.transitions = [delete]

    return protocol