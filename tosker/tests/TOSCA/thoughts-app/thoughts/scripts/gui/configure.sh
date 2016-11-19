#!/bin/sh

TARGET=thoughts-gui/public/script/config/rest-api.js

echo apiUrl='"'$INPUT_APIURL'"' > $TARGET
echo apiPort='"'$INPUT_APIPORT'"' >> $TARGET
echo apiResource='"'$INPUT_APIRESOURCE'"' >> $TARGET

cat $TARGET
