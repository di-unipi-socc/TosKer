#!/bin/sh

#/go/src/github.com/microservices-demo/user/bin/user -port=$INPUT_PORT -database=$INPUT_DATABASE -mongo-host=${INPUT_MONGOHOST}
user -port=$INPUT_PORT -database=$INPUT_DATABASE -mongo-host=${INPUT_MONGOHOST}
