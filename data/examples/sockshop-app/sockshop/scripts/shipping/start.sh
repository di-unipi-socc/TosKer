#!/bin/sh


# export JAVA_OPTS="-Djava.security.egd=file:/dev/urandom"

java -Djava.security.egd=file:/dev/urandom -jar $INPUT_JAR --port=$INPUT_PORT


# echo $JAVA_OPTS
