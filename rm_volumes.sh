#!/bin/sh
docker volume rm -f $(docker volume ls --filter dangling=true)
