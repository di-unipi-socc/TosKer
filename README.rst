tosKer
======

`Slides <http://slideck.io/github.com/di-unipi-socc/tosKer/doc/slide.md>`__

Intallation
-----------

**Requirements** - python>=2.7 - pip

::

    sudo pip install tosker

Usage:

::

    tosker <file> (create|start|stop|delete)... [<inputs>...]
    tosker <file> (create|start|stop|delete)... -q|--quiet [<inputs>...]
    tosker <file> (create|start|stop|delete)... --debug [<inputs>...]
    tosker -h|--help

Options:

::

    -h --help     Show this help.
    -q --quiet    Active quiet mode.
    --debug       Active debugging mode.

Examples:

::

    tosker tosker/test/TOSCA/wordpress.yaml create --name mario
    tosker tosker/test/TOSCA/wordpress.yaml start -q
    tosker tosker/test/TOSCA/wordpress.yaml stop --debuug
    tosker tosker/test/TOSCA/wordpress.yaml delete

    tosker tosker/test/TOSCA/wordpress.yaml create start --name mario
    tosker tosker/test/TOSCA/wordpress.yaml stop delete -q

Install from source
~~~~~~~~~~~~~~~~~~~

::

    git clone https://github.com/di-unipi-socc/tosKer/tree/master
    cd tosKer
    sudo python setup.py install

Run the tests:

::

    python setup.py test
