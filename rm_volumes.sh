#!/bin/sh
docker volume rm $(docker volume ls --filter dangling=true)
