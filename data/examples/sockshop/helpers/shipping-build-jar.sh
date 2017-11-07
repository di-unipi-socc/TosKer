#!/bin/sh

git clone  https://github.com/microservices-demo/shipping.git

cd \shipping && mvn -q -DskipTests package

cp target/shipping.jar ../../artifacts

cd .. && rm -rf shipping/
