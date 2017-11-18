#!/bin/sh
docker rm -fv $(docker ps -aq)
