#!/bin/sh

# Payment installation script
go get  github.com/microservices-demo/payment/
go get -u github.com/FiloSottile/gvt
cd /go/src/github.com/microservices-demo/payment/

gvt restore

CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o /app/main github.com/microservices-demo/payment/cmd/paymentsvc
