#!/bin/sh
apt-get remove -y mongodb-org
apt-get clean

rm -rf /db
