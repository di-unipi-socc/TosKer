# TosKer

<small>Luca Rinaldi</small>

---

## Software deployment
It is the execution of all the activities that make a software system available to use. <!-- .element: class="fragment" -->

It is now a days strictly related to the cloud infrastructure. <!-- .element: class="fragment" -->

<div>Need a way to express all the **requirements** and **capability** that the application needs to run. </div><!-- .element: class="fragment" -->

Note:
OS, database connection, library to install, programming language, and so on..

---

**How is possible to describe an application?**

---

## Docker
Docker containers wrap up the software and all their requirements: code, runtime, system tools, system libraries. <!-- .element: class="fragment" -->

This guarantees that it will always run in all environment that have Docker. <!-- .element: class="fragment" -->

**Install all the requirements inside a container!** <!-- .element: class="fragment" -->

---

## TOSCA
It is an OASIS standard language to describe a topology of an application, with their components and relationships. <!-- .element: class="fragment" -->

This guarantees that by following the description is possible to replicate the configuration of the application. <!-- .element: class="fragment" -->

**Describe every parts of your application!** <!-- .element: class="fragment" -->

---

## TOSCA vs Docker
Two different approach to resolve the same problem.

**installation** vs **description**

---

## Limitation of Docker
- &#8679; It works out of the box <!-- .element: class="fragment" -->

- &#8679; There are a lot of images ready to be used <!-- .element: class="fragment" -->

- &#8681; Can not deploy complex applications <!-- .element: class="fragment" -->

- &#8681; All have to be a container <!-- .element: class="fragment" -->

---

## Limitation of TOSCA
- &#8679; Well documented standard <!-- .element: class="fragment" -->

- &#8679; Adaptable to every deployment infrastructure <!-- .element: class="fragment" -->

- &#8681; Lack of implementations <!-- .element: class="fragment" -->

- &#8681; To verbose, everything have to be describe <!-- .element: class="fragment" -->

---

## TOSCA + Docker
Why not combine them instead of choose?

---

## TosKer
It is a project that aim to combine **TOSCA** and **Docker** to improve the deployment of the web application on the Cloud.

---

## Feature of TosKer
- Can deploy Docker container and generic software components <!-- .element: class="fragment" -->

- Can deploy complex application <!-- .element: class="fragment" -->

- Use the requirements/capability system of TOSCA <!-- .element: class="fragment" -->

- Can manage networking between components <!-- .element: class="fragment" -->

---

## How it works
1. The application is described using the TOSCA yaml language. <!-- .element: class="fragment" -->

2. The TOSCA file is validated and parsed <!-- .element: class="fragment" -->

3. The deployment order is computed <!-- .element: class="fragment" -->

4. The deployments is executed by using Docker <!-- .element: class="fragment" -->

---

## Custom Types
TosKer support only a set of TOSCA types:

- Docker persistent container `tosker.docker.container.persistent`

- Docker container `tosker.docker.container`

- Docker volume `tosker.docker.volume`

- Software `tosker.software`

---

## Type of relationship
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

## How use it
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
