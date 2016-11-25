#!/bin/sh
TEST_LOG=/tmp/tosker_test.log
echo '' > $TEST_LOG

if [ ! -d "venv2" ]; then
  virtualenv venv2 -p python2
fi

if [ ! -d "venv3" ]; then
  virtualenv venv3 -p python3
fi

# test on python2
echo '\nTEST PYTHON2' >> $TEST_LOG
. ./venv2/bin/activate
pip install -r requirements.txt
python -m unittest discover -v >> $TEST_LOG
deactivate

# test on python3
echo '\nTEST PYTHON3' >> $TEST_LOG
. ./venv3/bin/activate
pip install -r requirements.txt
python -m unittest discover -v >> $TEST_LOG
deactivate

# coverage
echo '\nCOVERAGE' >> $TEST_LOG
coverage run --source tosker -m unittest discover
coverage report -m >> $TEST_LOG
coverage html
