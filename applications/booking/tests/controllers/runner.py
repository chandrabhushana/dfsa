"""
This file loads and runs all the controller tests. It is loaded automatically by tests/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/runner.py

The controller tests use fake authentication based on manipulating global variables 
to set the current role and rerunning roles_perms.py before executing the controller script.
"""

def load_tests():
    execfile(approot + '/tests/controllers/activities.py', globals())
    execfile(approot + '/tests/controllers/event_types.py', globals())
    execfile(approot + '/tests/controllers/clients.py', globals())
    execfile(approot + '/tests/controllers/agencies.py', globals())
    execfile(approot + '/tests/controllers/organisations.py', globals())
    execfile(approot + '/tests/controllers/registrations.py', globals())
    execfile(approot + '/tests/controllers/events.py', globals())
    execfile(approot + '/tests/controllers/deactivate.py', globals())
    execfile(approot + '/tests/controllers/default.py', globals())
    execfile(approot + '/tests/controllers/reports.py', globals())
    

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    load_tests()
    run_tests()
else:
    #executed by tests/runner.py
    load_tests()
