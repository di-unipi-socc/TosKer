#!/bin/sh
git clone -b $INPUT_BRANCH $INPUT_REPO /thinking-api
cd /thinking-api
mvn clean install
