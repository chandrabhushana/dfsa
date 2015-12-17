import unittest

class TestEventsModel(unittest.TestCase):
    
    def setUp(self):
        global can
        can = lambda x,y: True
        execfile("applications/%s/controllers/events.py" % appname, globals()) #add the validatons
        db(db.events.id>0).delete()
        db(db.event_types.id>0).delete()
        db.event_types.insert(id=1,name='Fitting')
        
        global formname, form, post_vars
        formname = 'create'
        db.events.type.writable=True
        form = SQLFORM(db.events) #form has to be created after the db is prepared
        post_vars = dict(name='Dummy',
                     type='1',
                     slots='10',
                     date='08-08-2011',
                     start_time='09:00',
                     end_time='10:00', 
                     _formname=formname)
    
    def testRequiredFieldsShouldInsert(self):
        status = form.accepts(post_vars, formname=formname)
        self.assertTrue(status)
    
    def testEmptyNameShouldNotInsert(self):
        field = 'name'
        post_vars[field] = ''
        self.assertFalse(form.accepts(post_vars, formname=formname))
        self.assertEquals(form.errors[field], 'enter a value')
    
    def testEmptyTypeShouldNotInsert(self):
        field = 'type'
        post_vars[field] = ''
        self.assertFalse(form.accepts(post_vars, formname=formname))
        self.assertEquals(form.errors[field], 'value not in database')
    
    def testDummyTypeShouldNotInsert(self):
        field = 'type'
        post_vars[field] = '3'
        self.assertFalse(form.accepts(post_vars, formname=formname))
        self.assertEquals(form.errors[field], 'value not in database')
    
    def testEndTimeAfterStartTimeShouldNotInsert(self):
        field = 'end_time'
        post_vars[field] = '09:00'
        self.assertFalse(form.accepts(post_vars, formname=formname, onvalidation=event_form_processing))
        self.assertEquals(form.errors[field], 'End time must be after start time')
    

def add_tests():
    suite.addTest(unittest.makeSuite(TestEventsModel))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed by tests/models/runner.py
    add_tests()
