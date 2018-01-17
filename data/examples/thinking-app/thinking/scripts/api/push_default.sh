#!/bin/bash
data_csv=$INPUT_DATA
port=$INPUT_PORT
base_url="http://localhost:$port/thoughts"
abs_path=$(cd $(dirname $0) && pwd)

# start the API and wait that it is booted up
sh $abs_path/start.sh&
sleep 2

# load data from the csv and push it to API
while IFS=\; read -r col1 col2 col3
do
    curl -GX POST $base_url --data-urlencode "thought=$col1"\
                            --data-urlencode "author=$col2"\
                            --data-urlencode "location=$col3"
done < $data_csv

# stop the API
sh $abs_path/stop.sh