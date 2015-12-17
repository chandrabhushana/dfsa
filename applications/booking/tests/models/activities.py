import unittest

class TestActivitiesModel(unittest.TestCase):
    
    def setUp(self):
        execfile("applications/%s/controllers/activities.py" % appname, globals()) #add the validatons
        db(db.activities.id>0).delete()
        db(db.people.id>0).delete()
        db(db.event_types.id>0).delete()
        db.people.insert(id=1,first_name='John',last_name='Doe')
        db.event_types.insert(name='Fitting')
        
        global vars
        vars = dict(person_id='1', 
                    type='Fitting',
                    date='08-08-2011',
                    shoe_size='5.0',
                    clothing_size='6-8')
    
    def testOnlyRequiredFieldsShouldInsert(self):
        #remove non-required fields to avoid false positive
        for x in ['shoe_size','clothing_size']:
            del vars[x]
        r = db.activities.validate_and_insert(**vars)
        self.assertTrue(r.id)
        self.assertEquals(len(r.errors),0)
    
    def testEmptyDateShouldFail(self):
        field = 'date'
        vars[field] = ''
        r = db.activities.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Please select a date')
    
    #def testInvalidShoeSizeShouldFail(self):
    #    field = 'shoe_size'
    #    vars[field] = 'XYZ'
    #    r = db.activities.validate_and_insert(**vars)
    #    self.assertEquals(r.id, None)
    #    self.assertEquals(r.errors[field], 'value not allowed')
    #
    #def testInvalidClothingSizeShouldFail(self):
    #    field = 'clothing_size'
    #    vars[field] = 'XYZ'
    #    r = db.activities.validate_and_insert(**vars)
    #    self.assertEquals(r.id, None)
    #    self.assertEquals(r.errors[field], 'value not allowed')
    
    def testEmptyPersonIdShouldFail(self):
        field = 'person_id'
        vars[field] = ''
        r = db.activities.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Invalid Client ID')
    
    def testInvalidPersonIdShouldFail(self):
        field = 'person_id'
        vars[field] = '999'
        r = db.activities.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Invalid Client ID')
    
    def testEmptyTypeShouldFail(self):
        field = 'type'
        vars[field] = ''
        r = db.activities.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Please select a valid activity type')
    
    def testInvalidPersonIdShouldFail(self):
        field = 'type'
        vars[field] = 'FakeType'
        r = db.activities.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Please select a valid activity type')
    
    
def add_tests():
    suite.addTest(unittest.makeSuite(TestActivitiesModel))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed by tests/models/runner.py
    add_tests()
