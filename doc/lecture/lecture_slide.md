# TosKer

<small>Luca Rinaldi</small>

---

## Software deployment
The execution of all the activities that make a software system available to use. <!-- .element: class="fragment" -->

Nowadays strictly related to the cloud infrastructure. <!-- .element: class="fragment" -->

<div>Need of a way to express all the **requirements** and **capability** that the application needs to run. </div><!-- .element: class="fragment" -->

Note:
OS, database connection, library to install, programming language, and so on..

---

**How to describe an application?**

---

## Docker
Docker containers wrap up the software and all their requirements: code, runtime, system tools, system libraries. <!-- .element: class="fragment" -->

This guarantees that they will always run in all environment that support Docker. <!-- .element: class="fragment" -->

**Embed all the requirements inside a container!** <!-- .element: class="fragment" -->

---

## TOSCA
OASIS standard language to describe the topology of an application, with its components and relationships. <!-- .element: class="fragment" -->

Following the description it is possible to replicate the configuration of the application. <!-- .element: class="fragment" -->

**Describe every part of your application!** <!-- .element: class="fragment" -->

---

## TOSCA vs. Docker
Two different approach to resolve the same problem.

**installation** vs **description**

---

## Pros and Cons of Docker
- &#8679; It works out of the box <!-- .element: class="fragment" -->

- &#8679; There are a lot of images ready to be used <!-- .element: class="fragment" -->

- &#8681; Cannot deploy complex applications <!-- .element: class="fragment" -->

- &#8681; Everything must be a container <!-- .element: class="fragment" -->

---

## Pro and Cons of TOSCA
- &#8679; Well documented standard <!-- .element: class="fragment" -->

- &#8679; Adaptable to every deployment infrastructure <!-- .element: class="fragment" -->

- &#8681; Lack of implementations <!-- .element: class="fragment" -->

- &#8681; Too verbose, everything must be described <!-- .element: class="fragment" -->

---

## TOSCA + Docker
Why not combining them instead of choosing?

---

## TosKer
Project that aims to combine **TOSCA** and **Docker** to improve the deployment of applications on the Cloud.

---

## Features of TosKer
- Can deploy Docker container and generic software components <!-- .element: class="fragment" -->

- Can deploy complex applications <!-- .element: class="fragment" -->

- Uses the requirements/capability system of TOSCA <!-- .element: class="fragment" -->

- Can manage networking between components <!-- .element: class="fragment" -->

---

## How it works
1. The application is described using the TOSCA yaml language. <!-- .element: class="fragment" -->

2. The TOSCA file is validated and parsed <!-- .element: class="fragment" -->

3. The deployment order is computed <!-- .element: class="fragment" -->

4. The deployment is executed using Docker <!-- .element: class="fragment" -->

---

## Custom Types
TosKer support only a set of TOSCA types:

- Docker persistent container `tosker.docker.container.persistent`

- Docker container `tosker.docker.container`

- Docker volume `tosker.docker.volume`

- Software `tosker.software`

---

## Types of relationship
![container_type](img/Tosker_types_legend.png) <!-- .element: style="border: 0;background: 0; box-shadow:0 0;" -->

- host `tosca.relationships.AttachesTo`

- connect `tosca.relationships.ConnectsTo`

- depend `tosca.relationships.DependsOn`

- attach `tosca.relationships.AttachesTo`

---

### Docker container
![container_type](img/Tosker_types_container.png) <!-- .element: style="border: 0;background: 0; box-shadow:0 0;" -->

```yaml
my_container:
  type: tosker.docker.container
  properties:
    ports:
      80: 8000
  artifacts:
    my_image:
      file: ubuntu:16.04
      type: tosker.docker.image
      repository: docker_hub
```
---

### Docker volume
![container_type](img/Tosker_types_volume.png) <!-- .element: style="border: 0;background: 0; box-shadow:0 0;" -->

```yaml
my_volume:
  type: tosker.docker.volume
  properties:
    driver: local
    size: 200m
```

---

### Software type
![container_type](img/Tosker_types_software.png) <!-- .element: style="border: 0;background: 0; box-shadow:0 0;" -->

```yaml
my_software:
  type: tosker.software
  interfaces:
    Standard:
      create:
        implementation: create.sh
      configure:
        implementation: configure.sh
      start:
        implementation: start.sh
      stop:
        implementation: stop.sh
      delete:
        implementation: delete.sh
```
---

## An example
![example](img/Tosker_types_example.png) <!-- .element: style="border: 0;background: 0; box-shadow:0 0;" -->
___

### TOSCA specification
```yaml
node_templates:
  web_app:
    type: tosker.software
    artifacts:
      ...
    requirements:
      - host: node_container
      - connect: db
    interfaces:
      Standard:
        create:
          implementation: app/install.sh
        start:
          implementation: app/start.sh

  db:
    type: tosker.software
    requirements:
      - host: ubuntu_container
    interfaces:
      Standard:
        create:
          implementation: mongo/install.sh
        start:
          implementation: mongo/start.sh

  node_container:
    type: tosker.docker.container
    properties:
      ports:
        80: 8080
    artifacts:
      my_image:
        file: node:6
        type: tosker.docker.image
        repository: docker_hub

  ubuntu_container:
    type: tosker.docker.container
    artifacts:
      my_image:
        file: ubuntu16.04
        type: tosker.docker.image
        repository: docker_hub
```

---

## How to use it
```
tosker <file> (create|start|stop|delete)... [<inputs>...]
```

Options:
```
-h --help     Show this help.
-q --quiet    Active quiet mode.
--debug       Active debugging mode.
```

Examples:
```
tosker app.yaml create start
tosker app.yaml stop delete
```

---

# Demo
