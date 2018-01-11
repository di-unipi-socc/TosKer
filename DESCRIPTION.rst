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