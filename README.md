<p align="center">
  <img src="data/img/logo/tosker-logo.png" />
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

## Table of Contents
- [Quick Guide](#quick-guide)
  * [Installation](#installation)
  * [Example of usage](#example-of-usage)
- [License](#license)

## Quick Guide

### Installation
TosKer requires having [Docker](https://www.docker.com) installed and configured on the machine. In is possible to install TosKer by using pip:
```
# pip install tosker
```
The minimum Python version supported is 2.7. It is possible to find other installation methods on the documentation.

### Example of usage
After the installation it is possible to use TosKer to deploy some example application. First of all download the TosKer repository and go on the example folder:

```
$ git clone https://github.com/di-unipi-socc/TosKer.git
$ cd TosKer/data/examples
```

We can now try to deploy the Thinking application, to do so we can go on the `thinking-app` and execute the `thinking.up.plan`. The `thinking.up.plan` will put all the components of the Thinking application on the running state.
```
$ cd thinking-app
$ tosker exec thinking.csar --plan thinking.up.plan
```
After the command TosKer execute the plan on the topology and the Thinking application will be up and running. The application will be accessible on the `http://localhost:8080` url. More using the command `ls` it is possible to show the state of the components of the application:
```
$ tosker ls
```

Now suppose that we want to delete the *GUI* application we can run the command:
```
$ tosker exec thinking.csar gui:Standard.stop gui:Standard.delete
```
In this way we can instruct tosker to execute single operation on the topology without issuing a complete plan. Using the `ls` command again will show that the component *GUI* is deleted.

At this point if we want to delete all the component of the Thinking application except the *GUI*, which is already in the deleted state, we can exploit the `thinking.down.plan`. Indeed, we can remove the first 2 line, the one with the operation to delete the *GUI* component, with the `tail` command and pipe the result to TosKer. Thus, we can execute the following:
```
$ tail -n +3 thinking.down.plan | tosker exec thinking.csar -

```


## License

MIT license
