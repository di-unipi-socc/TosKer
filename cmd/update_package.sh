#!/bin/sh
python setup.py bdist_wheel
twine upload dist/* --skip-existing
