"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/clients.py

Comments:
Clients leverages the common people tests to follow the behaves like OO testing pattern.
"""
execfile('applications/booking/tests/controllers/people.py', globals())

class TestClientsControllerBase(TestPeopleContollerBase):
    
    def setup_helper(self, function):
        super(TestClientsControllerBase, self).setup_helper('clients', function, PERSON_TYPE_CLIENT)

class TestClientsControllerWithNoAuth(TestClientsControllerBase):
    """To be subclassed. Not to be run directly"""
    
    def testCreate(self):
        self.setup_helper(function='create')
        self.assert_not_authorized(create)
    
    def testUpdate(self):
        self.setup_helper(function='update')
        self.assert_not_authorized(update)
    
    def testIndex(self):
        self.setup_helper(function='index')
        self.assert_not_authorized(index)
    
    def testView(self):
        self.setup_helper(function='view')
        self.assert_not_authorized(view)
    
    def testEnableLogin(self):
        self.setup_helper(function='enable_login')
        self.assert_not_authorized(enable_login)
    
    def testDisableLogin(self):
        self.setup_helper(function='disable_login')
        self.assert_not_authorized(disable_login)


class TestClientsControllerWithFullAuth(TestClientsControllerBase):
    """To be subclassed. Not to be run directly"""
    
    def testCreate(self):
        self.setup_helper(function='create')
        self.create_update_helper(create)
        #response.render(self.resp)
    
    def testIndex(self):
        self.setup_helper(function='index')
        self.index_helper()
    
    def testUpdate(self):
        self.setup_helper(function='update')
        self.update_helper()
    
    def testView(self):
        self.setup_helper(function='view')
        self.view_helper()

    def testEnableLogin(self):
        self.setup_helper(function='enable_login')
        set_args(1)
        self.assert_redirect(enable_login, f='view', a='\d+')
       
    def testDisableLogin(self):
        self.setup_helper(function='disable_login')
        set_args(1)
        self.assert_redirect(enable_login, f='view', a='\d+')


class TestClientsControllerReadOnly(TestClientsControllerBase):
    """To be subclassed. Not to be run directly"""
    
    def testCreate(self):
        self.setup_helper(function='create')
        self.assert_not_authorized(create)
    
    def testUpdate(self):
        self.setup_helper(function='update')
        self.assert_not_authorized(update)
    
    def testIndex(self):
        self.setup_helper(function='index')
        self.index_helper()
    
    def testView(self):
        self.setup_helper(function='view')
        self.view_helper()

    def testEnableLogin(self):
        self.setup_helper(function='enable_login')
        set_args(1)
        self.assert_not_authorized(enable_login)
       
    def testDisableLogin(self):
        self.setup_helper(function='disable_login')
        set_args(1)
        self.assert_not_authorized(disable_login)



class TestClientsControllerAsAdmin(TestClientsControllerWithFullAuth):
    
    def setUp(self):
        set_is_admin()

class TestClientsControllerAsEmployee(TestClientsControllerWithFullAuth):
    
    def setUp(self):
        set_is_employee()

class TestClientsControllerAsClient(TestClientsControllerWithNoAuth):
    
    def setUp(self):
        set_is_client()

class TestClientsControllerAsVolunteer(TestClientsControllerReadOnly):
    
    def setUp(self):
        set_is_volunteer()        
        
class TestClientsControllerAsAgency(TestClientsControllerBase):
    
    def setUp(self):
        set_is_agency()
    
    def testIndex(self):
        self.setup_helper(function='index')
        self.index_helper()
    
    def testCreate(self):
        self.setup_helper(function='create')
        self.create_update_helper(create)
    
    def testUpdate(self):
        self.setup_helper(function='update')
        self.update_helper(authorized_on_other_org=False)
    
    def testView(self):
        self.setup_helper(function='view')
        self.creates_activities = False #Agency cannot create acitvities
        self.view_helper(authorized_on_other_org=False)

    def testEnableLogin(self):
        self.setup_helper(function='enable_login')
        self.assert_not_authorized(enable_login)
    
    def testDisableLogin(self):
        self.setup_helper(function='disable_login')
        self.assert_not_authorized(disable_login)


def add_tests():
    suite.addTest(unittest.makeSuite(TestClientsControllerAsAdmin))
    suite.addTest(unittest.makeSuite(TestClientsControllerAsEmployee))
    suite.addTest(unittest.makeSuite(TestClientsControllerAsClient))
    suite.addTest(unittest.makeSuite(TestClientsControllerAsVolunteer))
    suite.addTest(unittest.makeSuite(TestClientsControllerAsAgency))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed from runner.py
    add_tests()
