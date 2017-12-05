#!/bin/sh

TARGET=/thinking-api/api-config.yml

echo dbURL: '"'$INPUT_DBURL'"' > $TARGET
echo dbPort: '"'$INPUT_DBPORT'"' >> $TARGET
echo dbName: '"'$INPUT_DBNAME'"' >> $TARGET
echo collectionName: '"'$INPUT_COLLECTIONNAME'"' >> $TARGET
