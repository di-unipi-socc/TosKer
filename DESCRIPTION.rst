TosKer
======

TosKer is an orchestrator engine capable of automatically deploying and
managing multi-component applications specifies in `OASIS
TOSCA <https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=tosca>`__,
by exploiting `Docker <https://www.docker.com>`__ as a lightweight
virtualization framework. The novelty of TosKer is to decouple the
application-specific components, from the containers used to build their
infrastructure. This permits to improve the orchestration of the
components and to ease the change of the containers underneath.

-  `Documentation <https://tosker.readthedocs.io>`__
-  `Presentation Slids <https://github.com/lucarin91/TosKer-slides>`__

Installation
------------

TosKer requires having `Docker <https://www.docker.com>`__ installed and
configured on the machine. In is possible to install TosKer by using
pip:

::

    # pip install tosker

The minimum Python version supported is 2.7. It is possible to find
other installation methods on the documentation.

Quick Guide
-----------

After the installation it is possible to found in
``/usr/share/tosker/examples`` the CSAR of two example application,
``node-mongo.casr`` and ``thoughts.csar``.

To ``create`` and ``start`` the thoughts application run the command:

::

    tosker /usr/share/tosker/examples/thoughts.csar create start

It is possible to use the ``ls`` command to check that all the
components are in the ``started`` state:

::

    tosker ls

Now, the application can be accessible on
``http://127.0.0.1:8080/thoughts.html``. Finally, to ``stop`` and
``delete`` the application run the command:

::

    tosker /usr/share/tosker/examples/thoughts.csar stop delete

License
-------

MIT license
