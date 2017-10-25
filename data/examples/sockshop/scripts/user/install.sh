#!/bin/sh
go get -u github.com/microservices-demo/user
cd  ./src/github.com/microservices-demo/user
make build
