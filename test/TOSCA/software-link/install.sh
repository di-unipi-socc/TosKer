#!/bin/sh
echo "$@"
while [ $# -gt 1 ]; do
key="$1"
case $key in
    --package)
      PACKAGE="$2"
      shift
    ;;
esac
shift # past argument or value
done

cp $PACKAGE .
npm install
