'''
Classes to represent a Protocol
'''

class Protocol():
    '''
    A protocol class representation
    '''
    def __init__(self):
        '''
        pubblic attributes:
            initial_state:State
            states:{State}
            transitions:{Transition}
        '''
        self.states = []
        self.transitions = []
        self.initial_state = None
        self.current_state = None

class State():
    '''
    A protocol state class representation
    '''
    def __init__(self, name, requires=None, offers=None, transitions=None):
        '''
        State attributes:
            name:{str}
            offers:{str}
            requires:{str}
            transitions:{Transition}
        '''
        self.name = name
        self.requires = requires if requires is not None else []
        self.offers = offers if offers is not None else []
        self.transitions = transitions if transitions is not None else []

class Transition():
    '''
    A protocol transition class represention
    '''
    def __init__(self, name, source=None, target=None, interface=None):
        '''
        Transition attributes:
            name :str
            source :State
            target :State
            interface :str
        '''
        self.name = name
        self.source = source
        self.target = target
        self.interface = interface
