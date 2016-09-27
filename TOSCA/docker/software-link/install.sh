#!/bin/sh
while [ $# -gt 1 ]; do
key="$1"
case $key in
    --main)
      MAIN_FILE="$2"
      shift
    ;;
    --package)
      PACKAGE="$2"
      shift
    ;;
    *)
      exit -1
    ;;
esac
shift # past argument or value
done

cp $PACKAGE .
npm install
node $MAIN_FILE
