# TosKer
[![pipy](https://img.shields.io/pypi/v/tosker.svg)](https://pypi.python.org/pypi/tosker)
[![travis](https://travis-ci.org/di-unipi-socc/TosKer.svg?branch=master)](https://travis-ci.org/di-unipi-socc/TosKer)
[![docs](https://readthedocs.org/projects/tosker/badge/?version=latest)](http://tosker.readthedocs.io/en/latest/?badge=latest)
<!-- [![Updates](https://pyup.io/repos/github/lucarin91/tosker/shield.svg)](https://pyup.io/repos/github/lucarin91/tosker/) -->

TosKer is an orchestrator engine capable of automatically deploying and managing multi-component applications specifies in OASIS TOSCA on Docker.

- [Documentation](https://new-tosker.readthedocs.io)
- [Presentation Slids](https://github.com/lucarin91/TosKer-slides)

## Installation
TosKer requires having [Docker](https://www.docker.com) installed and configured on the machine. In is possible to install TosKer by using pip:
```
# pip install tosker
```
The minimum Python version supported is 2.7. It is possible to find other installation methods on the documentation.

## Quick Guide
After the installation it is possible to found in `/usr/share/tosker/examples` the CSAR of two example application, `node-mongo.casr` and `thoughts.csar`.

To `create` and `start` the thoughts application run the command:
```
tosker /usr/share/tosker/examples/thoughts.csar create start
```

It is possible to use the `ls` command to check that all the components are in the `started` state:

```
tosker ls
```

Now, the application can be accessible on `http://127.0.0.1:8080/thoughts.html`.
Finally, to `stop` and `delete` the application run the command:
```
tosker /usr/share/tosker/examples/thoughts.csar stop delete
```

## License

MIT license
