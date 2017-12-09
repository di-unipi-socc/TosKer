"""
Terminal interface build with click
"""
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

@cli.command()
@click.pass_context
@click.argument('file', type=click.Path(exists=True))
@click.argument('cmds', nargs=-1)
@click.option('--plan', '-p', type=click.Path(exists=True), help='File with the plan to execute.')
@click.option('--dry-run', is_flag=True, help='Simulate the dangerous operations.')
def exec(ctx, file, cmds, plan, dry_run):
    """Exec a plan to a topology.

    \b
    Examples:
    tosker hello.yaml component1:Standard.create component1:Standard.start
    tosker hello.yaml -p hello.down.plan
    cat hello.up.plan | tosker hello.yaml -
    """
    if plan:
        cmds = ctx.obj.read_plan(plan)
    elif cmds and cmds[0] == '-':
        import sys
        cmds = [line.strip() for line in sys.stdin if line.strip()]
    elif not cmds:
        ctx.fail('must supply a list of operation to execute.')
    # TODO: add inputs
    # TODO: implement dry_run
    inputs = None
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
    """Print the log of the execution of a component.
    
    \b
    Examples:
    tosker log my_app.my_component Standard.create
    """
    ctx.obj.log(component, operation)

@cli.command()
@click.pass_context
@click.confirmation_option(prompt='Are you sure you want remove all TosKer files?')
def prune(ctx):
    """Remove all files, container and volumes created."""
    ctx.obj.prune()
