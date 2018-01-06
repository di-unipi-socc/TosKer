"""A set of functions to help the protocols implementation."""
import six

from .graph.nodes import Root
from .helper import Logger

def can_execute(operation, component):
    """Check if an operation can be executed on a component."""
    assert isinstance(operation, six.string_types)
    assert isinstance(component, Root)
    _log = Logger.get(__name__)

    # component must have the opetaion in the current state
    protocol = component.protocol
    transition = protocol.next_transition(operation)
    _log.info('component "%s" is in state "%s"', component.name, protocol.current_state.name)
    if transition is None:
        raise ValueError('cannot execute operation "{}" from state "{}".'
                         ''.format(operation, protocol.current_state.name))

    # all requirement of the transition and of the next state
    # are satisfied.
    for req in transition.target.requires + transition.requires:
        for rel in component.relationships:
            if rel.requirement == req:
                # check that the capability needed is offered
                # by the target of the relationship
                _log.info('component "%s" require "%s" and "%s" offers %s',
                          component.name, rel.requirement, rel.to.name,
                          rel.to.protocol.current_state.offers)

                if rel.capability not in rel.to.protocol.current_state.offers:
                    raise ValueError('component "{}" require "{}" that is not offers by "{}"'
                                     ''.format(component.name, rel.requirement, rel.to.name))

    # all offers are not used by other component
    _log.debug('what I offer %s', transition.source.offers)
    _log.debug('who require me %s', [str(r) for r in component.up_requirements])
    for off in transition.source.offers:
        for rel in component.up_requirements:
            if rel.capability == off:
                # check that the capability needed is offered
                # by the target of the relationship
                _log.info('component "%s" offers "%s" and "%s" requires %s',
                          component.name, rel.capability, rel.origin.name,
                          rel.origin.protocol.current_state.requires)

                if rel.requirement in rel.origin.protocol.current_state.requires and\
                   rel.requirement not in transition.target.offers:
                    raise ValueError('component "{}" offers "{}" that is required by "{}"'
                                     ''.format(component.name, rel.capability, rel.origin.name))
