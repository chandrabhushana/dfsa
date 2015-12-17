"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/activities.py
"""
from applications.booking.tests.base import TestBase

class TestActivitiesControllerBase(TestBase):
        
    SELF_ID = 1
    CLIENT_1 = 2
    CLIENT_2 = 53
    THIRD_PARTY_ID = 55
    EMPLOYEE_1 = 56
    EMPLOYEE_2 = 57
    VOLUNTEER_1 = 58
    VOLUNTEER_2 = 59
    
    SELF_ACT = 1
    CLIENT_1_ACT = 2
    CLIENT_2_ACT = 3
    EMPLOYEE_1_ACT = 4
    EMPLOYEE_2_ACT = 5
    VOLUNTEER_1_ACT = 6
    VOLUNTEER_2_ACT = 7
    INVALID_ACT = 999999
    
    def setup_db(self):
       
        #Added here
        db(db.auth_user.id>0).delete()
        db(db.event_types.id>0).delete()
        db(db.activities.id>0).delete()  # Clear the database
        
        db.people.insert(id=self.SELF_ID,type=PERSON_TYPE_CLIENT, organisation=1, gender='Female',date_of_birth=request.now.date())
        db.people.insert(id=self.CLIENT_1,type=PERSON_TYPE_CLIENT, organisation=1, gender='Male', date_of_birth=request.now.date())
        db.people.insert(id=self.CLIENT_2,type=PERSON_TYPE_CLIENT, organisation=2, gender='Male',date_of_birth=request.now.date())
        db.people.insert(id=self.THIRD_PARTY_ID,type=PERSON_TYPE_AGENCY,organisation=1,date_of_birth=request.now.date())
        db.people.insert(id=self.EMPLOYEE_1,type=PERSON_TYPE_EMPLOYEE, organisation=1,date_of_birth=request.now.date())
        db.people.insert(id=self.EMPLOYEE_2,type=PERSON_TYPE_EMPLOYEE, organisation=2,date_of_birth=request.now.date())
        db.people.insert(id=self.VOLUNTEER_1,type=PERSON_TYPE_VOLUNTEER, organisation=1,date_of_birth=request.now.date())
        db.people.insert(id=self.VOLUNTEER_2,type=PERSON_TYPE_VOLUNTEER, organisation=2,date_of_birth=request.now.date())
        
        db.event_types.insert(name='Fitting')
        
        db.activities.insert(id=self.SELF_ACT,person_id=self.SELF_ID,type='Fitting')
        db.activities.insert(id=self.CLIENT_1_ACT,person_id=self.CLIENT_1,type='Fitting', type_of_clothing='Interview')
        db.activities.insert(id=self.CLIENT_2_ACT,person_id=self.CLIENT_2,type='Fitting',type_of_clothing='Interview')
        db.activities.insert(id=self.EMPLOYEE_1_ACT,person_id=self.EMPLOYEE_1, type='Fitting', gender='Female')
        db.activities.insert(id=self.EMPLOYEE_2_ACT,person_id=self.EMPLOYEE_2, type='Fitting', gender='Female')
        db.activities.insert(id=self.VOLUNTEER_1_ACT,person_id=self.VOLUNTEER_1, type='Fitting', gender='Male')
        db.activities.insert(id=self.VOLUNTEER_2_ACT,person_id=self.VOLUNTEER_2, type='Fitting', gender='Female')
        
    
    def setup_helper(self, function):
        """helper method for setup before each test"""
        setup_function(self,'activities',function)
        self.setup_db()
        
        #need to reset the conditional validators (done autmatically in normal request cycle)
        for x in ACTIVITIES_ITEMS_BOTH:
            db.activities.get(x).requires = []
    
    
    def post_valid_form(self, method, person_id=None):
        request.vars = request.post_vars = Storage(person=person_id)
        form = method().get('form') #get a new formkey
        request.vars = request.post_vars = Storage(type='Fitting',date='31-08-2011',
                                                   shoe_size=SHOE_SIZES_SET[0],clothing_size=CLOTHING_SIZES_SET[0],
                                                   start_time='09:00',end_time='09:15',gender='Male',type_of_clothing='Interview',
                                                   _formname=form.formname,_formkey=form.formkey,person=person_id)
        for x in ACTIVITIES_ITEMS_FEMALE:
            request.vars[x] = request.post_vars[x] = '0'
        
        self.assert_redirect(method, c='default',f='index')
    
    def post_invalid_forms(self, method, person_id=None):
        request.vars = request.post_vars = Storage(person=person_id)
        form = method().get('form') #get a new formkey
        request.vars = request.post_vars = Storage(_formname=form.formname, _formkey=form.formkey, person=person_id)
        form = method().get('form')
        self.assertTrue(form.errors)
        
        #test another failure with the male items set rather than female items (Client 1 is female)
        request.vars = request.post_vars = Storage(type='Fitting',date='01-01-2010',_formname=form.formname, _formkey=form.formkey,person=person_id)
        request.vars.shoe_size = request.post_vars.shoe_size = SHOE_SIZES_SET_MALE[-2]
        request.vars.clothing_size = request.post_vars.clothing_size = CLOTHING_SIZES_SET_MALE[-2]
        for x in ACTIVITIES_ITEMS_MALE:
            request.vars[x] = request.post_vars[x] = '0'
        form = method().get('form')
        self.assertTrue('shoe_size' in form.errors)
        self.assertTrue('clothing_size' in form.errors)
        self.assertTrue('nbr_skirts' in form.errors)
        self.assertTrue('nbr_makeup' in form.errors)
        self.assertTrue('nbr_dresses' in form.errors)
        self.assertTrue('nbr_softtops' in form.errors)
        self.assertTrue('nbr_kneehighs' in form.errors)
        self.assertTrue('nbr_scarves' in form.errors)
        self.assertTrue('nbr_handbags' in form.errors)
        self.assertTrue('nbr_esteem_jewellery' in form.errors)
        self.assertTrue('nbr_boots' in form.errors)
        self.assertTrue('nbr_underwear' in form.errors)
        self.assertTrue('nbr_bra' in form.errors)
        self.assertTrue('nbr_camisole' in form.errors)
        
        
        
    def create_helper(self):
        """helper method for create functionality"""
        
        #Get the initial form
        user_id = auth.user_id #self
        request.vars = request.post_vars = Storage(person=user_id)
        resp = create()
        self.assertTrue(resp.get('person'))
        self.assertTrue(resp.get('form'))
        self.assertEquals(resp.get('readonly'), False)
        
        #test the view render the view
        self.ui_test_helper_create(resp)
        
        self.post_invalid_forms(create, person_id=user_id)
        self.post_valid_form(create, person_id=user_id)
        
        self.create_permission_helper()
    
    def update_helper(self):
        """helper method for update functionality"""
        
        set_args(self.SELF_ACT)
        resp = update()
        self.assertTrue(resp.get('person'))
        self.assertTrue(resp.get('form'))
        self.assertEquals(resp.get('readonly'), False)
        
        #test the view render
        self.ui_test_helper_update(resp)
        
        self.post_valid_form(update, None)
        self.post_invalid_forms(update, None)
        
        self.assertEquals(str(session.flash), 'Activity updated!')
        
        ###test the permissions on different scenarios###
        self.view_update_permission_helper(update)
    
    def view_helper(self):
        """helper method for view functionality"""
        
        set_args(self.SELF_ACT)
        resp = view()
        self.assertTrue(resp.get('form'))
        self.assertEquals(resp.get('readonly'), True)
        
        #test the view render
        self.ui_test_helper_view(resp)
        
        #test the permissions on different scenarios
        self.view_update_permission_helper(view)
    
    def create_permission_helper(self):
        request.post_vars = Storage()
        
        request.vars = Storage()
        self.assert_redirect(create, c='default',f='index')
        self.assertEquals(session.flash, 'Invalid person id')
        
        request.vars = Storage(person=99999)
        self.assert_redirect(create, c='default',f='index')
        self.assertEquals(session.flash, 'Invalid person id')
        
        #check that volunteer can manage clients' activities but not other entities
        request.vars = Storage(person=self.CLIENT_1)
        can_create_clients = is_volunteer or is_employee or is_admin 
        if can_create_clients:
            resp = create()
            self.ui_test_helper_create(resp) #also test the view when auth.user<>person
        else:
            self.assert_not_authorized(create)
        
        request.vars = Storage(person=self.CLIENT_2)
        create() if can_create_clients else self.assert_not_authorized(create)
        
        can_create_others = is_employee or is_admin
        for x in [self.VOLUNTEER_1, self.VOLUNTEER_2, self.EMPLOYEE_1, self.EMPLOYEE_2]:
            request.vars = Storage(person=x)
            create() if can_create_others else self.assert_not_authorized(create)
        
    
    def view_update_permission_helper(self, method):
        
        #should redirect to default/index before person auth check
        set_args(self.INVALID_ACT)
        self.assert_redirect(method, c='default',f='index')
        
        if method.__name__=='view':
            can_x_all_clients = is_admin or is_employee or is_volunteer
            can_x_clients_in_same_org = can_x_all_clients or is_agency
            can_x_all_others = is_admin or is_employee 
            can_x_others_in_same_org = can_x_all_others or False
            ui_helper = self.ui_test_helper_view
        else: #update
            can_x_all_clients = is_admin or is_employee or is_volunteer
            can_x_clients_in_same_org = can_x_all_clients
            can_x_all_others = is_admin or is_employee 
            can_x_others_in_same_org = can_x_all_others
            ui_helper = self.ui_test_helper_update
        
        #check that volunteer can manage clients' activities but not other entities
        set_args(self.CLIENT_1_ACT)
        if can_x_clients_in_same_org:
            resp = method()
            ui_helper(resp) #also test the view when auth.user<>person
        else:
            self.assert_not_authorized(method)
        
        
        set_args(self.CLIENT_2_ACT)
        method() if can_x_all_clients else self.assert_not_authorized(method)
                
        #employee1 and colunteer1 are in same org than auth user
        for x in [self.EMPLOYEE_1_ACT, self.VOLUNTEER_1_ACT]:
            set_args(x)
            method() if can_x_others_in_same_org else self.assert_not_authorized(method)
        
        #employee2 and colunteer2 are in different org than auth user
        for x in [self.EMPLOYEE_2_ACT, self.VOLUNTEER_2_ACT]:
            set_args(x)
            method() if can_x_all_others else self.assert_not_authorized(method)
        
    
    def ui_test_helper_view(self, d):
        self.html = render_helper(d)
        person = d.get('person')
        entity = entity_by_person_type(person.type)
        
        if not is_client:
            self.assertInHtml('<span><a class="" href="/%s">Find %s</a></span>' % (entity, person.type))
            self.assertInHtml('<span><a class="" href="/%s/view/%s">View %s</a></span>' % (entity, person.id, person.type))
        self.assertInHtml('<h2>View Activity</h2>')
        #for readonly, activity type is a div
        self.assertInHtml('<td><div id="activities_type">Fitting</div></td>')
        #if person.id==auth.user_id:
        #    self.assertInHtml('<td><span><a class="button" href="/">Cancel</a></span></td>')
        #else:
        #    self.assertInHtml('<td><span><a class="button" href="/%s/view/%s">Cancel</a></span></td>' % (entity, person.id))
        
    def ui_test_helper_update(self, d):
        person = d.get('person')
        entity = entity_by_person_type(person.type)
        self.html = render_helper(d)
        
        if not is_client:
            self.assertInHtml('<span><a class="" href="/%s">Find %s</a></span>' % (entity, person.type))
            self.assertInHtml('<span><a class="" href="/%s/view/%s">View %s</a></span>' % (entity, person.id, person.type))
        self.assertInHtml('<h2>Edit Activity</h2>')
        self.assertInHtml('<span class="required-message">(<span class="m">*</span>) required field</span>')
        #for non-readonly, activity type is a select
        self.assertInHtml('<td><select class="string" id="activities_type" name="type"><option value=""></option><option selected="selected" value="Fitting">Fitting</option></select></td>')
        #if person.id==auth.user_id:
        #    self.assertInHtml('<td><span><a class="button" href="/">Cancel</a></span></td>')
        #else:
        #    self.assertInHtml('<td><span><a class="button" href="/%s/view/%s">Cancel</a></span></td>' % (entity, person.id))
        
        
    def ui_test_helper_create(self, d):
        person = d.get('person')
        entity = entity_by_person_type(person.type)
        self.html = render_helper(d)
        
        if not is_client:
            self.assertInHtml('<span><a class="" href="/%s">Find %s</a></span>' % (entity, person.type))
            self.assertInHtml('<span><a class="" href="/%s/view/%s">View %s</a></span>' % (entity, person.id, person.type))
        self.assertInHtml('<h2>New Activity</h2>')
        self.assertInHtml('<span class="required-message">(<span class="m">*</span>) required field</span>')
        #for non-readonly, activity type is a select
        self.assertInHtml('<td><select class="string" id="activities_type" name="type"><option value=""></option><option value="Fitting">Fitting</option></select></td>')
        #if person.id==auth.user_id:
        #    self.assertInHtml('<td><span><a class="button" href="/">Cancel</a></span></td>')
        #else:
        #    self.assertInHtml('<td><span><a class="button" href="/%s/view/%s">Cancel</a></span></td>' % (entity, person.id))
        

class TestActivitiesControllerWithFullAuth(TestActivitiesControllerBase):
    """to be subclassed by role specific test class. not to be run directly"""
    
    def testCreate(self):
        self.setup_helper('create')
        self.create_helper()
    
    def testUpdate(self):
        self.setup_helper('update')
        self.update_helper()
    
    def testView(self):
        self.setup_helper('view')
        self.view_helper()


class TestActivitiesControllerAsReadOnly(TestActivitiesControllerBase):
    """to be subclassed by role specific test class. not to be run directly"""
    
    def testCreate(self):
        self.setup_helper('create')
        self.assert_not_authorized(create)
    
    def testUpdate(self):
        self.setup_helper('update')
        self.assert_not_authorized(update)
    
    def testView(self):
        self.setup_helper('view')
        self.view_helper()
    

class TestActivitiesControllerAsAdmin(TestActivitiesControllerWithFullAuth):
    
    def setUp(self):
        set_is_admin()
       
class TestActivitiesControllerAsEmployee(TestActivitiesControllerWithFullAuth):
    
    def setUp(self):
        set_is_employee()

class TestActivitiesControllerAsVolunteer(TestActivitiesControllerBase):
    
    def setUp(self):
        set_is_volunteer()
    
    def testCreate(self):
        self.setup_helper('create')
        self.create_helper()
    
    def testUpdate(self):
        self.setup_helper('update')
        self.update_helper()
    
    def testView(self):
        self.setup_helper('view')
        self.view_helper()

class TestActivitiesControllerAsAgency(TestActivitiesControllerAsReadOnly):
    
    def setUp(self):
        set_is_agency()

class TestActivitiesControllerAsClient(TestActivitiesControllerAsReadOnly):
    
    def setUp(self):
        set_is_client()


def add_tests():
    suite.addTest(unittest.makeSuite(TestActivitiesControllerAsAdmin))
    suite.addTest(unittest.makeSuite(TestActivitiesControllerAsEmployee))
    suite.addTest(unittest.makeSuite(TestActivitiesControllerAsVolunteer))
    suite.addTest(unittest.makeSuite(TestActivitiesControllerAsAgency))
    suite.addTest(unittest.makeSuite(TestActivitiesControllerAsClient))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed from runner.py
    add_tests()

