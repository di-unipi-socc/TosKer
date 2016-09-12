#!/bin/sh
docker stop $(docker ps -q -a)
docker rm -v $(docker ps -q -a) 
