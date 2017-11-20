'''
Classes to represent a Protocol
'''
from .relationships import HOST, STORAGE, CONNECTION,\
                           DEPENDENCY, ATTACHMENT, ENDPOINT, FEATURE

class Protocol():
    '''
    The Protocol class representation.

    Attributes:
    initial_state -- the initial state (type:State)
    current_state -- the current state (type:State)
    states        -- a list of States (type:[State])
    transitions   -- the list of transitions (type:[Transition])
    '''
    def __init__(self):
        """Create a new Protocol object."""
        self.states = []
        self.transitions = []
        self._initial_state = None
        self._current_state = None

    @property
    def initial_state(self):
        return self._initial_state

    @initial_state.setter
    def initial_state(self, state):
        assert isinstance(state, State)
        self.current_state = self._initial_state = state

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, state):
        assert isinstance(state, (State, str))
        if isinstance(state, str):
            state = next((s for s in self.states if s.name == state), None)
        self._current_state = state
        
    def reset(self):
        """Reset the protocol state."""
        self.current_state = self.initial_state

    def execute_operation(self, operation):
        """Execute the operation and change the current state."""
        next_state = self.next_state(operation)
        if next_state is None:
            return None
        self.current_state = next_state
        return next_state

    def next_state(self, operation):
        """Return the state reached from the current state with the given operation."""
        return self.current_state.next_state(operation)

    def next_transition(self, operation):
        """Return the transition reached with the given operation."""
        return self.current_state.next_transition(operation)

class State():
    """
    The protocol State class representation.

    Attributes:
    name        -- the State name (type:str)
    offers      -- the list of the capability offered in the state (type:[str])
    requires    -- the list of the requirement required in the state (type:[str])
    transitions -- the transition list (type:[Transition])
    """
    def __init__(self, name, requires=None, offers=None, transitions=None):
        """Create a new State object."""
        self.name = name
        self.requires = requires if requires is not None else []
        self.offers = offers if offers is not None else []
        self.transitions = transitions if transitions is not None else []

    def next_transition(self, operation):
        """Return the transition reached with the given operation."""
        return next((t for t in self.transitions if t.name == operation), None)

    def next_state(self, operation):
        """Return the state reached with the given operation."""
        transition = self.next_transition(operation)
        return transition.target if transition is not None else None

class Transition():
    """
    The protocol Transition class represention.

    Attributes:
    name -- the name Transition name (type:str)
    source -- the source state of the Transition (type:State)
    target -- the target state of the Transition (type:State)
    interface -- the interface name to be executed to change the State (type:str)
    """
    def __init__(self, name, source=None, target=None, interface=None):
        """Create a new Transition object."""
        self.name = name
        self.source = source
        self.target = target
        self.interface = interface


# Default protocols
def get_container_protocol():
    """Return the default protocol for the Container component."""
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
    """Return the default protocol for the Software component."""
    protocol = Protocol()
    protocol.states = deleted, created, configured, running = [
        State('deleted'),
        State('created', requires={HOST}, offers={HOST}),
        State('configured', requires={HOST}, offers={HOST}),
        State('running',
              requires={HOST, CONNECTION, DEPENDENCY},
              offers={HOST, ENDPOINT, FEATURE})
    ]
    protocol.initial_state = protocol.current_state = deleted

    protocol.transitions = create, configure, start, stop, delete, delete_conf = [
        Transition('create', deleted, created, 'create'),
        Transition('configure', created, configured, 'configure'),
        Transition('start', configured, running, 'start'),
        Transition('stop', running, configured, 'stop'),
        Transition('delete', created, deleted, 'delete'),
        Transition('delete', configured, deleted, 'delete')
    ]

    deleted.transitions = [create]
    created.transitions = [delete, configure]
    configured.transitions = [start, delete_conf]
    running.transitions = [stop]

    return protocol

def get_volume_protocol():
    """Return the default protocol for the Volume component."""
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
