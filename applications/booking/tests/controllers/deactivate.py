"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/deactivate.py
"""
from applications.booking.tests.base import TestBase

"""
View tests: No view tests are required for deactivate since all functions redirect. 
The page which it redirects to will be tested with their own controller.
"""

class TestDeactivateControllerBase(TestBase):
    
    def seed_data(self):
        """ Helper Method """
        
        db.people.insert(id=1, organisation=1,date_of_birth=request.now.date())
        db.people.insert(id=2, organisation=1,date_of_birth=request.now.date())
        db.event_types.insert(id=1,name='Fitting')
        db.events.insert(id=1,type=1,is_full=True)
        db.events.insert(id=2,type=1,is_full=True)
        db.events.insert(id=3,type=1,is_full=True)
        db.registrations.insert(id=1, event=1, person=1)
        db.registrations.insert(id=2, event=1, person=2)
        db.registrations.insert(id=3, event=1, person=1)
        db.registrations.insert(id=4, event=1, person=2)
        db.registrations.insert(id=5, event=2, person=1)
        db.activities.insert(id=1, person_id=1)
        db.activities.insert(id=2, person_id=1)
        
        db.organisations.insert(id=1)
        db.people.insert(id=11,organisation=1,type=PERSON_TYPE_CLIENT,date_of_birth=request.now.date())
        db.people.insert(id=12,organisation=1,type=PERSON_TYPE_EMPLOYEE,date_of_birth=request.now.date())
        db.people.insert(id=13,organisation=1,type=PERSON_TYPE_AGENCY,date_of_birth=request.now.date())
        db.people.insert(id=14,organisation=1,type=PERSON_TYPE_ADMIN,date_of_birth=request.now.date())
        db.people.insert(id=15,organisation=1,type=PERSON_TYPE_VOLUNTEER,date_of_birth=request.now.date())
    
    def setup_helper(self, function):
        """ Helper Method """
        setup_function(self,'deactivate',function)
        set_args(1) #add /1 to all urls
        
        db(db.activation_dates.id>0).delete()
        db(db.people.id>0).delete()
        db(db.events.id>0).delete()
        db(db.event_types.id>0).delete()
        db(db.organisations.id>0).delete()
        db(db.activities.id>0).delete()
        self.seed_data()
        
    def assert_deactivation_date_record(self, type=None, id=1, length=1):
        if type==None:
            type=request.function
        recs = db( (db.activation_dates.record_type==type) & (db.activation_dates.record_id==id) & (db.activation_dates.de_activate=='deactivate') ).select()
        self.assertEquals(len(recs), length)
    
class TestDeactivateControllerWithFullAuth(TestDeactivateControllerBase):
    """To be subclassed. Not to be run directly"""
    
    def testClients(self):
        """
        Client deactivate should cascade down to registrations and activities
        """
        self.setup_helper('clients')
        self.assert_redirect(clients, '/clients/view')
        
        self.assert_deactivation_date_record()
        self.assertEquals(resource_by_id(db.people, 1), None)
        self.assertEquals(resource_by_id(db.registrations, 1), None)
        self.assertEquals(resource_by_id(db.registrations, 3), None)
        self.assertNotEquals(resource_by_id(db.activities, 1), None) #activities dont get deactivated
        self.assertNotEquals(resource_by_id(db.activities, 2), None) #activities dont get deactivated
        self.assertNotEquals(resource_by_id(db.events, 1), None) #events dont get deactivated
        self.assertEquals(resource_field_by_id(db.people, 'registration_key', 1), 'disabled')
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 1), True)
        self.assertEquals(resource_field_by_id(db.registrations, 'deactivated', 1), True)
        self.assertEquals(resource_field_by_id(db.registrations, 'deactivated', 3), True)
        self.assertEquals(resource_field_by_id(db.activities, 'deactivated', 1), False) #activities dont get deactivated
        self.assertEquals(resource_field_by_id(db.activities, 'deactivated', 2), False)  #activities dont get deactivated
        self.assertEquals(resource_field_by_id(db.events, 'deactivated', 1), False) #Event doesn't get deactivated
        self.assertEquals(resource_field_by_id(db.events, 'is_full', 1), False) #is_full goes back to False
        self.assertEquals(resource_field_by_id(db.events, 'is_full', 2), False) #is_full goes back to False
        self.assertEquals(resource_field_by_id(db.events, 'is_full', 3), True) #is_full stays True if this client was not registered
    
    
    def testVolunteers(self):
        """
        Volunteer deactivate should cascade down to registrations and activities
        """
        self.setup_helper('volunteers')
        self.assert_redirect(employees, '/volunteers/view')
        
        self.assert_deactivation_date_record()
        self.assertEquals(resource_by_id(db.people, 1), None)
        self.assertEquals(resource_by_id(db.registrations, 1), None)
        self.assertEquals(resource_by_id(db.registrations, 3), None)
        self.assertNotEquals(resource_by_id(db.activities, 1), None) #activities dont get deactivated
        self.assertNotEquals(resource_by_id(db.activities, 2), None) #activities dont get deactivated
        self.assertNotEquals(resource_by_id(db.events, 1), None) #events dont get deactivated
        self.assertEquals(resource_field_by_id(db.people, 'registration_key', 1), 'disabled')
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 1), True)
        self.assertEquals(resource_field_by_id(db.registrations, 'deactivated', 1), True)
        self.assertEquals(resource_field_by_id(db.registrations, 'deactivated', 3), True)
        self.assertEquals(resource_field_by_id(db.activities, 'deactivated', 1), False) #activities dont get deactivated
        self.assertEquals(resource_field_by_id(db.activities, 'deactivated', 2), False)  #activities dont get deactivated
        self.assertEquals(resource_field_by_id(db.events, 'deactivated', 1), False) #Event doesn't get deactivated
        self.assertEquals(resource_field_by_id(db.events, 'is_full', 1), True) #is_full stays full for volunteer deactivate
        self.assertEquals(resource_field_by_id(db.events, 'is_full', 2), True) #is_full stays full for volunteer deactivate
        self.assertEquals(resource_field_by_id(db.events, 'is_full', 3), True) #is_full stays full for volunteer deactivate
    
    def testEmployees(self):
        """
        Employee deactivate should cascade down to registrations and activities
        """
        self.setup_helper('employees')
        self.assert_redirect(employees, '/employees/view')
        
        self.assert_deactivation_date_record()
        self.assertEquals(resource_by_id(db.people, 1), None)
        self.assertEquals(resource_by_id(db.registrations, 1), None)
        self.assertEquals(resource_by_id(db.registrations, 3), None)
        self.assertNotEquals(resource_by_id(db.activities, 1), None) #activities dont get deactivated
        self.assertNotEquals(resource_by_id(db.activities, 2), None) #activities dont get deactivated
        self.assertNotEquals(resource_by_id(db.events, 1), None) #events dont get deactivated
        self.assertEquals(resource_field_by_id(db.people, 'registration_key', 1), 'disabled')
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 1), True)
        self.assertEquals(resource_field_by_id(db.registrations, 'deactivated', 1), True)
        self.assertEquals(resource_field_by_id(db.registrations, 'deactivated', 3), True)
        self.assertEquals(resource_field_by_id(db.activities, 'deactivated', 1), False) #activities dont get deactivated
        self.assertEquals(resource_field_by_id(db.activities, 'deactivated', 2), False)  #activities dont get deactivated
        self.assertEquals(resource_field_by_id(db.events, 'deactivated', 1), False) #Event doesn't get deactivated
        self.assertEquals(resource_field_by_id(db.events, 'is_full', 1), True) #is_full stays full for employee deactivate
        self.assertEquals(resource_field_by_id(db.events, 'is_full', 2), True) #is_full stays full for employee deactivate
        self.assertEquals(resource_field_by_id(db.events, 'is_full', 3), True) #is_full stays full for employee deactivate
    
    def testAgency(self):
        """
        Agency deactivate does not cascade down to anything
        """
        self.setup_helper('agencies')
        self.assert_redirect(agencies, '/agencies/view')
        
        self.assert_deactivation_date_record()
        self.assertEquals(resource_by_id(db.people, 1), None)
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 1), True)
        self.assertEquals(resource_field_by_id(db.people, 'registration_key', 1), 'disabled')
        
    
    def testEvents(self):
        """
        Events deactivate should cascade down to registrations 
        """
        self.setup_helper('events')
        self.assert_redirect(events, '/events')
        
        self.assert_deactivation_date_record()
        self.assertEquals(resource_by_id(db.events, 1), None)
        self.assertEquals(resource_by_id(db.registrations, 1), None)
        self.assertEquals(resource_by_id(db.registrations, 2), None)
        self.assertEquals(resource_field_by_id(db.registrations, 'deactivated', 1), True)
        self.assertEquals(resource_field_by_id(db.registrations, 'deactivated', 2), True)
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 1), False) #Client doesn't get deactivated
    
    def testOrganisation(self):
        """
        Organisations deactivate should NOT cascade down to people 
        """
        self.setup_helper('organisations')
        self.assert_redirect(organisations, '/organisations/view')
        
        self.assert_deactivation_date_record()
        self.assertEquals(resource_by_id(db.organisations, 1), None)
        self.assertEquals(resource_field_by_id(db.organisations, 'deactivated', 1), True)
        #None of the linked people should get deactivated
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 11), False)
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 12), False)
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 13), False)
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 14), False)


class TestDeactivateControllerWithNoAuth(TestDeactivateControllerBase):
    """To be subclassed. Not to be run directly"""
        
    def testClients(self):
        self.setup_helper('clients')
        self.assert_not_authorized(clients)
    
    def testEmployees(self):
        self.setup_helper('employees')
        self.assert_not_authorized(employees)
    
    def testVolunteers(self):
        self.setup_helper('volunteers')
        self.assert_not_authorized(volunteers)
    
    def testThirdParties(self):
        self.setup_helper('agencies')
        self.assert_not_authorized(agencies)
    
    def testOrganisations(self):
        self.setup_helper('organisations')
        self.assert_not_authorized(organisations)
    
    def testEvents(self):
        self.setup_helper('events')
        self.assert_not_authorized(events)
    

class TestDeactivateControllerAsAdmin(TestDeactivateControllerWithFullAuth):

    def setUp(self):
        set_is_admin()

class TestDeactivateControllerAsClient(TestDeactivateControllerWithNoAuth):
    
    def setUp(self):
        set_is_client()

class TestDeactivateControllerAsAgency(TestDeactivateControllerWithNoAuth):
    
    def setUp(self):
        set_is_agency()

class TestDeactivateControllerAsVolunteer(TestDeactivateControllerWithNoAuth):
    
    def setUp(self):
        set_is_volunteer()        

class TestDeactivateControllerAsEmployee(TestDeactivateControllerWithFullAuth):
    
    def setUp(self):
        set_is_employee()
    

def add_tests():
    suite.addTest(unittest.makeSuite(TestDeactivateControllerAsAdmin))
    suite.addTest(unittest.makeSuite(TestDeactivateControllerAsClient))
    suite.addTest(unittest.makeSuite(TestDeactivateControllerAsAgency))
    suite.addTest(unittest.makeSuite(TestDeactivateControllerAsEmployee))
    suite.addTest(unittest.makeSuite(TestDeactivateControllerAsVolunteer))

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed from runner.py
    add_tests()
