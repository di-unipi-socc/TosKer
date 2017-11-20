"""A set of functions to help the protocols implementation."""
from .helper import Logger
from .graph.nodes import Root

def can_execute(operation, component):
    """Check if an operation can be executed on a component."""
    assert isinstance(operation, str)
    assert isinstance(component, Root)
    _log = Logger.get(__name__)
    # component must have the opetaion in the current state
    protocol = component.protocol
    transition = protocol.next_transition(operation)
    _log.info('component "{}" is in state "{}"'.format(
        component.name, protocol.current_state.name))
    if transition is None:
        return False

    # all requirement of the next state are satisfied
    for req in transition.target.requires:
        for rel in component.relationships:
            if rel.requirement == req:
                # check that the capability needed is offered
                # by the target of the relationship
                _log.info('component "%s" require "%s" and "%s" offers %s',
                          component.name, rel.requirement, rel.to.name,
                          rel.to.protocol.current_state.offers)

                if rel.capability not in rel.to.protocol.current_state.offers:
                    return False

    # all offers are not used by anyone
    for off in transition.source.offers:
        for rel in component.up_requirements:
            if rel.capability == off:
                # check that the capability needed is offered
                # by the target of the relationship
                _log.info('component "%s" offers "%s" and "%s" requires %s',
                          component.name, rel.capability, rel.origin.name,
                          rel.origin.protocol.current_state.requires)

                if rel.requirement in rel.origin.protocol.current_state.requires:
                    return False
    return True
