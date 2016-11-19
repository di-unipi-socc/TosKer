#!/bin/sh

git clone -b $INPUT_BRANCH $INPUT_REPO thoughts-api
cd thoughts-api/
mvn clean install
