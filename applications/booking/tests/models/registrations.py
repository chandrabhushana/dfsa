"""
This file is loaded automatically by tests/models/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/models/registrations.py
"""

import unittest
from datetime import date

class TestRegistrationsModel(unittest.TestCase):
    
    def setUp(self):
        execfile("applications/%s/controllers/registrations.py" % appname, globals()) #add the validatons
        db(db.registrations.id>0).delete()
        db(db.people.id>0).delete()
        db(db.events.id>0).delete()
        db.people.insert(id=1,type='Client',first_name='John',last_name='Doe')
        db.people.insert(id=2,type='Admin',first_name='Admin',last_name='Admin')
        db.people.insert(id=3,type='Client',first_name='Jane',last_name='Doe', deactivated=True)
        db.events.insert(id=1,type=1,name='Test Event', date=date.today())
        db.events.insert(id=2,type=2,name='Test Event', date=date.today(), deactivated=True)
        
        global vars
        vars = dict(person='1', event='1')
    
    def testRequiredFieldsShouldInsert(self):
        r = db.registrations.validate_and_insert(**vars)
        self.assertTrue(r.id)
        self.assertEquals(len(r.errors),0)
    
    def testEmptyEventShouldFail(self):
        field='event'
        vars[field] = None
        r = db.registrations.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field],'value not in database')
    
    def testInvalidEventShouldFail(self):
        field='event'
        vars[field] = 999999
        r = db.registrations.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field],'value not in database')
    
    def testDeletedEventShouldInsert(self):
        field='event'
        vars[field] = 2
        r = db.registrations.validate_and_insert(**vars)
        self.assertTrue(r.id)
        self.assertEquals(len(r.errors),0)
    
    def testEmptyClientShouldFail(self):
        field='person'
        vars[field] = None
        r = db.registrations.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field],'value not in database')
    
    def testNonClientPersonShouldFail(self):
        field='person'
        vars[field] = 2
        r = db.registrations.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field],'value not in database')
    
    def testDeletedClientShouldFail(self):
        field='person'
        vars[field] = 3
        r = db.registrations.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field],'value not in database')
    

def add_tests():
    suite.addTest(unittest.makeSuite(TestRegistrationsModel))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed by tests/models/runner.py
    add_tests()
