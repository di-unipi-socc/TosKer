#!/bin/sh
java -Djava.security.egd=file:/dev/urandom -jar $INPUT_JAR --port=$INPUT_PORT&