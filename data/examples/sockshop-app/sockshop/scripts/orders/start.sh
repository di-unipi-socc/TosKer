#!/bin/sh

# java -Djava.security.egd=file:/dev/urandom -jar $INPUT_JAR --port=$INPUT_PORT #-db=cart-db

java -Ddebug -Djava.security.egd=file:/dev/urandom -jar /orders/target/orders.jar --port=$INPUT_PORT&

# java -jar $INPUT_JAR --port=$INPUT_PORT --shipping_endpoint=$INPUT_SHIPPING --payment_endpoint=$INPUT_PAYMENT
