"""
Terminal interface build with click
"""
import re

import click

from . import __version__, helper
from .orchestrator import Orchestrator


@click.group()
@click.version_option(version=__version__)
@click.option('--quiet', '-q', is_flag=True, help='Prevent the command to print.')
@click.option('--debug', is_flag=True, help='Print additional debuging log (override quiet mode).')
@click.pass_context
def cli(ctx, quiet, debug):
    """Orchestrate TOSCA applications on top of Docker.

    TosKer is an orchestrator engine capable of automatically deploying
    and managing multi-component applications specified in OASIS TOSCA. The engine executes
    the component exploiting Docker as a lightweight virtualization framework."""
    if debug:
        ctx.obj = Orchestrator(log_handler=helper.get_consol_handler(),
                               quiet=False)
    else:
        ctx.obj = Orchestrator(quiet=quiet)
    ctx.obj.quiet = quiet


@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.pass_context
@click.argument('file', type=click.Path(exists=True))
@click.argument('cmds_inputs', nargs=-1, type=click.UNPROCESSED)
# @click.argument('cmds', nargs=-1)
@click.option('--plan', '-p', type=click.Path(exists=True), help='File with the plan to execute.')
@click.option('--dry-run', is_flag=True, help='Simulate the dangerous operations.')
def exec(ctx, file, cmds_inputs, plan, dry_run):
    """Exec a plan.

    \b
    Examples:
    tosker hello.yaml component1:Standard.create component1:Standard.start
    tosker hello.yaml -p hello.down.plan
    cat hello.up.plan | tosker hello.yaml -
    """

    cmds, inputs = _get_cmds_inputs(ctx, cmds_inputs)
    if plan:
        cmds = ctx.obj.read_plan(plan)
    elif cmds and cmds[0] == '-':
        import sys
        cmds = [line.strip() for line in sys.stdin if line.strip()]
    elif not cmds:
        ctx.fail('must supply a list of operation to execute.')
    # TODO: implement dry_run
    ctx.obj.orchestrate(file, cmds, inputs)


@cli.command()
@click.pass_context
@click.argument('application', required=False)
@click.option('--state', help='Filter by the component state (i.g. created, configured, running).')
@click.option('--type', help='Filter by the components type (Container, Software, Volume)')
def ls(ctx, application, state, type):
    """List all the deployed applications.

    \b
    Examples:
    tosker ls
    tosker ls hello
    tosker ls hello --type Software --state running"""
    filter = {}
    if state is not None:
        filter['state'] = state
    if type is not None:
        filter['type'] = type
    ctx.obj.ls_components(application, filter)


@cli.command()
@click.pass_context
@click.argument('component', required=True)
@click.argument('operation', required=True)
def log(ctx, component, operation):
    """Print the execution log of an operation.

    \b
    Examples:
    tosker log my_app.my_component Standard.create
    """
    ctx.obj.log(component, operation)


@cli.command()
@click.pass_context
@click.confirmation_option(prompt='Are you sure you want to delete all TosKer files?')
def prune(ctx):
    """Remove all files, container and volumes created."""
    ctx.obj.prune()


def _get_cmds_inputs(ctx, ci):
    """Parse and return commands and TOSCA inputs."""
    cmds = []
    inputs = {}
    i = 0
    while i < len(ci):
        if ci[i].startswith('--'):
            # Parse TOSCA inputs in the two possible format:
            # --key value or --key=value
            if '=' in ci[i]:
                k, v = ci[i].split('=')
                inputs[k[2:]] = v
            elif i < len(ci) - 1:
                inputs[ci[i][2:]] = ci[i + 1]
                i += 1
            else:
                ctx.fail('missing the TOSCA inputs value.')
        else:
            # Check that the format of the operation si correct
            if re.match('.*:.*\..*', ci[i]) is None:
                ctx.fail('"{}" not valid format. Should be COMPONENT:INTERFACE.OPERATION.'
                         ''.format(ci[i]))
            cmds.append(ci[i])
        i += 1
    return cmds, inputs
