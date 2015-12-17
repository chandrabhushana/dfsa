"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/agencies.py

Comments:
Employees leverages the common people tests to follow the behaves like OO testing pattern.
"""

execfile('applications/booking/tests/controllers/people.py', globals())

class TestThirdpartiesControllerBase(TestPeopleContollerBase):
    """ Helpers only. To be subclassed"""
    
    def setup_helper(self, function, resetdb=True):
        #print super(self.__class__,self)
        #super(self.__class__,self).setup_helper('agencies', function, PERSON_TYPE_AGENCY)
        super(TestThirdpartiesControllerBase, self).setup_helper('agencies', function, PERSON_TYPE_AGENCY)
        self.shows_activities = False
        self.creates_activities = False
        self.shows_events = False

class TestThirdpartiesControllerWithFullAuth(TestThirdpartiesControllerBase):
    """to be subclassed. not to be run directly"""
    
    def testCreate(self):
        self.setup_helper(function='create', resetdb=False)
        self.create_update_helper(create)
    
    def testIndex(self):
        self.setup_helper(function='index')
        self.index_helper()
    
    def testUpdate(self):
        self.setup_helper(function='update')
        self.update_helper(authorized_on_other_org=True)
    
    def testView(self):
        self.setup_helper(function='view')
        self.view_helper(authorized_on_other_org=True)    

    def testEnableLogin(self):
        self.setup_helper(function='enable_login')
        set_args(1)
        self.assert_redirect(enable_login, f='view', a='\d+')
       
    def testDisableLogin(self):
        self.setup_helper(function='disable_login')
        set_args(1)
        self.assert_redirect(enable_login, f='view', a='\d+')

class TestThirdpartiesControllerWithReadOnlyAuthByOrg(TestThirdpartiesControllerBase):
    """to be subclassed. not to be run directly"""
    
    def testCreate(self):
        self.setup_helper(function='create', resetdb=False)
        self.assert_not_authorized(create)
    
    def testUpdate(self):
        self.setup_helper(function='update')
        self.assert_not_authorized(update)
    
    def testIndex(self):
        self.setup_helper(function='index')
        self.index_helper()
    
    def testView(self):
        self.setup_helper(function='view')
        self.view_helper(authorized_on_other_org=False)

    def testEnableLogin(self):
        self.setup_helper(function='enable_login')
        self.assert_not_authorized(enable_login)
    
    def testDisableLogin(self):
        self.setup_helper(function='disable_login')
        self.assert_not_authorized(disable_login)

class TestThirdpartiesControllerWithNoAuth(TestThirdpartiesControllerBase):
    """to be subclassed. not to be run directly"""
    
    def testIndex(self):
        self.setup_helper(function='index')
        self.assert_not_authorized(index)
    
    def testCreate(self):
        self.setup_helper(function='create')
        self.assert_not_authorized(create)
    
    def testUpdate(self):
        self.setup_helper(function='update')
        self.assert_not_authorized(update)
    
    def testView(self):
        self.setup_helper(function='view')
        self.assert_not_authorized(view)

    def testEnableLogin(self):
        self.setup_helper(function='enable_login')
        self.assert_not_authorized(enable_login)
    
    def testDisableLogin(self):
        self.setup_helper(function='disable_login')
        self.assert_not_authorized(disable_login)

class TestThirdpartiesControllerAsAdmin(TestThirdpartiesControllerWithFullAuth):
    
    def setUp(self):
        set_is_admin()

class TestThirdpartiesControllerAsEmployee(TestThirdpartiesControllerWithFullAuth):
    
    def setUp(self):
        set_is_employee()

class TestThirdpartiesControllerAsAgency(TestThirdpartiesControllerWithReadOnlyAuthByOrg):
    
    def setUp(self):
        set_is_agency()

class TestThirdpartiesControllerAsClient(TestThirdpartiesControllerWithNoAuth):
    
    def setUp(self):
        set_is_client()

class TestThirdpartiesControllerAsVolunteer(TestThirdpartiesControllerWithNoAuth):
    
    def setUp(self):
        set_is_volunteer()


def add_tests():
    suite.addTest(unittest.makeSuite(TestThirdpartiesControllerAsAdmin))
    suite.addTest(unittest.makeSuite(TestThirdpartiesControllerAsClient))
    suite.addTest(unittest.makeSuite(TestThirdpartiesControllerAsAgency))
    suite.addTest(unittest.makeSuite(TestThirdpartiesControllerAsEmployee))
    suite.addTest(unittest.makeSuite(TestThirdpartiesControllerAsVolunteer))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed from runner.py
    add_tests()
