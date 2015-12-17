"""
Base Class Only. Not meant to be executed directly
"""
import unittest
from gluon.storage import Storage
from datetime import date
from applications.booking.tests.base import TestBase

class TestPeopleContollerBase(TestBase):
    
    USER_IDS = Storage(DEFAULT=1,SAME_ORG=1,OTHER_ORG=2,DEACTIVE=3,NO_ORG=4,INVALID=999999)
    
    def setup_db(self, person_type):
        """Helper method"""
        db(db.people.id>0).delete()
        db(db.organisations.id>0).delete()
        db(db.activities.id>0).delete()
        db.organisations.insert(id=1, name='Test', organisations_types='Referral Agency')
        db.people.insert(id=1,type=person_type, first_name='FName1', last_name='LName1', mobile='1', organisation=1, date_of_birth=parse_date('2011-02-03'),referral_contact_email='abc@email.com') #same org as auth user
        db.people.insert(id=2,type=person_type, first_name='FName2', last_name='LName2', mobile='2', organisation=2, date_of_birth=parse_date('2011-02-03'),referral_contact_email='abc@email.com') #different org than auth user
        db.people.insert(id=3,type=person_type, first_name='FName3', last_name='LName3', mobile='3', organisation=1, date_of_birth=parse_date('2011-02-03'),referral_contact_email='abc@email.com', deactivated=True)
        db.people.insert(id=4,type=person_type, first_name='FName4', last_name='LName4', mobile='4', organisation=None, date_of_birth=parse_date('2011-02-03'), referral_contact_email='abc@email.com') #no org
        db.activities.insert(person_id=1,date=date.today())        
    
    def setup_helper(self, controller, function, person_type):
        """ Helper method """
        self.setup_db(person_type)
        setup_function(self,controller,function)
        execfile('applications/booking/models/validations.py') #reset the validations based on request.controller
        self.index = index
        self.create = create
        self.update = update
        self.view = view
        self.person_type = person_type
        
        ###Init the permissions for views/html. Can be overwritten
        self.shows_activities = True
        self.shows_events = True
        self.creates_activities = True
        self.can_index = False #for breadcrumbs check
    
    def index_helper(self):
        """ Helper method """
        
        resp = self.index()
        length = len(resp['people'])
        expected = 1 if is_agency else 4 if can('activate', request.controller) else 3
        self.assertEquals(length, expected, 'wrong initial count: %i, expected %i' % (length,expected))
        
        ### Testing the search
        request.vars = Storage(first_name='XYZ')
        resp = self.index()
        length = len(resp['people'])
        self.assertEquals(length, 0, 'wrong count with fake name: %i' % length)
        
        #Testing 1 value exact
        request.vars = Storage(first_name='FName1')
        resp = self.index()
        length = len(resp['people'])
        self.assertEquals(length, 1, 'wrong count with exact first name filter: %i' % length)
        
        #Testing starts-with
        request.vars = Storage(first_name='F')
        resp = self.index()
        length = len(resp['people'])
        #expected = 2 if is_admin else 1
        self.assertEquals(length, expected, 'wrong count with first name "F" filter: %i, expected %i' % (length,expected))
        
        #Testing all 3 values
        request.vars = Storage(first_name='FName1', last_name='LName1', mobile='1', email='')
        resp = self.index()
        length = len(resp['people'])
        self.assertEquals(length, 1, 'wrong count with filter on all fields: %i' % length)
        self.resp = resp
    
    def create_update_helper(self, method):
        """ Helper method """
        resp = method() #get the form
        
        if method.__name__=='create':
            self.ui_test_helper_create(resp)
        else:        
            self.ui_test_helper_update(resp)
        
        form = resp.get('form')
        request.vars = Storage(_formname=form.formname, _formkey=form.formkey)
        resp = method() #post the invalid form
        form = resp.get('form')
        self.ui_test_helper_no_internal_errors(resp)
        self.assertTrue(form.errors)
        
        #rebuild valid vars with the new formkey
        request.vars = Storage(first_name='FirstName', last_name='LastName', 
                               mobile='12345678', email='first.last@example.com', 
                               gender='Female', clothing_size=CLOTHING_SIZES_SET[0],date_of_birth=parse_date('2011-02-03'), shoe_size=SHOE_SIZES_SET[0],
                               organisation='1', organisations_types='Referral Agency',contact_name='Contact Name', contact_number='111111',referral_contact_email='abc@email.com',
                               _formname=form.formname, _formkey=form.formkey)
        
        #post the valid form
        self.assert_redirect(method, f='view', a='\d+')
    
    def update_helper(self, authorized_on_other_org=True):
        set_args(self.USER_IDS.DEFAULT)
        self.create_update_helper(self.update)
        
        #test redirect on invalid client
        set_args(self.USER_IDS.INVALID)
        self.assert_redirect(self.update)
    
        #test redirect on deleted client
        set_args(self.USER_IDS.DEACTIVE)
        if can('activate', request.controller):
            self.update() #no redirect if user can activate
        else:
            self.assert_redirect(self.update)
        
        #test redirect on un-authed client
        set_args(self.USER_IDS.OTHER_ORG)
        if authorized_on_other_org:
            self.update()
        else:
            self.assert_not_authorized(self.update)
        
    
    def view_helper(self, authorized_on_other_org=True):
        set_args(self.USER_IDS.DEFAULT)
        resp = self.view()
        self.assertTrue(resp['activities']) if self.shows_activities else self.assertEquals(resp['activities'], None)
        self.assertTrue(resp['person'])
        
        self.ui_test_helper_view(resp)
        
        #test redirect on invalid client
        set_args(self.USER_IDS.INVALID)
        self.assert_redirect(self.view)
    
        #test redirect on deleted client
        set_args(self.USER_IDS.DEACTIVE)
        if can('activate', request.controller):
            self.view() #no redirect if user can activate
        else:
            self.assert_redirect(self.view)
        
        
        if authorized_on_other_org:
            #try viewing form a different org or no org
            set_args(self.USER_IDS.OTHER_ORG)
            self.view()
            set_args(self.USER_IDS.NO_ORG)
            resp = self.view()
            self.assertTrue(resp['person'])
        else:
            set_args(self.USER_IDS.OTHER_ORG)
            self.assert_not_authorized(self.view)
            set_args(self.USER_IDS.NO_ORG)
            self.assert_not_authorized(self.view)
    
    def ui_test_helper_create(self, d):
        self.html = render_helper(d)
        self.assertNoInternalErrors()
        self.assertInHtml('<h2>Create %s</h2>' % self.person_type)
        if self.can_index:
            self.assertInHtml('<span><a class="" href="/%s">Find %s</a></span> >' % (request.controller,self.person_type))
        self.assertInHtml('<table class="form-table">')
        self.assertInHtml('<td><input class="string" id="auth_user_first_name" name="first_name" type="text" value="" /></td>')
    
    def ui_test_helper_update(self, d):
        self.html = render_helper(d)
        self.assertNoInternalErrors()
        self.assertInHtml('<h2>Edit %s</h2>' % self.person_type )
        if self.can_index:
            self.assertInHtml('<span><a class="" href="/%s">Find %s</a></span> >' % (request.controller,self.person_type))
            self.assertInHtml('<span><a class="" href="/%s/view/1">View %s</a></span>' % (request.controller,self.person_type))
        self.assertInHtml('<table class="form-table">')
        self.assertInHtml('<td><input class="string" id="auth_user_first_name" name="first_name" type="text" value="FName1" /></td>')
    
    def ui_test_helper_no_internal_errors(self, d):
        self.html = render_helper(d)
        self.assertNoInternalErrors()
    
    def ui_test_helper_view(self, d, can_update=True, can_deactivate=False):
        self.html = render_helper(d)
        self.assertNoInternalErrors()
        
        if self.can_index:
            self.assertInHtml('<span><a class="" href="/%s">Find %s</a></span>' % (request.controller,self.person_type))
        self.assertInHtml('<h2>FName1 LName1</h2>')
        self.assertInHtml('<div class="infodisplay">')
        
        update_html = '<span><a class="button" href="/user/profile">Edit Profile</a></span>'
        self.assertInHtml(update_html) if can_update else self.assertNotHtml(update_html)
        
        #if is_admin:       
        #    self.assertInHtml('<span><a class="deactivate button" href="/deactivate/%s/1">Deactivate %s</a></span>' % (request.controller,self.person_type))
        #    if request.controller in ['clients', 'volunteers']:
        #        self.assertInHtml('<span><a class="button" href="/%s/enable_login/1">Enable Login</a></span>' % request.controller)
        #    else:
        #        self.assertInHtml('<span><a class="button" href="/%s/disable_login/1">Disable Login</a></span>' % request.controller)
        
        if self.shows_activities:
            self.assertInHtml('<span class="sh">Activities</span>')
            
            if self.creates_activities:
                self.assertInHtml('<tr class="clickable" onclick="go_to(\'/activities/update')
                self.assertInHtml('<span><a class="button" href="/activities/create?person=1">Add Activity</a></span>')
            else:
                self.assertInHtml('<tr class="clickable" onclick="go_to(\'/activities/view')
                self.assertNotInHtml('<span><a class="button" href="/activities/create?person=1">Add Activity</a></span>')
            
        if self.shows_events:
            self.assertInHtml('web2py_component("/events/index.load?person=1&person_type=%s"' % self.person_type)
        else:
            self.assertNotInHtml('web2py_component("/events/index.load?person=1&person_type=%s"' % self.person_type)
        
