#!/bin/bash
MODULE_NAME=c4solver

echo 'pytest + coverage: Python 3...'
python3 -m coverage run --source ${MODULE_NAME} -m pytest -vv -s -ra --durations=3 || exit 1
# show code coverage info
coverage report -m
