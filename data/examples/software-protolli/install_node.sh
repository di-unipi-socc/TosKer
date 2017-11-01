#!/bin/sh
apt-get update
apt-get install nodejs npm -y
apt-get clean
ln -s /usr/bin/nodejs /usr/bin/node
