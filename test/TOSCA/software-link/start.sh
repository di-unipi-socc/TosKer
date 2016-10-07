#!/bin/sh
echo "$@"
while [ $# -gt 1 ]; do
key="$1"
case $key in
    --main)
      MAIN_FILE="$2"
      shift
    ;;
    --port)
      PORT_ARG="$2"
      shift
    ;;
esac
shift # past argument or value
done

export PORT=$PORT_ARG
node $MAIN_FILE
