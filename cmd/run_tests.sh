#!/bin/sh
TEST_LOG="/tmp/tosker_$(date +'%F_%T').test"
echo '' > $TEST_LOG

if [ ! -d "venv2" ]; then
  virtualenv venv2 -p python2
fi

if [ ! -d "venv3" ]; then
  virtualenv venv3 -p python3
fi

# test on python2
echo 'TEST PYTHON2' >> $TEST_LOG
. ./venv2/bin/activate
pip install -r requirements.txt &> /dev/null
python -m unittest discover -v 2>> $TEST_LOG
deactivate

# test on python3
echo "\nTEST PYTHON3" >> $TEST_LOG
. ./venv3/bin/activate
pip install -r requirements.txt &> /dev/null
python -m unittest discover -v 2>> $TEST_LOG
deactivate

# coverage
echo "\nCOVERAGE" >> $TEST_LOG
. ./venv3/bin/activate
coverage run --source tosker -m unittest discover 2> /dev/null
coverage report -m >> $TEST_LOG
coverage html
deactivate
