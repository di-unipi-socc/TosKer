#!/bin/sh
# echo $@
#
/go/src/github.com/microservices-demo/user/bin/user -port=$INPUT_PORT -database=$INPUT_DATABASE -mongo-host=${INPUT_MONGOHOST}
# /go/src/github.com/microservices-demo/user/bin/user -port=8080 -database=mongodb -mongo-host=localhost:27017
