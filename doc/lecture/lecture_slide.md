# TosKer

<small>Luca Rinaldi</small>

note:
In this seminar we talk TosKer that is a project that I'm working right now for my thesis. It's a tool that use the capability of Docker and TOSCA to acchive a better system of application deployment. So first of all we talk about..

---

## Software deployment

It is all the activity that make a software system available to use.

It is now a days strictly related to the cloud.

It is important to find system to express all the requirements and capability that the software need to run (database connection, library to install, ecc..)

---

**How can I describe my application?**

---

## Docker

> Docker containers wrap up a piece of software in a complete filesystem that contains everything it needs to run: code, runtime, system tools, system libraries – anything you can install on a server. This guarantees that it will always run the same, regardless of the environment it is running in.

Installing all the requirements inside a container!

---

## TOSCA
It is an OASIS standard language to describe a topology of an application, with their components and relationships.

Describe your application including all the libraries and software that you need!

---

## TOSCA vs Docker
Two different approach to resolve the same problem.

**installation** vs **description**

---

## Limitation of Docker
- &#8679; It works out of the box

- &#8679; There are a lot of images ready to be used

- &#8681; Can not deploy complex applications

- &#8681; All have to be a container

---

## Limitation of TOSCA
- &#8679; Well documented standard

- &#8679; Adaptable to every deployment infrastructure

- &#8681; Lack of implementations

- &#8681; To verbose everything have to be describe

---

## TOSCA + Docker
Why not combine them instead of choose?

## TosKer
It is a project that aim to combine **TOSCA** and **Docker** to improve the deployment of the web application on the Cloud.

---

## Feature of TosKer
- Can deploy Docker container and generic software components

- Can deploy complex application

- use the requirements/capability system of TOSCA

- Can manage networking between components

---

## How it works
The application is described using the TOSCA yaml language.

The TOSCA file validated and parsed

Is computed the deployment order of the components

The deployments is done by using the Docker

---

## Custom Types
TosKer support only a set of TOSCA types:

- Docker container `tosker.docker.container`

- Docker volume `tosker.docker.volume`

- Software `tosker.software`

---

## Type of relationship
Each components can express a set of relationship:

- host `tosca.relationships.AttachesTo`

- connect `tosca.relationships.ConnectsTo`

- depend `tosca.relationships.DependsOn`

- attach `tosca.relationships.AttachesTo`

---

### Docker container
![container_type](img/Tosker_types_container.png)

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
![container_type](img/Tosker_types_volume.png)

```yaml
my_volume:
  type: tosker.docker.volume
  properties:
    driver: local
    size: 200m
```

---

### Software type
![container_type](img/Tosker_types_software.png)

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

---


## How use it


---

# Demo
