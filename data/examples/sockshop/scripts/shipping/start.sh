#!/bin/sh


# export JAVA_OPTS="-Djava.security.egd=file:/dev/urandom"

/usr/local/bin/java.sh -jar $INPUT_JAR --port=$INPUT_PORT


echo $JAVA_OPTS
