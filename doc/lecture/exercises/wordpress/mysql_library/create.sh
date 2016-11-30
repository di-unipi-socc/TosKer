#!/bin/sh
apt-get update
apt-get install php5-mysql libmcrypt-dev
docker-php-ext-install mysqli pdo pdo_mysql mcrypt
