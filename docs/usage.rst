=====
Usage
=====

Complete Usage
--------------
This is the complete usage of TosKer::

Usage: tosker [OPTIONS] COMMAND [ARGS]...

  Orchestrate TOSCA applications on top of Docker.

  TosKer is an orchestrator engine capable of automatically deploying and
  managing multi-component applications specified in OASIS TOSCA. The engine
  executes the component exploiting Docker as a lightweight virtualization
  framework.

Options:
  --version    Show the version and exit.
  -q, --quiet  Prevent the command to print.
  --debug      Print additional debuging log (override quiet mode).
  --help       Show this message and exit.

Commands:
  exec   Exec a plan.
  log    Print the execution log of an operation.
  ls     List all the deployed applications.
  prune  Remove all files, container and volumes...