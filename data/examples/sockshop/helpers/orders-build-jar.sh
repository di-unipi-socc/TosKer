#!/bin/sh

git clone  https://github.com/microservices-demo/orders.git

cd \orders && mvn -DskipTests package

cp target/orders.jar ../../artifacts

cd .. && rm -rf orders/
