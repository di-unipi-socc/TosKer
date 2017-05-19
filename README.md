# TosKer
TosKer is an orchestrator engine capable of automatically deploying and managing multi-component applications specifies in OASIS TOSCA on Docker.

## Installation
**Requirements**
- python>=2.7
- pip

```
sudo pip install tosker
```
After the installation it is possible to found in `/usr/share/tosker/examples` the CSAR of two example application, `node-mongo.casr` and `thoughts.csar`.

To create and start the thoughts application run the command:
```
tosker /usr/share/tosker/examples/thoughts.csar create start
```
Then the application can be accessible on `http://127.0.0.1:8080/thoughts.html`

To stop and delete the application run the command:
```
tosker /usr/share/tosker/examples/thoughts.csar stop delete
```

### Install from source
```
git clone https://github.com/di-unipi-socc/tosKer/tree/master
cd tosKer
sudo python setup.py install
```

Run the tests:
```
./scripts/run_tests.sh
```

## Usage details
```
tosker FILE [COMPONENTS...] COMMANDS... [OPTIONS] [INPUTS]
tosker -h|--help
tosker -v|--version
```
Where
- `FILE` is a TOSCA YAML file or CSAR file

- `COMMANDS` are a list of the following commands:
    - `create` Create application components
    - `start` Start applications components
    - `stop` Stop application components
    - `delete` Delete application components (except volume)

- `COMPONENTS` is a list of components to deploy

- `OPTIONS`
    - `-h --help`      Print usage
    - `-q --quiet`     Enable quiet mode
    - `--debug`        Enable debugging mode (override quiet mode)
    - `-v --version`   Print version

- `INPUTS` provide TOSCA inputs _(syntax: `--NAME VALUE`)_

Examples:
```
tosker hello.yaml create --name mario
tosker hello.yaml start -q
tosker hello.yaml stop --debuug
tosker hello.yaml delete

tosker hello.yaml create start --name mario
tosker hello.yaml stop delete -q

tosker hello.yaml database api create start
```
