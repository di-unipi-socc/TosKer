=======
History
=======

0.4.0 (2017-07-10)
------------------

* First release on PyPI.


1.0.0 (2017-11-20)
----------------------------
Stable release without Management Protocols.

* Add command log, to show the execution of an operation on a component.
* Add command prune, to remove all TosKer files and restore initial state.
* Improve memory management.
* Improve command line interface.
* Bug fix.


2.0.0 (2017-12-09)
----------------------------
* Switch to Management Protocols to manage the life cycle of the components
* Add support for derived node types.
* Add support for custom interfaces.
* Support custom management protocol defined using policies.
* Support safe execution of plans (list of <component, interface, operation>).
* Improve command line interface.