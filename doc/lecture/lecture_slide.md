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
TosKer support only those custom types:

- Docker persistent container *tosker.docker.container.persistent*<!--.element: style="font-size:20pt;"-->

- Docker container *tosker.docker.container*<!--.element: style="font-size:20pt;"-->

- Docker volume *tosker.docker.volume* <!--.element: style="font-size:20pt;"-->

- Software *tosker.software*<!--.element: style="font-size:20pt;"-->

---

## Types of relationship
![container_type](img/Tosker_legend.png) <!-- .element: style="border: 0;background: 0; box-shadow:0 0;" -->

Tosker support all the normative relationship:

- host *tosca.relationships.AttachesTo* <!--.element: style="font-size:20pt;"-->

- connect *tosca.relationships.ConnectsTo* <!--.element: style="font-size:20pt;"-->

- depend *tosca.relationships.DependsOn* <!--.element: style="font-size:20pt;"-->

- attach *tosca.relationships.AttachesTo*<!--.element: style="font-size:20pt;"-->

---

## Docker container
![container_type](img/Tosker_types_container.png) <!-- .element: style="border: 0;background: 0; box-shadow:0 0;" -->

___

### Definition

```yaml
tosker.docker.container:
  derived_from: tosca.nodes.Container.Runtime
  properties:
    ports:
      type: map
      required: false
  requirements:
    - attach:
        capability: tosca.capabilities.Attachment
        occurrences: [0, UNBOUNDED]
  capabilities:
    host:
      type: tosca.capabilities.Container
      valid_source_types: [tosker.software]
      occurrences: [0, UNBOUNDED]
```
___

### Example
```yaml
my_container:
  type: tosker.docker.container
  requirements:
    - attach: my_volume
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

## Docker Persistent Container
![container_type](img/Tosker_types_persistent_container.png) <!-- .element: style="border: 0;background: 0; box-shadow:0 0;" -->

___

### Definition

```yaml
tosker.docker.container.persistent:
  derived_from: tosker.docker.container
  properties:
    env_variable:
      type: map
      required: false
    ...
  requirements:
    - connect:
        capability: tosca.capabilities.Endpoint
        occurrences: [0, UNBOUNDED]
    - depend:
        capability: tosca.capabilities.Node
        occurrences: [0, UNBOUNDED]
  capabilities:
    connect:
      type: tosca.capabilities.Endpoint
      valid_source_types: [tosker.software, tosker.docker.container.persistent]
      occurrences: [0, UNBOUNDED]
    depend:
      type: tosca.capabilities.Node
      valid_source_types: [tosker.software, tosker.docker.container.persistent]
      occurrences: [0, UNBOUNDED]
```
___

### Example

```yaml
my_container:
  type: tosker.docker.container.persistent
  requirements:
    - connect: my_other_container
    - depend: my_other_software
    - attach: my_volume
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

## Docker volume
![container_type](img/Tosker_types_volume.png) <!-- .element: style="border: 0;background: 0; box-shadow:0 0;" -->

___

### Definition
```yaml
tosker.docker.volume:
  derived_from: tosca.nodes.BlockStorage
  properties:
    driver: # by default it is local
      type: string
      required: false
    size: # restrict to a given size. for example: 100m
      type: string
      required: false
    ...
  capabilities:
    attach:
      type: tosca.capabilities.Attachment
      valid_source_types: [tosker.docker.container.persistent, tosker.docker.container]
      occurrences: [0, UNBOUNDED]
```
___

### Example

```yaml
my_volume:
  type: tosker.docker.volume
  properties:
    driver: local
    size: 200m
```

---

## Software type
![container_type](img/Tosker_types_software.png) <!-- .element: style="border: 0;background: 0; box-shadow:0 0;" -->

___

### Definition

```yaml
tosker.software:
  derived_from: tosca.nodes.SoftwareComponent
  requirements:
    - connect:
        capability: tosca.capabilities.Endpoint
        occurrences: [0, UNBOUNDED]
    - depend:
        capability: tosca.capabilities.Node
        occurrences: [0, UNBOUNDED]
    - host:
        capability: tosca.capabilities.Container
        occurrences: 1
  capabilities:
    host:
      type: tosca.capabilities.Container
      valid_source_types: [tosker.software]
      occurrences: [0, UNBOUNDED]
    connect:
      type: tosca.capabilities.Endpoint
      valid_source_types: [tosker.software, tosker.docker.container.persistent]
      occurrences: [0, UNBOUNDED]
    depend:
      type: tosca.capabilities.Node
      valid_source_types: [tosker.software, tosker.docker.container.persistent]
      occurrences: [0, UNBOUNDED]

```
___

### Example

```yaml
my_software:
  type: tosker.software
  requirements:
    - connect: my_other_software
    - depend: my_other_software
    - host: my_container
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

## An example: Thoughts
![example](img/Tosker_example.png) <!-- .element: style="border: 0;background: 0; box-shadow:0 0;" -->

___

### TOSCA specification
```yaml
tosca_definitions_version: tosca_simple_yaml_1_0

description: TOSCA description of the Thoughts application.

repositories:
  docker_hub: https://registry.hub.docker.com/

imports:
  - tosker: https://di-unipi-socc.github.io/tosker-types/0.0.5/tosker.yaml

topology_template:
  inputs:
    app_port:
      type: integer
      default: 8080
      description: the application port
    api_port:
      type: integer
      default: 8000
      description: the API port

  node_templates:
    api:
      type: tosker.software
      requirements:
        - host: maven_container
        - connect: db_container
      interfaces:
        Standard:
          create:
            implementation: scripts/api/install.sh
          configure:
            implementation: scripts/api/configure.sh
          start:
            implementation: scripts/api/start.sh
          stop:
            implementation: scripts/api/stop.sh
          delete:
            implementation: scripts/api/uninstall.sh

    gui:
      type: tosker.software
      requirements:
        - host: node_container
        - depend: api
      interfaces:
        Standard:
          create:
            implementation: scripts/gui/install.sh
          configure:
            implementation: scripts/gui/configure.sh
          start:
            implementation: scripts/gui/start.sh
          stop:
            implementation: scripts/gui/stop.sh
          delete:
            implementation: scripts/gui/uninstall.sh

    maven_container:
      type: tosker.docker.container
      properties:
        ports:
          8080: { get_input: api_port }
      artifacts:
        my_image:
          file: maven:3.3-jdk-8
          type: tosker.docker.image
          repository: docker_hub

    node_container:
      type: tosker.docker.container
      properties:
        ports:
          3000: { get_input: app_port }
      artifacts:
        my_image:
          file: node:6
          type: tosker.docker.image
          repository: docker_hub

    db_container:
      type: tosker.docker.container.persistent
      artifacts:
        my_image:
          file: mongo:3.4
          type: tosker.docker.image
          repository: docker_hub
      requirements:
        - attach:
            node: db_volume
            relationship:
              type: tosca.relationships.AttachesTo
              properties:
                location: /data/db

    db_volume:
      type: tosker.docker.volume
```

---

## How to use TosKer
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
