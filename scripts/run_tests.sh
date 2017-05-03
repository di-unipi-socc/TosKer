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
if [ $# == 0 ] || [ $1 == "python2" ]; then
  echo 'run python2 tests...'
  echo 'TEST PYTHON2' >> $TEST_LOG
  . ./venv2/bin/activate
  pip install -r requirements.txt &> /dev/null
  python -m unittest discover -v 2>> $TEST_LOG
  deactivate
fi


# test on python3 and coverage
if [ $# == 0 ] || [ $1 == "python3" ]; then
  echo 'run python3 tests...'
  echo "\nTEST PYTHON3 and COVERAGE" >> $TEST_LOG
  . ./venv3/bin/activate
  pip install -r requirements.txt &> /dev/null
  coverage run --source tosker -m unittest discover -v 2> /dev/null
  coverage report -m --omit 'tosker/tests/*,tosker/graph/*,tosker/helper.py,*__init__.py' >> $TEST_LOG
  coverage html --omit 'tosker/tests/*,tosker/graph/*,tosker/helper.py,*__init__.py'
  deactivate
fi
