#!/bin/sh

TARGET=thoughts-api/api-config.yml

echo dbURL: '"'$INPUT_DBURL'"' > $TARGET
echo dbPort: '"'$INPUT_DBPORT'"' >> $TARGET
echo dbName: '"'thoughtsSharing'"' >> $TARGET
echo collectionName: '"'thoughts'"' >> $TARGET

cat $TARGET
