"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/registrations.py
"""
import unittest
import gluon as gluon
from gluon.globals import Request, Response
from gluon.storage import Storage
from applications.booking.tests.base import TestBase

class TestRegistrationsControllerBase(TestBase):
    
    DEFAULT_SLOTS = 2
    CLIENT_1 = '1'
    CLIENT_2 = '2'
    CLIENT_D = '3'
    ADMIN_ID = '4'
    THIRD_PARTY_ID = '5'
    EMPLOYEE_1 = '6'
    EMPLOYEE_2 = '7'
    EMPLOYEE_D = '8'
    VOLUNTEER_1 = '9'
    VOLUNTEER_2 = '10'
    VOLUNTEER_D = '11'
    
    def class_reset_db(self):
        """Helper method"""
        db(db.people.id > 0).delete()
        db(db.events.id > 0).delete()
        db(db.organisations.id > 0).delete()
        db.organisations.insert(id=1, name='Test')
        db.people.insert(id=int(self.CLIENT_1), type=PERSON_TYPE_CLIENT, first_name='John', last_name='Doe', mobile='12345', organisation=1, date_of_birth=request.now.date(),email='client@email.com')
        db.people.insert(id=int(self.CLIENT_2), type=PERSON_TYPE_CLIENT, first_name='Jane', last_name='Doe', mobile='12345', organisation=2, date_of_birth=request.now.date(),email='client1@email.com')
        db.people.insert(id=int(self.CLIENT_D), type=PERSON_TYPE_CLIENT, first_name='Kyle', last_name='Kelly', mobile='12345', organisation=1,date_of_birth=request.now.date(), deactivated=True)
        db.people.insert(id=int(self.ADMIN_ID), type='Admin', first_name='Admin', last_name='Admin', mobile='12345',date_of_birth=request.now.date())
        db.people.insert(id=int(self.THIRD_PARTY_ID), type=PERSON_TYPE_AGENCY, first_name='Party', last_name='Admin', mobile='12345',date_of_birth=request.now.date())
        db.people.insert(id=int(self.EMPLOYEE_1), type=PERSON_TYPE_EMPLOYEE, first_name='John', last_name='Doe', mobile='12345', organisation=1,date_of_birth=request.now.date(),email='employee1@email.com')
        db.people.insert(id=int(self.EMPLOYEE_2), type=PERSON_TYPE_EMPLOYEE, first_name='Jane', last_name='Doe', mobile='12345', organisation=2,date_of_birth=request.now.date(),email='employee@email.com')
        db.people.insert(id=int(self.EMPLOYEE_D), type=PERSON_TYPE_EMPLOYEE, first_name='Kyle', last_name='Kelly', mobile='12345', organisation=1,date_of_birth=request.now.date() ,deactivated=True)
        db.people.insert(id=int(self.VOLUNTEER_1), type=PERSON_TYPE_VOLUNTEER, first_name='Joe', last_name='Smith', mobile='12345', organisation=1,date_of_birth=request.now.date(),email='volunteer1@email.com')
        db.people.insert(id=int(self.VOLUNTEER_2), type=PERSON_TYPE_VOLUNTEER, first_name='george', last_name='bush', mobile='12345', organisation=1,date_of_birth=request.now.date(),email='volunteer@email.com')
        db.events.insert(id=1, type=1, name='Test Event1', slots=self.DEFAULT_SLOTS)
        db.events.insert(id=2, type=1, name='Test Event2', slots=self.DEFAULT_SLOTS)
        db.events.insert(id=3, type=1, name='Test Event', slots=self.DEFAULT_SLOTS, deactivated=True)
        db.events.insert(id=4, type=1, name='Test Event', slots=self.DEFAULT_SLOTS, date=date(1999, 01, 01))
        
    
    def seed_reg_data(self, insert_vars_person=True, slots=DEFAULT_SLOTS):
        """Helper method"""
        if insert_vars_person:
            db.registrations.insert(event=1, person=int(self.CLIENT_1), type=PERSON_TYPE_CLIENT) #vars client
            db.registrations.insert(event=1, person=int(self.EMPLOYEE_1), type=PERSON_TYPE_EMPLOYEE) #vars employee
            db.registrations.insert(event=1, person=int(self.VOLUNTEER_1), type=PERSON_TYPE_VOLUNTEER) #vars volunteer
            self.TOTAL_REGISTRATIONS = 6 #doesn't include deactivated
            self.client_slots_taken = 2
        else:
            self.TOTAL_REGISTRATIONS = 3 #doesn't include deactivated
            self.client_slots_taken = 1
        
        db.registrations.insert(event=1, person=int(self.CLIENT_2), type=PERSON_TYPE_CLIENT)
        db.registrations.insert(event=1, person=int(self.CLIENT_D), type=PERSON_TYPE_CLIENT, deactivated=True)
        db.registrations.insert(event=1, person=int(self.EMPLOYEE_2), type=PERSON_TYPE_EMPLOYEE)
        db.registrations.insert(event=1, person=int(self.EMPLOYEE_D), type=PERSON_TYPE_EMPLOYEE, deactivated=True)
        db.registrations.insert(event=1, person=int(self.VOLUNTEER_2), type=PERSON_TYPE_VOLUNTEER)
        db.registrations.insert(event=1, person=int(self.VOLUNTEER_D), type=PERSON_TYPE_VOLUNTEER, deactivated=True)
        
        self.client_spots_available = slots - self.client_slots_taken  
        self.init_is_full = (self.client_spots_available <= 0)
        db(db.events.id == 1).update(is_full=self.init_is_full)
        db(db.events.id == 1).update(slots=slots)
    
    def setup_helper(self, function, auth_id='0', resetdb=True, insert_vars_person=True, slots=DEFAULT_SLOTS):
        """Helper method"""
        setup_function(self, 'registrations', function)
        
        #self.init_is_full = insert_vars_person if init_is_full==None else init_is_full
        if resetdb:
            db(db.registrations.id > 0).delete()
            self.seed_reg_data(insert_vars_person, slots)
        
        #Reset up the auth
        user_type = resource_field_by_id(db.people, 'type', int(auth_id))
        auth.user = gluon.storage.Storage(id=int(auth_id), type=user_type, organisation=1, first_name='First', last_name='Last', mobile='12345',date_of_birth=request.now.date)


class TestRegistrationsControllerWithFullAuth(TestRegistrationsControllerBase):
    
    def test1_ClassSetup(self):
        self.class_reset_db()
    
    def testManage_NoEventId(self):
        ### R.A.M.1 ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID)
        request.vars = Storage()
        resp = manage()
        self.assertEquals(response.view, 'error.load')
        self.assertEquals(resp, 'No event id provided')
    
    def testManage_ViewWithoutPersonInVars(self):
        ### R.A.M.2 ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID)
        request.vars = Storage(event='1')
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'You must use the Client/Employee/Volunteer page for registration or un-registration.')
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(resp.get('form'), None)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, True)
        
    
    def testManage_ViewWithUnregisteredClient(self):
        ### R.A.M.3 ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID, insert_vars_person=False)
        request.vars = Storage(event='1', person=self.CLIENT_1)
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 1')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) is <strong>not registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertTrue(resp['person'])
        self.assertEquals(resp['person_name'], 'John Doe (12345)')
        self.assertTrue('register' in str(resp.get('form')))
        self.assertTrue('John Doe (12345)' in str(resp.get('form')))
        self.assertEquals(resp['is_full'], False)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no client registration changes
        
    
    def testManage_RegisterClientWithSpotAvailable(self):
        ### R.A.M.4 ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID, insert_vars_person=False)
        self.assertEquals(db.events(1).is_full, False) ##Initially not full
        request.vars = request.post_vars = Storage(event='1', person=self.CLIENT_1, register='X')
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) has been <strong>registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS) #won't include the new one
        self.assertTrue('value="Unregister"' in str(resp.get('form')))
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, True) ##Changed
        
    
    def testManage_ViewWithUnregisteredClientAndNoSlots(self):
        ### R.A.M.5 ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID, insert_vars_person=False, slots=1)
        request.vars = Storage(event='1', person=self.CLIENT_1)
        resp = manage()
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(resp['person_name'], 'John Doe (12345)')
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(resp.get('form'), 'There are no client spots available.')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) is <strong>not registered</strong> for this event.')
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no client registration changes
        
    
    def testMange_RegisterClientWithNoSpotsAvailable(self):
        ### R.A.M.6 ###
        ### Register attempt is ignored 
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID, insert_vars_person=False, slots=1)
        request.vars = request.post_vars = Storage(event='1', person=self.CLIENT_1, register='X')
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'We\'re sorry, but there are no spots available.')
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS) #won't include the new one
        self.assertEquals(resp.get('form'), 'There are no client spots available.')
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no client registration changes
        
    
    def testManage_ViewWithUnregisteredEmployee(self):
        ### R.A.M.7 ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID, insert_vars_person=False)
        request.vars = Storage(event='1', person=self.EMPLOYEE_1)
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 1')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) is <strong>not registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertTrue(resp['person'])
        self.assertEquals(resp['person_name'], 'John Doe (12345)')
        self.assertTrue('register' in str(resp.get('form')))
        self.assertTrue('John Doe (12345)' in str(resp.get('form')))
        self.assertEquals(resp['is_full'], False)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no client registration changes
        
    
    def testManage_RegisterEmployeeWithSpotAvailable(self):
        ### R.A.M.8 ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID, insert_vars_person=False)
        request.vars = request.post_vars = Storage(event='1', person=self.EMPLOYEE_1, register='X')
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 1')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) has been <strong>registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS) #won't include the new one
        self.assertTrue('value="Unregister"' in str(resp.get('form')))
        self.assertEquals(resp['is_full'], False)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no client registration changes
        
    
    def testManage_ViewWithUnregisteredEmployeeAndNoSlots(self):
        ### R.A.M.9 ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID, insert_vars_person=False, slots=1)
        request.vars = Storage(event='1', person=self.EMPLOYEE_1)
        resp = manage()
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(resp['person_name'], 'John Doe (12345)')
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) is <strong>not registered</strong> for this event.')
        self.assertTrue(resp['person'])
        self.assertEquals(resp['person_name'], 'John Doe (12345)')
        self.assertTrue('register' in str(resp.get('form')))
        self.assertTrue('John Doe (12345)' in str(resp.get('form')))
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no client registration changes
        
    
    def testMange_RegisterEmployeeWithNoClientSpotsAvailable(self):
        ### R.A.M.10 ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID, insert_vars_person=False, slots=1)
        request.vars = request.post_vars = Storage(event='1', person=self.EMPLOYEE_1, register='X')
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) has been <strong>registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS) #won't include the new one
        self.assertTrue('value="Unregister"' in str(resp.get('form')))
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no client registration changes
        
    
    def testManage_ViewWithRegisteredClient(self):
        ### R.A.M.11 ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID, insert_vars_person=True)
        request.vars = Storage(event='1', person=self.CLIENT_1)
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) is <strong>registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertTrue('value="Unregister"' in str(resp.get('form')))
        self.assertEquals(resp['person_name'], 'John Doe (12345)')
        self.assertTrue(resp['person'])
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no registration changes
        
    
    def testManage_ViewWithRegisteredEmployee(self):
        ### R.A.M.12 ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID, insert_vars_person=True)
        request.vars = Storage(event='1', person=self.EMPLOYEE_1)
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) is <strong>registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertTrue('value="Unregister"' in str(resp.get('form')))
        self.assertEquals(resp['person_name'], 'John Doe (12345)')
        self.assertTrue(resp['person'])
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, True) ##default since no registration changes
        
    
    def testManage_UnregisterClient(self):
        ### R.A.M.13 (a) ###
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID)
        self.assertEquals(db.events(1).is_full, True) ##Initially full
        
        request.vars = request.post_vars = Storage(event='1', person=self.CLIENT_1, unregister='X')
        resp = manage()
        self.assertEquals(resp['slots_message'], 'Client spots available: 1')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) has been <strong>un-registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS-1) #-1 for the unregister
        self.assertTrue('value="Register"' in str(resp.get('form')))
        self.assertTrue('John Doe (12345)' in str(resp.get('form')))
        self.assertEquals(resp['person_name'], 'John Doe (12345)')
        self.assertTrue(resp['person'])
        self.assertEquals(resp['is_full'], False)
        self.assertEquals(db.events(1).is_full, False) ##Changed

    def testManage_cannotRegisterInPastDate(self):
        self.setup_helper(function='manage', auth_id=self.ADMIN_ID)
        request.vars = Storage(event='4', person=self.EMPLOYEE_1)
        resp = manage()
        self.assertEquals(form, 'Cannot register or unregister for an event in the past.')
    

class TestRegistrationsControllerWithAuthByOrg(TestRegistrationsControllerBase):
    """
    Most auth by org behavior is the same as full auth. These tests focus on the auth differences only
    """
    
    def test1_ClassSetup(self):
        self.class_reset_db()
    
    def testManage_ViewClientFromDifferentOrg(self):
        ### R.T.M. 1 (view) ###
        self.setup_helper(function='manage', auth_id=self.THIRD_PARTY_ID, slots=5)
        request.vars = request.post_vars = Storage(event='1', person=self.CLIENT_2)
        resp = manage()
        self.assertEquals(resp['slots_message'], 'Client spots available: 3')
        self.assertEquals(str(resp['registration_message']), 'You do not have authorization to register this person.')
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertEquals(resp['is_full'], False)
        self.assertEquals(db.events(1).is_full, False)    
        self.assertEquals(resp.get('form'), None)
        self.assertEquals(resp['person'], None)
        self.assertEquals(resp['person_name'], None)
    
    def testManage_RegisterClientFromDifferentOrg(self):
        ### R.T.M. 1 (register) ###
        self.setup_helper(function='manage', auth_id=self.THIRD_PARTY_ID)
        request.vars = request.post_vars = Storage(event='1', person=self.CLIENT_2, register='X') 
        resp = manage()
        self.assertEquals(str(resp['registration_message']), 'You do not have authorization to register this person.')
        self.assertEquals(resp.get('form'), None)
        self.assertEquals(resp['person'], None)
        self.assertEquals(resp['person_name'], None)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no registration changes
        
    def testManage_UnregisterClientFromDifferentOrg(self):
        ### R.T.M. 1 (unregister) ###
        self.setup_helper(function='manage', auth_id=self.THIRD_PARTY_ID)
        request.vars = request.post_vars = Storage(event='1', unregister='X', person=self.CLIENT_2) 
        resp = manage()
        self.assertEquals(str(resp['registration_message']), 'You do not have authorization to register this person.')
        self.assertEquals(resp.get('form'), None)
        self.assertEquals(resp['person'], None)
        self.assertEquals(resp['person_name'], None)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no registration changes
        
    
    def testManage_ViewEmployeeFromDifferentOrg(self):
        ### R.T.M. 2 (view) ###
        self.setup_helper(function='manage', auth_id=self.THIRD_PARTY_ID)
        request.vars = request.post_vars = Storage(event='1', person=self.EMPLOYEE_2)
        resp = manage()
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'You do not have authorization to register this person.')
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertEquals(resp.get('form'), None)
        self.assertEquals(resp['person'], None)
        self.assertEquals(resp['person_name'], None)
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no registration changes
        
    
    def testManage_RegisterEmployeeFromDifferentOrg(self):
        ### R.T.M. 2 (register) ###
        self.setup_helper(function='manage', auth_id=self.THIRD_PARTY_ID)
        request.vars = request.post_vars = Storage(event='1', person=self.EMPLOYEE_2, register='X') 
        resp = manage()
        self.assertEquals(str(resp['registration_message']), 'You do not have authorization to register this person.')
        self.assertEquals(resp.get('form'), None)
        self.assertEquals(resp['person'], None)
        self.assertEquals(resp['person_name'], None)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no registration changes
        
    
    def testManage_UnregisterEmployeeFromDifferentOrg(self):
        ### R.T.M. 2 (unregister) ###
        self.setup_helper(function='manage', auth_id=self.THIRD_PARTY_ID)
        request.vars = request.post_vars = Storage(event='1', unregister='X', person=self.EMPLOYEE_2) 
        resp = manage()
        self.assertEquals(str(resp['registration_message']), 'You do not have authorization to register this person.')
        self.assertEquals(resp.get('form'), None)
        self.assertEquals(resp['person'], None)
        self.assertEquals(resp['person_name'], None)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, self.init_is_full) ##default since no registration changes
        
    
    def testManage_ViewUnregisteredClientFromSameOrg(self):
        ### R.T.M.3 (view) ###
        self.setup_helper(function='manage', auth_id=self.THIRD_PARTY_ID, insert_vars_person=False)
        request.vars = Storage(event='1', person=self.CLIENT_1)
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 1')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) is <strong>not registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertTrue(resp['person'])
        self.assertEquals(resp['person_name'], 'John Doe (12345)')
        self.assertTrue('value="Register"' in str(resp.get('form')))
        self.assertTrue('John Doe (12345)' in str(resp.get('form')))
        self.assertEquals(resp['is_full'], False)
        self.assertEquals(db.events(1).is_full, self.init_is_full)
        
    def testManage_RegisterClientFromSameOrg(self):
        ### R.T.M.3 (register) ###
        self.setup_helper(function='manage', auth_id=self.THIRD_PARTY_ID, insert_vars_person=False)
        request.vars = request.post_vars = Storage(event='1', person=self.CLIENT_1, register='X')
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) has been <strong>registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertTrue('value="Unregister"' in str(resp.get('form')))
        self.assertEquals(resp['is_full'], True)
        self.assertEquals(db.events(1).is_full, True)  
    
    def testManage_UnregisterClientFromSameOrg(self):
        ### R.T.M.3 (unregister) ###
        self.setup_helper(function='manage', auth_id=self.THIRD_PARTY_ID)
        request.vars = request.post_vars = Storage(event='1', person=self.CLIENT_1, unregister='X')
        resp = manage()
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) has been <strong>un-registered</strong> for this event.')
        self.assertEquals(resp['slots_message'], 'Client spots available: 1')
        self.assertTrue('value="Register"' in str(resp.get('form')))
        self.assertEquals(resp['is_full'], False)
        self.assertEquals(db.events(1).is_full, False)
    
    def testManage_ViewUnregisteredEmployeeFromSameOrg(self):
        ### R.T.M.4 (view) ###
        self.setup_helper(function='manage', auth_id=self.THIRD_PARTY_ID, insert_vars_person=False)
        request.vars = Storage(event='1', person=self.EMPLOYEE_1)
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 1')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) is <strong>not registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertTrue(resp['person'])
        self.assertEquals(resp['person_name'], 'John Doe (12345)')
        self.assertTrue('register' in str(resp.get('form')))
        self.assertTrue('John Doe (12345)' in str(resp.get('form')))
        self.assertEquals(resp['is_full'], False)
        self.assertEquals(db.events(1).is_full, self.init_is_full)
    
    def testManage_RegisterEmployeeFromSameOrg(self):
        ### R.T.M.3 (register) ###
        self.setup_helper(function='manage', auth_id=self.THIRD_PARTY_ID, insert_vars_person=False)
        request.vars = request.post_vars = Storage(event='1', person=self.EMPLOYEE_1, register='X')
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['slots_message'], 'Client spots available: 1')
        self.assertEquals(str(resp['registration_message']), 'John Doe (12345) has been <strong>registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(len(resp['registrations']), self.TOTAL_REGISTRATIONS)
        self.assertTrue('value="Unregister"' in str(resp.get('form')))
        self.assertEquals(resp['is_full'], False)
        self.assertEquals(db.events(1).is_full, self.init_is_full)
    


class TestRegistrationsControllerAsClient(TestRegistrationsControllerBase):
    
    def setUp(self):
        set_is_client()
    
    def test1_ClassSetup(self):
        self.class_reset_db()
    
    def testManageSelf_NoEventId(self):
        self.setup_helper(function='manage', auth_id=self.CLIENT_1, insert_vars_person=False)
        request.vars = Storage()
        resp = manage()
        self.assertEquals(response.view, 'error.load')
        self.assertEquals(resp, 'No event id provided')
    
    def testManageSelf_ViewWhenNotRegisteredAndNotFull(self):
        self.setup_helper(function='manage', auth_id=self.CLIENT_1, insert_vars_person=False)
        request.vars = Storage(event='1')
        resp = manage()
        self.assertEquals(resp['event_id'], '1')
        self.assertEquals(resp['person_name'], 'First Last (12345)') #from auth.user
        self.assertEquals(resp['slots_message'], 'Client spots available: 1')
        self.assertEquals(str(resp['registration_message']), 'You are <strong>not registered</strong> for this event.')
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(resp.get('form'), None)
        
        ### Test that with input slots will override the event slots
        request.vars = Storage(event='1', slots='1000')
        resp = manage()
        self.assertEquals(resp['slots_message'], 'Client spots available: 999')
    
    def testManageSelf_ViewWhenRegistered(self):
        self.setup_helper(function='manage', auth_id=self.CLIENT_1)
        request.post_vars = Storage()
        request.vars = Storage(event='1')
        resp = manage()
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'You are <strong>registered</strong> for this event.')
        self.assertEquals(resp.get('form'), None)
    
    def testManageSelf_RegisterSelfIgnored(self):
        ### R.C.M.3 ###
        self.setup_helper(function='manage', auth_id=self.CLIENT_1, insert_vars_person=False)
        request.post_vars = request.vars = Storage(event='1', register='X')
        resp = manage()
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(resp['slots_message'], 'Client spots available: 1')
        self.assertEquals(str(resp['registration_message']), 'You are <strong>not registered</strong> for this event.')
        self.assertEquals(resp.get('form'), None)
    
    def testManageSelf_UnregisterSelfIgnored(self):
        ### R.C.M.5 ###
        self.setup_helper(function='manage', auth_id=self.CLIENT_1)
        request.post_vars = request.vars = Storage(event='1', unregister='X')
        resp = manage()
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'You are <strong>registered</strong> for this event.')        
        self.assertEquals(resp.get('form'), None)
    
    def testManageOtherIgnored(self):
        ### R.C.M.8 ###
        self.setup_helper(function='manage', auth_id=self.CLIENT_1, insert_vars_person=False, slots=5)
        request.post_vars = request.vars = Storage(event='1', person=self.CLIENT_2)
        resp = manage()
        self.assertEquals(resp['person'].id, int(self.CLIENT_1))
        self.assertEquals(resp['person_name'], 'First Last (12345)') #values from auth user
    
    def testManageSelf_RegisterWhenAlreadyRegistered(self):
        ### R.C.M.9 ###
        self.setup_helper(function='manage', auth_id=self.CLIENT_1, insert_vars_person=True, slots=5)
        request.post_vars = request.vars = Storage(event='1', register='X')
        resp = manage()
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(resp['slots_message'], 'Client spots available: 3')
        self.assertEquals(str(resp['registration_message']), 'You are <strong>registered</strong> for this event.')
        self.assertEquals(resp.get('form'), None)

class TestRegistrationsControllerAsAdmin(TestRegistrationsControllerWithFullAuth):
    
    def setUp(self):
        set_is_admin()

class TestRegistrationsControllerAsEmployee(TestRegistrationsControllerWithFullAuth):
    
    def setUp(self):
        set_is_employee()

class TestRegistrationsControllerAsVolunteer(TestRegistrationsControllerBase):
    
    def setUp(self):
        set_is_volunteer()

    def test1_ClassSetup(self):
        self.class_reset_db()

    def testManageSelf_NoEventId(self):
        self.setup_helper(function='manage', auth_id=self.CLIENT_1, insert_vars_person=False)
        request.vars = Storage()
        resp = manage()
        self.assertEquals(response.view, 'error.load')
        self.assertEquals(resp, 'No event id provided')
    
    def testManageSelf_ViewWhenRegistered(self):
        self.setup_helper(function='manage', auth_id=self.VOLUNTEER_1)
        request.post_vars = Storage()
        request.vars = Storage(event='1', person=self.VOLUNTEER_1)
        resp = manage()
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(str(resp['registration_message']), 'You are <strong>registered</strong> for this event.')
        self.assertEquals(resp.get('form'), None)

    def testManageSelf_ViewWhenNotRegisted(self):
        self.setup_helper(function='manage', auth_id=self.VOLUNTEER_1, insert_vars_person=False)
        request.post_vars = Storage()
        request.vars = Storage(event='1')
        resp = manage()
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(str(resp['registration_message']), 'You are <strong>not registered</strong> for this event.')
        self.assertEquals(resp.get('form'), None)

    def testManageOtherIgnored(self):
        self.setup_helper(function='manage', auth_id=self.VOLUNTEER_1, insert_vars_person=False, slots=5)
        request.post_vars = request.vars = Storage(event='1', person=self.VOLUNTEER_2)
        resp = manage()
        self.assertEquals(resp['person'].id, int(self.VOLUNTEER_1))
        self.assertEquals(resp['person_name'], 'First Last (12345)') #values from auth user
        self.assertEquals(resp.get('form'), None)
    
    def testManageSelf_RegisterSelfIgnored(self):
        ### R.C.M.3 ###
        self.setup_helper(function='manage', auth_id=self.VOLUNTEER_1, insert_vars_person=False)
        request.post_vars = request.vars = Storage(event='1', register='X')
        resp = manage()
        self.assertEquals(resp['is_registered'], False)
        self.assertEquals(resp['slots_message'], 'Client spots available: 1')
        self.assertEquals(str(resp['registration_message']), 'You are <strong>not registered</strong> for this event.')
        self.assertEquals(resp.get('form'), None)
    
    def testManageSelf_UnregisterSelfIgnored(self):
        self.setup_helper(function='manage', auth_id=self.VOLUNTEER_1)
        request.post_vars = request.vars = Storage(event='1', unregister='X')
        resp = manage()
        self.assertEquals(resp['is_registered'], True)
        self.assertEquals(resp['slots_message'], 'Client spots available: 0')
        self.assertEquals(str(resp['registration_message']), 'You are <strong>registered</strong> for this event.')
        self.assertEquals(resp.get('form'), None)
    
    
    
class TestRegistrationsControllerAsAgency(TestRegistrationsControllerWithAuthByOrg):
    def setUp(self):
        set_is_agency()


def add_tests():
    suite.addTest(unittest.makeSuite(TestRegistrationsControllerAsAdmin))
    suite.addTest(unittest.makeSuite(TestRegistrationsControllerAsAgency))
    suite.addTest(unittest.makeSuite(TestRegistrationsControllerAsEmployee))
    suite.addTest(unittest.makeSuite(TestRegistrationsControllerAsClient))
    suite.addTest(unittest.makeSuite(TestRegistrationsControllerAsVolunteer))


if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed from runner.py
    add_tests()
