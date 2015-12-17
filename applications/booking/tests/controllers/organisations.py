"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/organisations.py
"""
from applications.booking.tests.base import TestBase
from gluon.storage import Storage

class TestOrganisationsControllerBase(TestBase):
    """
    This class has all common functionality and helper code that can be shared by multiple roles
    """
    
    """ Various organisation ids to test, matching the values being inserted in setup_db()"""
    ORG_IDS=Storage(INVALID=99999,DEFAULT=1,DEACTIVE=3,OTHER_ORG=2) #assumes auth.user.organisation=1
    
    def setup_db(self):
        """
        3 test cases to insert. 
        id=1 (organisation.id == auth.user.organisation)
        id=2 (organisation.id != auth.user.organisation)
        id=3 (organisation.id != auth.user.organisation and deactivated)
        """
        db(db.organisations.id>0).delete()
        db.organisations.insert(id=1, name='Test1', abn='1234', street_addr='wadgaon', suburb_addr='xxx', state_addr='VIC', postcode_addr='111',organisations_types='Referral Agency')
        db.organisations.insert(id=2, name='Test2', abn='5678', street_addr='wadgaon', suburb_addr='xxx', state_addr='VIC', postcode_addr='111',organisations_types='Referral Agency')
        db.organisations.insert(id=3, name='Test3', abn='9999', street_addr='wadgaon', suburb_addr='xxx', state_addr='VIC', postcode_addr='111',deactivated=True,organisations_types='Referral Agency')
    
    def setup_helper(self, function):
        """helper method"""
        #Setup the request and has_auth global vars for the specific function in organisations controller
        #Also sets the 'logged in user' to have organisaiton=1 (auth.user.organisation=1)
        setup_function(self,'organisations',function)
        #Setup the DB
        self.setup_db()
    
    def index_helper(self):
        """helper method to test multiple index scenarios"""
        
        """
        Call booking/controllers/organisations/index function and get back the dict
        Check how many 'organisations' get returned in the list
        For admin, it should list all the organisations.
        """
        resp = index()
        self.ui_test_helper_index(resp)
        expected = 3
        length = len(resp.get(entity))
        self.assertEquals(length, expected, 'wrong initial count: %i, expected %i' % (length,expected))
        
        """
        Call booking/controllers/organisations/index function with search
        search criteria: invalid 
        """
        request.vars = Storage(name='XYZ')
        resp = index()
        self.assertEquals(len(resp.get(entity)), 0, 'wrong count with fake name')
        
        """
        Call booking/controllers/organisations/index function with search
        search criteria: name is exact match 
        """
        request.vars = Storage(name='Test1')
        resp = index()
        self.assertEquals(len(resp.get(entity)), 1, 'wrong count with exact first name filter')
        
        """
        Call booking/controllers/organisations/index function with search
        search criteria: all active organisations with 'est' (checking string contains)
        """
        request.vars = Storage(name='est')
        resp = index()
        self.assertEquals(len(resp.get(entity)), expected, 'wrong count with first name "T" filter')
        
        """
        Call booking/controllers/organisations/index function with search
        search criteria: checking both name and abn
        """
        request.vars = Storage(name='Test', abn='1234')
        resp = index()
        self.assertEquals(len(resp.get(entity)), 1, 'wrong count with filter on all fields')
    
    
    def create_update_helper(self, method):
        """helper method to tests 3 different scenarios for both create and update:
        -no post vars
        -invalid form/post vars
        -valid form/post vars
        """
        
        """
        Call booking/controllers/organisations/(create|update) function with no values
        Get back the dict and check the values (new form)
        """
        resp = method() #get the form
        form = resp.get('form')
        if method.__name__=='create':
            self.ui_test_helper_create(resp)
        else:
            self.ui_test_helper_update(resp)
        
        """
        Create invalid form (missing required fields) and post to controller function
        Get back the dict and check that it contains form with errors
        """
        request.vars = request.post_vars = Storage(_formname=form.formname, _formkey=form.formkey)
        resp = method() #post the invalid form
        form = resp.get('form')
        self.assertTrue(form.errors)
        
        """
        Create valid form (containing required fields) and post to controller function.
        According to the desired controller logic (both create and update), 
        if the form posts successfully, controller should redirect to /organisations/view/<org_id>
        """
        request.vars = request.post_vars = Storage(name='ACME', desc='Cool things',street_addr='wadgaon', suburb_addr='xxx', state_addr='VIC', postcode_addr='111',organisations_types='Referral Agency', _formname=form.formname, _formkey=form.formkey)
        self.assert_redirect(method, f='view', a='\d+')

    def update_helper(self):
        """Helper function to test different 'organisation lookup' scenarios for update:
        -valid organisation
        -invalid (not in db)
        -deactivated
        """
        
        """
        Set the args (org id=1) and use create_update helper to test different scenarios 
        """
        set_args(self.ORG_IDS.DEFAULT)
        self.create_update_helper(update)
        
        """
        Set the args (org id=99999) and assert that controller will redirect back to index
            tests code: organisation = resource[id] or redirect(URL(c=entity,f='index'))
        """
        set_args(self.ORG_IDS.INVALID)
        self.assert_redirect(update)
        
        """
        Set the args (org id=3) and assert that controller will redirect back to index
            tests code: redirect_if_deactivated(organisation)
        """
        #test redirect on deleted client
        set_args(self.ORG_IDS.DEACTIVE)
        #if can('activate', request.controller):
        #    update() #no redirect if user can activate
        #else:
        self.assert_redirect(update)
        
    
    def view_helper(self, authorized_on_other_org=True):
        """Helper function to test different 'organisation lookup' scenarios for view:
        -valid organisation matching auth.user.organisation
        -valid organisation different than auth.user.organisation
        -invalid (not in db)
        -deactivated
        """
        
        """
        Call booking/controllers/organisations/view with org id 1 in args
        Get the dict back and check that the organisation was returned from DB
        """
        set_args(self.ORG_IDS.DEFAULT)
        resp = view()
        self.assertTrue(resp['organisation'])
        self.ui_test_helper_view(resp)
        
        """
        Set the args (org id=99999) and assert that controller will redirect back to index
            tests code: organisation = resource[id] or redirect(URL(c=entity,f='index'))
        """
        set_args(self.ORG_IDS.INVALID)
        self.assert_redirect(view)
        
        """
        Check different behaviour based on the role. 
        Agency should not be able to view organisations that are not their own (auth.user.organisation!=organisation.id)  
        """
        if authorized_on_other_org:
            """Admin user should get normal deactivated redirect (to index)"""
            
            #test redirect on deleted client
            set_args(self.ORG_IDS.DEACTIVE)
            if can('activate', request.controller):
                view() #no redirect if user can activate
            else:
                self.assert_redirect(self.view)
            
            
            """Admin user should be able to see organisation.id different than auth.user.organisation """
            set_args(self.ORG_IDS.OTHER_ORG)
            view()
        else:
            """
            Authorization check should fail before the deactivated check based on this code sequence:
                redirect_if_not_authorized_on(is_owner(organisation))
                redirect_if_deactivated(organisation)
            """
            set_args(self.ORG_IDS.DEACTIVE)
            self.assert_not_authorized(view)
            """Agency user should not be able to see organisation.id different than auth.user.organisation """
            set_args(self.ORG_IDS.OTHER_ORG)
            self.assert_not_authorized(view)
    
    def ui_test_helper_view(self, d):
        """Check that views/organisations/view.html renders properly with some key elements"""
        self.html = render_helper(d)
        self.assertNoInternalErrors()
        self.assertInHtml('<h2>Test1</h2>')
        self.assertInHtml('<div class="infodisplay">')
        self.assertInHtml('<td>Organisation: Test1</td>')
        self.assertInHtml('<td>ABN or Non-Profit ID: 1234</td>')
        self.assertInHtml('<span><a class="button" href="/organisations/update/1">Edit Details</a></span>')
        self.assertInHtml('<span><a class="deactivate button" href="/deactivate/organisations/1">Deactivate Organisation</a></span>')
    
    def ui_test_helper_index(self, d):
        """Check that views/organisations/index.html renders properly with some key elements"""
        self.html = render_helper(d)
        self.assertNoInternalErrors()
        self.assertInHtml('<h2>Find Organisation</h2>')
        self.assertInHtml('<form name="search" method="post" enctype="multipart/form-data" action="">')
        self.assertInHtml('<td><input type="text" name="name" value="" size="15" /></td>')
        self.assertInHtml('<div id="organisations-list">')
        self.assertInHtml('<tr class="clickable" onclick="go_to(\'/organisations/view/1\')">')
        self.assertInHtml('<span><a class="button" href="/organisations/create">Create Organisation</a></span>')
    
    def ui_test_helper_update(self, d):
        """Check that views/organisations/update.html renders properly with some key elements"""
        self.html = render_helper(d)
        self.assertNoInternalErrors()
        self.assertInHtml('<span><a class="" href="/organisations">Find Organisations</a></span>')
        self.assertInHtml('<span><a class="" href="/organisations/view/1">View Organisation</a></span>')
        self.assertInHtml('<h2>Edit Organisation</h2>')
        self.assertInHtml('<form  action="" enctype="multipart/form-data" method="post">')
        self.assertInHtml('<td><input class="string" id="organisations_name" name="name" type="text" value="Test1" /></td>')
        self.assertInHtml('<input name="_formname" type="hidden" value="organisations/1" />')
    
    def ui_test_helper_create(self, d):
        """Check that views/organisations/create.html renders properly with some key elements"""
        self.html = render_helper(d)
        self.assertNoInternalErrors()
        self.assertInHtml('<span><a class="" href="/organisations">Find Organisations</a></span>')
        self.assertInHtml('<h2>Create Organisation</h2>')
        self.assertInHtml('<form  action="" enctype="multipart/form-data" method="post">')
        self.assertInHtml('<td><input class="string" id="organisations_name" name="name" type="text" value="" /></td>')
        self.assertInHtml('<input name="_formname" type="hidden" value="organisations/create"')
    
        
class TestOrganisationsControllerWithNoAuth(TestOrganisationsControllerBase):
    """to be subclassed. not to be run directly"""
    
    """
    This class has all common functionality for an authorized user that can 
    be shared by mutiple roles (admin and third-party) rather than duplicating in each
    """
    
    def testCreate(self):
        self.setup_helper(function='create') #sets up has_auth for organisations/create with role assigned in setUp
        self.assert_not_authorized(create) #assert that create function fails auth.requires decorator
    
    def testUpdate(self):
        self.setup_helper(function='update') #sets up has_auth for organisations/update with role assigned in setUp
        self.assert_not_authorized(update) #assert that create function fails auth.requires decorator
    
    def testIndex(self):
        self.setup_helper(function='index') #sets up has_auth for organisations/index with role assigned in setUp
        self.assert_not_authorized(index) #assert that create function fails auth.requires decorator
    
    def testView(self):
        self.setup_helper(function='view') #sets up has_auth for organisations/view with role assigned in setUp
        self.assert_not_authorized(view) #assert that create function fails auth.requires decorator


class TestOrganisationsControllerWithFullAuth(TestOrganisationsControllerBase):
    """to be subclassed. not to be run directly"""
    
    def testIndex(self):
        self.setup_helper(function='index') #sets up has_auth for organisations/create with role assigned in setUp
        self.index_helper() #run the different index scenarios
    
    def testCreate(self):
        self.setup_helper(function='create') #sets up has_auth for organisations/update with role assigned in setUp
        self.create_update_helper(create) #run the different create scenarios
    
    def testUpdate(self):
        self.setup_helper(function='update') #sets up has_auth for organisations/index with role assigned in setUp
        self.update_helper() #run the different update scenarios
    
    def testView(self):
        self.setup_helper(function='view') #sets up has_auth for organisations/view with role assigned in setUp
        self.view_helper() #run the different view scenarios

class TestOrganisationsControllerAsAdmin(TestOrganisationsControllerWithFullAuth):
    
    def setUp(self):
        set_is_admin()

class TestOrganisationsControllerAsEmployee(TestOrganisationsControllerWithNoAuth):
    
    def setUp(self):
        set_is_employee()

class TestOrganisationsControllerAsVolunteer(TestOrganisationsControllerWithNoAuth):
    
    def setUp(self):
        set_is_volunteer()

class TestOrganisationsControllerAsClient(TestOrganisationsControllerWithNoAuth):
    
    def setUp(self):
        set_is_client()
    
class TestOrganisationsControllerAsAgency(TestOrganisationsControllerWithNoAuth):
    
    def setUp(self):
        set_is_agency()

#Add the tests to the suite
def add_tests():
    suite.addTest(unittest.makeSuite(TestOrganisationsControllerAsAdmin))
    suite.addTest(unittest.makeSuite(TestOrganisationsControllerAsClient))
    suite.addTest(unittest.makeSuite(TestOrganisationsControllerAsAgency))
    suite.addTest(unittest.makeSuite(TestOrganisationsControllerAsEmployee))
    suite.addTest(unittest.makeSuite(TestOrganisationsControllerAsVolunteer))


#Check if this test file is being executed directly or from runner
if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed from runner.py
    add_tests()
