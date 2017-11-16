#!/bin/sh

# Users isntall script
# go get -u github.com/microservices-demo/user
# cd  ./src/github.com/microservices-demo/user
# // make build


# golang:1.7-alpine
go get -u github.com/microservices-demo/user
go get -v github.com/Masterminds/glide
cd src/github.com/microservices-demo/user
glide install
go install

echo $HATEAOS
