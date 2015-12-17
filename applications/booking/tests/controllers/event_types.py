"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/event_types.py
"""
from applications.booking.tests.base import TestBase

class TestEventTypesControllerBase(TestBase):
    
    def setup_helper(self, function,e='load'):
        """ Helper method """
        setup_function(self,'event_types',function,e=e)
        db(db.event_types.id>0).delete()  # Clear the database
    
    def ui_test_helper_index(self, d, assert_error=False):
        #print response._view_environment['form']
        self.html = render_helper(d)
        self.assertInHtml('<div id="event_types">')
        self.assertInHtml('<h2>Event Types</h2>')
        self.assertInHtml('<table class="list-table" id="event_types_list" summary="Event Type List">')
        f = self.assertInHtml if is_admin else self.assertNotInHtml
        f('<span class="sh">Create Event Type</span>')
        
        self.assertInHtml('<td>Dummy</td>')
        self.assertInHtml('<td><input style="width: 19px; border: solid 1px #33677F; background:blue;" disabled=True  /></td>')
        
        if is_admin and assert_error:
            self.assertInHtml('<td><input class="string" id="event_types_name" name="name" type="text" value="Dummy" /><div class="error" id="name__error">Type already exists</div></td>')
        

class TestEventTypesControllerWithFullAuth(TestEventTypesControllerBase):
    """ To be subclassed. Not to be run directly"""
    
    def textIndex(self):
        self.setup_helper(function='index',e='html')
        resp = index()
        self.assertEquals(len(resp),0)
        self.html = render_helper(resp)
        print self.html
        
    def testAjaxIndex(self):
        self.setup_helper(function='index')
        request.ajax=True
        
        """
        The first call is expected to return an empty form and empty list
        
        The second call (with post vals) should return the new id and name to indicate successful insert, 
         - as well as a new empty form and still an empty list*.
           *The new record is not yet in the list due to the serialization transactions of GAE 
           - which the code works around by fetching the existing rows BEFORE the insert, not after.
           - See http://code.google.com/appengine/articles/transaction_isolation.html
        
        The third call (posting with the same name) should return a form error, 
            - and this time the list should contain the row from the previous transaction. 
            - New id and new name will be empty since the insert failed. 
        """
        
        ###Call 1 - Fetch the initial form
        resp = index()
        self.assertTrue(resp.get('form'), 'There should be a create form for admin')
        self.assertEquals(len(resp.get('event_types')), 0, 'There should be 0 event types initially')
                
        ###Call 2- submit the new type and confirm there is a new id
        form = resp.get('form')
        request.post_vars = Storage(name='Dummy', color='blue', _formname=form.formname, _formkey=form.formkey)
        resp = index() #post the form
        self.assertTrue(resp.get('new_event_type')!=None, 'There should be a new event type')
        self.assertEquals(len(resp.get('event_types')), 0, 'The event types list should still have 0 rows')
        
        self.ui_test_helper_index(resp) #check that the ui handles the new record properly
        
        ##Call 3-post again with the same type to test error
        form = resp.get('form')
        request.post_vars = Storage(name='Dummy', color='blue', _formname=form.formname, _formkey=form.formkey)
        resp = index() #post the form
        form = resp.get('form')
        self.assertTrue('name' in form.errors, 'Form should have an error for name ')
        self.assertEquals(form.errors.name, 'Type already exists')
        self.assertEquals(len(resp.get('event_types')), 1, 'There should be 1 event type from the previous create')
        
        self.ui_test_helper_index(resp, assert_error=True)


class TestEventTypesControllerReadonly(TestEventTypesControllerBase):
    """ To be subclassed. Not to be run directly"""
    
    def testAjaxIndex(self):
        """
        The first call is expected to return an empty empty list and no form
        After inserting into the db, the second call should have the 2 records. 
        """
        self.setup_helper(function='index')
        
        ###Call 1 - Fetch the initial form
        request.ajax=True
        resp = index()
        self.assertEquals(resp.get('form'), None, 'Form should be None form for this role')
        self.assertEquals(len(resp.get('event_types')), 0, 'There should be 0 event types initially')
        
        db.event_types.insert(name='Dummy', color='blue')
        db.event_types.insert(name='Dummy2', color='yellow')
        
        resp = index()
        self.assertEquals(resp.get('form'), None, 'Form should be None form for this role')
        self.assertEquals(len(resp.get('event_types')), 2, 'There should be 2 event types now')
        
        self.ui_test_helper_index(resp)
        
class TestEventTypesControllerAsAdmin(TestEventTypesControllerWithFullAuth):

    def setUp(self):
        set_is_admin()

class TestEventTypesControllerAsClient(TestEventTypesControllerReadonly):
    
    def setUp(self):
        set_is_client()

class TestEventTypesControllerAsAgency(TestEventTypesControllerReadonly):
    
    def setUp(self):
        set_is_agency()

class TestEventTypesControllerAsVolunteer(TestEventTypesControllerReadonly):
    
    def setUp(self):
        set_is_volunteer()        

class TestEventTypesControllerAsEmployee(TestEventTypesControllerReadonly):
    
    def setUp(self):
        set_is_employee()


def add_tests():
    suite.addTest(unittest.makeSuite(TestEventTypesControllerAsAdmin))
    suite.addTest(unittest.makeSuite(TestEventTypesControllerAsClient))
    suite.addTest(unittest.makeSuite(TestEventTypesControllerAsAgency))
    suite.addTest(unittest.makeSuite(TestEventTypesControllerAsEmployee))
    suite.addTest(unittest.makeSuite(TestEventTypesControllerAsVolunteer))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed from runner.py
    add_tests()
