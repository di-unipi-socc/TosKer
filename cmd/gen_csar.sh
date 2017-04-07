#!/bin/sh

if [ $1 ] && [ $2 ] ;then
  cp $2 $1
  cd $1
  zip -r ../$(basename $1).csar .
else
  exit -1
fi
