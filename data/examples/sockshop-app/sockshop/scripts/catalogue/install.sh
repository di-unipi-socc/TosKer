#!/bin/sh

go get -u github.com/microservices-demo/catalogue
go get -u github.com/FiloSottile/gvt
cd /go/src/github.com/microservices-demo/catalogue && gvt restore

cp -r  /go/src/github.com/microservices-demo/catalogue/images/ /go/images

CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o /app/catalogue ./cmd/cataloguesvc
