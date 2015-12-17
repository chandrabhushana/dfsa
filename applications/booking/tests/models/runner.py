"""
This file loads and runs all the model tests. It is loaded automatically by tests/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/models/runner.py
"""

def load_tests():
    execfile(approot + '/tests/models/event_types.py', globals())
    execfile(approot + '/tests/models/events.py', globals())
    execfile(approot + '/tests/models/people.py', globals())
    execfile(approot + '/tests/models/activities.py', globals())
    execfile(approot + '/tests/models/registrations.py', globals())
    execfile(approot + '/tests/models/organisations.py', globals())

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    load_tests()
    run_tests()
else:
    #executed by tests/runner.py
    load_tests()
