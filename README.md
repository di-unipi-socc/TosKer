<p align="center">
  <img src="logo/tosker-logo.png" />
</p>

-------

[![pipy](https://img.shields.io/pypi/v/tosker.svg)](https://pypi.python.org/pypi/tosker)
[![travis](https://travis-ci.org/di-unipi-socc/TosKer.svg?branch=master)](https://travis-ci.org/di-unipi-socc/TosKer)
[![docs](https://readthedocs.org/projects/tosker/badge/)](http://tosker.readthedocs.io/en/latest)
<!-- [![Updates](https://pyup.io/repos/github/lucarin91/tosker/shield.svg)](https://pyup.io/repos/github/lucarin91/tosker/) -->

TosKer is an orchestrator engine capable of automatically deploying and managing multi-component applications specified in [OASIS TOSCA](https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=tosca), by exploiting [Docker](https://www.docker.com) as a lightweight virtualization framework.
It was first presented in 
> _A. Brogi, L. Rinaldi, J. Soldani <br>
> **TosKer: Orchestrating applications with TOSCA and Docker.** <br>
> Submitted for publication_ 

If you wish to reuse the tool or the sources contained in this repository, please properly cite the above mentioned paper. Below you can find the BibTex reference:
```
@misc{TosKer,
  author = {Antonio Brogi and Luca Rinaldi and Jacopo Soldani},
  title = {{TosKer}: Orchestrating applications with {TOSCA} and {D}ocker},
  editor={Zoltán Ádám Mann, Volker Stolz},
  bookTitle={Advances in Service-Oriented and Cloud Computing: Workshops of ESOCC 2017},
  publisher={Springer},
  note={{\em [In press]}}
}
```

The documentation of TosKer can be found [here](https://tosker.readthedocs.io).

## Quick Guide

### Installation
TosKer requires having [Docker](https://www.docker.com) installed and configured on the machine. In is possible to install TosKer by using pip:
```
# pip install tosker
```
The minimum Python version supported is 2.7. It is possible to find other installation methods on the documentation.

### Example of usage
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
