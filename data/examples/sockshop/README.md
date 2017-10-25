

## SockerShop microservice demo application

**Sock Shop** simulates the user-facing part of an e-commerce website that sells socks.
It is intended to aid the demonstration and testing of microservice and cloud native technologies.

  - [SockeShop site](https://microservices-demo.github.io/)
  - [Github repo](https://github.com/microservices-demo)


## Architecture

Sockshop is built using:
    - Spring Boot,
    - [Go kit](http://gokit.io/): A toolkit for microservices
    - Node.js

and is packaged in Docker containers.

![Architecture diagram](Architecture.png)

The architecture of the demo microserivces application was intentionally designed to provide as many microservices as possible. If you are considering your own design, we would recommend the iterative approach, whereby you only define new microservices when you see issues (performance/testing/coupling) developing in your application.

Furthermore, it is intentionally polyglot to exercise a number of different technologies. Again, we'd recommend that you only consider new technologies based upon a need.

As seen in the image above, the microservices are roughly defined by the function in an ECommerce site. Networks are specified, but due to technology limitations may not be implemented in some deployments.

All services communicate using REST over HTTP. This was chosen due to the simplicity of development and testing. Their API specifications are under development.


## architecture requiremetns

- *front-end*: require `npm:2.15.11` `mode:4.8.x`


## user

``` $ /user -h
Usage of /user:
  -database string
    	Database to use, Mongodb or ... (default "mongodb")
  -link-domain string
    	HATEAOS link domain (default "user")
  -mongo-host string
    	Mongo host (default "user-db")
  -mongo-password string
    	Mongo password
  -mongo-user string
    	Mongo user
  -port string
    	Port on which to run (default "8084")
  -zipkin string
    	Zipkin address
```

## orders

`java.sh` script launched inside the `weaveworksdemos/msd-java:8u131` for running the `orders` Software.

``` /usr/local/bin # cat java.sh
#!/bin/sh

if [ -z "$JAVA_OPTS" ]; then
  JAVA_OPTS="-XX:+UnlockExperimentalVMOptions -XX:+UseCGroupMemoryLimitForHeap -XX:MaxRAMFraction=1 -XX:UseG1GC"
fi
```
