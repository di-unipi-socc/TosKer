#!/bin/sh
apt-get remove -y mongodb-org
apt-get autoremove
apt-get clean

rm -rf /db
