#!/bin/sh

if [ $1 ] ;then
  cd $1

  zip -r ../$(basename $1).csar .
else
  exit -1
fi
