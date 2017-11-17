#!/bin/sh

# docker run -it maven:3.2-jdk-8 sh
# git clone https://github.com/microservices-demo/carts.git
# cd /carts
# mvn -q -DskipTests package


git clone https://github.com/microservices-demo/orders.git /orders
cd /orders

# configure endpoint
sed -i "s/\"payment\"/\"$INPUT_PAYMENT\"/g" src/main/java/works/weave/socks/orders/config/OrdersConfigurationProperties.java
sed -i "s/\"shipping\"/\"$INPUT_SHIPPING\"/g" src/main/java/works/weave/socks/orders/config/OrdersConfigurationProperties.java
cat src/main/java/works/weave/socks/orders/config/OrdersConfigurationProperties.java

mvn -DskipTests package
