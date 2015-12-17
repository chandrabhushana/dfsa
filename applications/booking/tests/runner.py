#!/usr/bin/python
"""
Execute with:
>   python web2py.py -S booking -M -R applications/booking/tests/runner.py

Currently runs model tests. 
controllers and view tests still need to be run separately due to permissions

"""

import unittest
from gluon import current
from copy import copy

appname = current.request.application
approot = 'applications/' + appname
execfile(approot + '/tests/test_utils.py', globals())

setup_env()

#Load Tests into the suite
execfile(approot + '/tests/models/runner.py')
execfile(approot + '/tests/controllers/runner.py')

run_tests()
