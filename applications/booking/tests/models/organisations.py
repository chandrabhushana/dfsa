import unittest

class TestOrganisationsModel(unittest.TestCase):
    
    def setUp(self):
        execfile("applications/%s/controllers/organisations.py" % appname, globals()) #add the validations
        db(db.organisations.id>0).delete()
        db.organisations.insert(id=1,name='XYZ Inc')
        
        global vars
        vars = dict(name='Acme Inc')                    
    
    def testOnlyRequiredFieldsShouldInsert(self):
        r = db.organisations.validate_and_insert(**vars)
        self.assertTrue(r.id)
        self.assertEquals(len(r.errors),0)
    
    def testEmptyNameShouldFail(self):
        field='name'
        vars[field] = ''
        r = db.organisations.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Name cannot be empty')
    
    
    def testDuplicateNameShouldFail(self):
        field='name'
        vars[field] = 'XYZ Inc'
        r = db.organisations.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Name already exists')
        
def add_tests():
    suite.addTest(unittest.makeSuite(TestOrganisationsModel))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed by tests/models/runner.py
    add_tests()
