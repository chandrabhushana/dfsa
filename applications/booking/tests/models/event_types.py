import unittest
#from gluon.globals import Request, Response

class TestEventTypesModel(unittest.TestCase):
    
    def setUp(self):
        execfile("applications/%s/controllers/event_types.py" % appname, globals()) #add the validatons
        db(db.event_types.id>0).delete()  # Clear the database
        db.event_types.insert(name='Fitting')
        
        global vars
        vars = dict(name='Dummy', color='blue')
    
    def testRequiredFieldsShouldInsert(self):
        r = db.event_types.validate_and_insert(**vars)
        self.assertTrue(r.id)
        self.assertEquals(len(r.errors),0)
    
    def testEmptyNameShoulNotInsert(self):
        field='name'
        vars[field]=''
        r = db.event_types.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Type cannot be empty')
    
    def testDuplicateNameShouldNotInsert(self):
        field='name'
        vars[field]='Fitting'
        r = db.event_types.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Type already exists')
        
    def testEmptyColorShouldNotInsert(self):
        field='color'
        vars[field]=''
        r = db.event_types.validate_and_insert(**vars)
        self.assertEquals(r.id, None)
        self.assertEquals(r.errors[field], 'Color cannot be empty')

def add_tests():
    suite.addTest(unittest.makeSuite(TestEventTypesModel))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed by tests/models/runner.py
    add_tests()
