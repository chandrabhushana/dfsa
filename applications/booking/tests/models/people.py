"""
This file is loaded automatically by tests/models/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/models/people.py
"""

import unittest

class TestPeopleModel(unittest.TestCase):
    
    def setUp(self):
        #execfile("applications/%s/controllers/people.py" % appname, globals()) #add the validatons
        db(db.auth_user.id>0).delete()
        db(db.people.id>0).delete()
        db(db.organisations.id>0).delete()
        db.organisations.insert(id=1,name='Acme Inc')
        db.people.insert(first_name='test', last_name='test', mobile='11111111')
        
        global vars
        vars = dict(type='Client',
                    first_name='John',
                    last_name='Doe',
                    email='test.email@example.com',
                    mobile='123456789')
    
    def testRequiredFieldsShouldAccept(self):
        r = db.people.validate_and_insert(**vars)
        self.assertTrue(r.id)
        self.assertEquals(len(r.errors),0)    
    
    def testAllFieldsShouldAccept(self):
        vars = dict(type='Client',
                    first_name='John',
                    last_name='Doe',
                    email='test.email@example.com',
                    mobile='123456789',
                    street_addr='123 Pine Ave',
                    suburb_addr='Melbourne',
                    state_addr=STATES_SET[0],
                    postcode_addr='3000',
                    gender=GENDERS_SET[0],
                    age_range= '12',
                    ethnicity=ETHNICITIES_SET[0],
                    contact_name='Jane Doe',
                    contact_number='121212',
                    shoe_size=SHOE_SIZES_SET[0],
                    clothing_size=CLOTHING_SIZES_SET[0],
                    job_type='Programming',
                    pref_showroom=False,
                    pref_fitting=False,
                    pref_admin=False,
                    pref_collection=False,
                    pref_donations=False,
                    pref_careers=False,
                    pref_mentoring=False,
                    pref_other='XYZ',
                    organisation='1',
                    )
        r = db.people.validate_and_insert(**vars)
        self.assertTrue(r.id)
        self.assertEquals(len(r.errors),0)
    
    def testEmptyFirstNameShouldFail(self):
        field='first_name'
        vars[field] = ''
        r = db.people.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Please enter a first name')
    
    def testEmptyLastNameShouldFail(self):
        field='last_name'
        vars[field]=''
        r = db.people.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Please enter a last name')
    
    def testEmptyMobileShouldFail(self):
        field='mobile'
        vars[field]=''
        r = db.people.validate_and_insert(**vars)
        #self.assertEquals(r.id, None)
        #self.assertEquals(r.errors[field], 'Please enter a unique contact number')
    
    def testDuplicateMobileShouldFail(self):
        field='mobile'
        vars[field] = '11111111'
        r = db.people.validate_and_insert(**vars)
        #self.assertEquals(r.id, None)
        #self.assertEquals(r.errors[field], 'Please enter a unique contact number')

def add_tests():
    suite.addTest(unittest.makeSuite(TestPeopleModel))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed by tests/models/runner.py
    add_tests()
