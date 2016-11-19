#!/bin/sh
docker rmi $(docker images | grep -vE 'mysql |ubuntu |node |wordpress |mongo |rabbitmq |maven ')
