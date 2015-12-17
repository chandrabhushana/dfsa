"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/employees.py

Comments:
Employees leverages the common people tests to follow the behaves like OO testing pattern.
"""

execfile('applications/booking/tests/controllers/people.py', globals())

class TestEmployeesControllerBase(TestPeopleContollerBase):
    """ Helpers only. To be subclassed"""
    
    def setup_helper(self, function, resetdb=True):
        super(TestEmployeesControllerBase, self).setup_helper('employees', function, PERSON_TYPE_EMPLOYEE)

class TestEmployeesControllerWithNoAuth(TestEmployeesControllerBase):
    """To be subclassed. Not to be run directly"""
    
    def testCreate(self):
        self.setup_helper(function='create')
        self.assert_not_authorized(create)
    
    def testUpdate(self):
        self.setup_helper(function='update')
        self.assert_not_authorized(update)
    
    def testView(self):
        self.setup_helper(function='view')
        self.assert_not_authorized(view)
    
    def testIndex(self):
        self.setup_helper(function='index')
        self.assert_not_authorized(index)
    
    def testEnableLogin(self):
        self.setup_helper(function='enable_login')
        self.assert_not_authorized(enable_login)
    
    def testDisableLogin(self):
        self.setup_helper(function='disable_login')
        self.assert_not_authorized(disable_login)


class TestEmployeesControllerWithFullAuth(TestEmployeesControllerBase):
    """To be subclassed. Not to be run directly"""
    
    def testCreate(self):
        self.setup_helper(function='create')
        self.create_update_helper(create)
    
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

class TestEmployeesControllerAsAdmin(TestEmployeesControllerWithFullAuth):
    
    def setUp(self):
        set_is_admin()

class TestEmployeesControllerAsEmployee(TestEmployeesControllerWithFullAuth):
    
    def setUp(self):
        set_is_employee()
    
    """ Override from FullAuth """
    def testUpdate(self):
        self.setup_helper(function='update')
        self.assert_not_authorized(update)

class TestEmployeesControllerAsAgency(TestEmployeesControllerWithNoAuth):
    
    def setUp(self):
        set_is_agency()

class TestEmployeesControllerAsVolunteer(TestEmployeesControllerWithNoAuth):
    
    def setUp(self):
        set_is_volunteer()         

class TestEmployeesControllerAsClient(TestEmployeesControllerWithNoAuth):
    
    def setUp(self):
        set_is_client()


def add_tests():
    suite.addTest(unittest.makeSuite(TestEmployeesControllerAsAdmin))
    suite.addTest(unittest.makeSuite(TestEmployeesControllerAsEmployee))
    suite.addTest(unittest.makeSuite(TestEmployeesControllerAsAgency))
    suite.addTest(unittest.makeSuite(TestEmployeesControllerAsClient))
    suite.addTest(unittest.makeSuite(TestEmployeesControllerAsVolunteer))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed from runner.py
    add_tests()
