'''
Classes used to represent a Management Protocol
'''
from .relationships import (ATTACHMENT, CONNECTION, DEPENDENCY, ENDPOINT,
                            FEATURE, HOST, STORAGE)


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
        assert isinstance(state, State)
        self._current_state = state
    
    def find_state(self, state_name):
        """Find the state object given its name."""
        return next((s for s in self.states if state_name == s.name), None)
    
    def reset(self):
        """Reset the protocol state."""
        self.current_state = self.initial_state

    def is_reset(self):
        return self.current_state == self.initial_state

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

    def __str__(self):
        return 'States: {}\nTransitions: {}\nInitial state: {}\nCurrent state: {}'.format(
            ', '.join((str(s) for s in self.states)),
            ', '.join((str(t) for t in self.transitions)),
            self.initial_state, self.current_state
        )

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
        return next((t for t in self.transitions if t.full_operation == operation), None)

    def next_state(self, operation):
        """Return the state reached with the given operation."""
        transition = self.next_transition(operation)
        return transition.target if transition is not None else None

    def __eq__(self, other):
        return isinstance(other, State) and\
               self.name == other.name

    def __str__(self):
        return '({}, r=[{}], o=[{}], t=[{}])'.format(
            self.name, ','.join(self.requires), ','.join(self.offers),
            ','.join((t.full_operation for t in self.transitions)))

class Transition():
    """
    The protocol Transition class represention.

    Attributes:
    name -- the name Transition name (type:str)
    source -- the source state of the Transition (type:State)
    target -- the target state of the Transition (type:State)
    interface -- the interface name (type:str)
    operation -- the operation name to be executed to change the State (type:str)
    """
    def __init__(self, source=None, target=None, interface='Standard',
                 operation=None, requires=None):
        """Create a new Transition object."""
        self.source = source
        self.target = target
        self.interface = interface
        self.operation = operation
        self.requires = requires if requires is not None else []

    @property
    def full_operation(self):
        return '.'.join((self.interface, self.operation))

    def __eq__(self, other):
        return isinstance(other, Transition) and\
               self.source == other.source and\
               self.target == other.target and\
               self.full_operation == other.full_operation

    def __str__(self):
        return '(s={}, t={}, o={}, r=[{}])'.format(
            self.source.name, self.target.name, self.full_operation, ','.join(self.requires))

# Protocols constants
ALIVE = 'alive'
CONTAINER_STATES = CONTAINER_STATE_DELETED, CONTAINER_STATE_CREATED, CONTAINER_STATE_RUNNING =\
                   'deleted', 'created', 'running'
SOFTWARE_STATES = SOFTWARE_STATE_DELETED, SOFTWARE_STATE_CREATED, SOFTWARE_STATE_CONFIGURED,\
                  SOFTWARE_STATE_RUNNING, SOFTWARE_STATE_ZOTTED = 'deleted', 'created',\
                  'configured', 'running', 'zotted'
VOLUME_STATES = VOLUME_STATE_DELETED, VOLUME_STATE_CREATED = 'deleted', 'created'

STATES = STATE_DELETED, STATE_CREATED, STATE_CONFIGURED, STATE_RUNNING, STATE_ZOTTED =\
         SOFTWARE_STATES

# Default protocols
def get_container_protocol():
    """Return the default protocol for the Container component."""
    protocol = Protocol()
    protocol.states = deleted, created, running = [
        State(CONTAINER_STATE_DELETED),
        State(CONTAINER_STATE_CREATED, offers=[ALIVE]),
        State(CONTAINER_STATE_RUNNING,
              requires=[STORAGE, CONNECTION, DEPENDENCY],
              offers=[ALIVE, HOST, ENDPOINT, FEATURE])
    ]
    protocol.initial_state = deleted

    protocol.transitions = create, start, stop, delete = [
        Transition(deleted, created, operation='create'),
        Transition(created, running, operation='start'),
        Transition(running, created, operation='stop'),
        Transition(created, deleted, operation='delete')
    ]

    deleted.transitions = [create]
    created.transitions = [delete, start]
    running.transitions = [stop]

    return protocol


def get_software_protocol():
    """Return the default protocol for the Software component."""
    protocol = Protocol()
    protocol.states = deleted, created, configured, running = [
        State(SOFTWARE_STATE_DELETED),
        State(SOFTWARE_STATE_CREATED, requires=[ALIVE], offers=[ALIVE]),
        State(SOFTWARE_STATE_CONFIGURED, requires=[ALIVE], offers=[ALIVE]),
        State(SOFTWARE_STATE_RUNNING,
              requires=[ALIVE, HOST, CONNECTION, DEPENDENCY],
              offers=[ALIVE, HOST, ENDPOINT, FEATURE])
    ]
    protocol.initial_state = deleted

    protocol.transitions = create, configure, start, stop, delete, delete_conf = [
        Transition(deleted, created, operation='create', requires=[HOST]),
        Transition(created, configured, operation='configure', requires=[HOST]),
        Transition(configured, running, operation='start', requires=[HOST]),
        Transition(running, configured, operation='stop', requires=[HOST]),
        Transition(created, deleted, operation='delete', requires=[HOST]),
        Transition(configured, deleted, operation='delete', requires=[HOST])
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
        State(VOLUME_STATE_DELETED),
        State(VOLUME_STATE_CREATED, offers=[ATTACHMENT])
    ]
    protocol.initial_state = deleted

    protocol.transitions = create, delete = [
        Transition(deleted, created, operation='create'),
        Transition(created, deleted, operation='delete')
    ]

    deleted.transitions = [create]
    created.transitions = [delete]

    return protocol
