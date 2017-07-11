=====
Usage
=====

TosKer is a command line programme. It inputs the TOSCA file of the application and the commands to executed on it.

For instance to ``create`` the application described in the ``hello.yaml``::

   tosker hello.yaml create start

To ``start`` the application it is possible to do::

   tosker hello.yaml start

It is also possible to give more than one command to be executed on the application, thus to ``stop`` and ``delete`` the ``hello.yaml`` application execute::

   tosker hello.yaml stop delete


Complete Usage
--------------
This is the complete usage of TosKer::

   tosker FILE [COMPONENTS...] COMMANDS...  [OPTIONS] [INPUTS]
   tosker ls [APPLICATION] [FILTES]
   tosker -h|--help
   tosker -v|--version

Where the placeholders are:

- ``FILE`` is a TOSCA YAML file or CSAR file

-  ``COMMANDS`` are a list of the following commands:

   -  ``create`` Create application components
   -  ``start`` Start applications components
   -  ``stop`` Stop application components
   -  ``delete`` Delete application components (except volume)

-  ``COMPONENTS`` is a list of components to deploy

-  ``OPTIONS``

   -  ``-h --help`` Print usage
   -  ``-q --quiet`` Enable quiet mode
   -  ``--debug`` Enable debugging mode (override quiet mode)
   -  ``-v --version`` Print version

-  ``INPUTS`` provide TOSCA inputs *(syntax: ``--NAME VALUE``)*

- ``FILTER``
   - ``--name <name>`` filter by the component name
   - ``--state <state>`` filter by the state (created, started, deleted)
   - ``--type <type>`` filter by the type (Container, Volume, Software)

- ``APPLICATION`` the application name (CSAR or YAML file without the extension)


Usage Examples
--------------
Those are a set of valid command to be executed with TosKer::

   tosker hello.yaml create start --name mario
   tosker hello.yaml stop delete -q

   tosker hello.yaml database api create start

   tosker ls
   tosker ls hello
   tosker ls hello --type Software --state started
