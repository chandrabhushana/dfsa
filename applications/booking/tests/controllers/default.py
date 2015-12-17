"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/default.py

"""
from applications.booking.tests.base import TestBase
from gluon.storage import Storage

class TestDefaultControllerBase(TestBase):
    """ Helpers only. To be subclassed"""
    
    def setup_helper(self, function, user_type):
        """ Helper method """
        setup_function(self,'default',function, user_type=user_type)
        db(db.activities.id>0).delete()
        db.activities.insert(person_id=1,date=request.now) #for the activities list to work
    
    ALL_LINKS = set(['Home','Events','View Reports','Organisations',
                'Find Client','Create Client','Find Volunteer','Create Volunteer',
                'Find Employee','Create Employee','Find Agency User','Create Agency User']) 
    
    def assert_quicklinks(self, have=[]):
        
        #print self.html
        self.assertInHtml('<li><h4><a href="/user/logout">Logout</a></h4></li>')
        for x in have:
            self.assertInHtml(x + '</a></li>')
        for x in (self.ALL_LINKS-set(have)):
            self.assertNotInHtml(x + '</a></li>')
        
    
    def testDoubleLogin(self):
        """
        This test for double login applies to all account types so it is in the base class.
        Assume it is already logged in
        """
        self.setup_helper('user','FakeUser')
        auth.user.email = 'abc@email.com'
        
        set_args(['login'])
        self.assert_redirect(user, '/')
        self.assertEquals(session.flash, {'main_notice': 'You are already logged in.'})
        
        request.post_vars.email = 'xyz@email.com'
        self.assert_redirect(user, '/')
        self.assertEquals(session.flash, {'main_error': 'You are already logged in with abc@email.com on this browser. You can only have 1 login at a time per browser'})
        
        

class TestDefaultControllerAsClient(TestDefaultControllerBase):
    
    def setUp(self):
        set_is_client()
    
    def testIndex(self):
        self.setup_helper(function='index', user_type=PERSON_TYPE_CLIENT)
        resp = index()
        self.assertEquals(resp.get('entity'), 'clients')
        self.assertTrue(resp.get('person'))
        self.assertNotEquals(resp.get('activities'), None)
        self.assertEquals(response.view, 'people/view.html')
        self.html = render_helper(resp)
        self.assert_quicklinks(['Home'])
    
class TestDefaultControllerAsAdmin(TestDefaultControllerBase):
    
    def setUp(self):
        set_is_admin()

    def testIndex(self):
        self.setup_helper(function='index', user_type=PERSON_TYPE_ADMIN)
        #self.assert_not_authorized(index)
        resp = index()        
        self.assertEquals(resp.get('entity'), 'admin')
        self.assertTrue(resp.get('person'))
        self.assertNotEquals(resp.get('activities'), None)
        self.assertEquals(response.view, 'people/view.html')
        self.html = render_helper(resp)
        self.assert_quicklinks(self.ALL_LINKS)
    
class TestDefaultControllerAsEmployee(TestDefaultControllerBase):
    
    def setUp(self):
        set_is_employee()
    
    def testIndex(self):
        self.setup_helper(function='index', user_type=PERSON_TYPE_EMPLOYEE)
        #self.assert_not_authorized(index)
        resp = index()
        self.assertEquals(resp.get('entity'), 'employees')
        self.assertTrue(resp.get('person'))
        self.assertNotEquals(resp.get('activities'), None)
        self.assertEquals(response.view, 'people/view.html')
        self.html = render_helper(resp)
        self.assert_quicklinks(self.ALL_LINKS-set(['Organisations','View Reports']))
    
class TestDefaultControllerAsAgency(TestDefaultControllerBase):
    
    def setUp(self):
        set_is_agency()
    
    def testIndex(self):
        self.setup_helper(function='index', user_type=PERSON_TYPE_AGENCY)
        #self.assert_not_authorized(index)
        resp = index()
        self.assertEquals(resp.get('entity'), 'agencies')
        self.assertTrue(resp.get('person'))
        self.assertNotEquals(resp.get('activities'), None)
        self.assertEquals(response.view, 'people/view.html')
        self.html = render_helper(resp)
        self.assert_quicklinks(['Home','Create Client','Find Client','Find Agency User'])
    
class TestDefaultControllerAsVolunteer(TestDefaultControllerBase):
    
    def setUp(self):
        set_is_volunteer()
    
    def testIndex(self):
        self.setup_helper(function='index', user_type=PERSON_TYPE_VOLUNTEER)
        #self.assert_not_authorized(index)
        resp = index()
        self.assertEquals(resp.get('entity'), 'volunteers')
        self.assertTrue(resp.get('person'))
        self.assertNotEquals(resp.get('activities'), None)
        self.assertEquals(response.view, 'people/view.html')
        self.html = render_helper(resp)
        self.assert_quicklinks(['Home'])

def add_tests():
    suite.addTest(unittest.makeSuite(TestDefaultControllerAsAdmin))
    suite.addTest(unittest.makeSuite(TestDefaultControllerAsEmployee))
    suite.addTest(unittest.makeSuite(TestDefaultControllerAsClient))
    suite.addTest(unittest.makeSuite(TestDefaultControllerAsAgency))
    suite.addTest(unittest.makeSuite(TestDefaultControllerAsVolunteer))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed from runner.py
    add_tests()
