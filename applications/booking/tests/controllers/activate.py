"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/activate.py
"""
from applications.booking.tests.base import TestBase

"""
View tests: No view tests are required for deactivate since all functions redirect. 
The page which it redirects to will be tested with their own controller.
"""

class TestDeactivateControllerBase(TestBase):
    
    def seed_data(self):
        """ Helper Method """
        db.organisations.insert(id=1,deactivated=True)
        db.people.insert(id=1, organisation=1,registration_key='disabled',deactivated=True)
        db.people.insert(id=2, organisation=1,registration_key='disabled',deactivated=True)
        db.people.insert(id=11,organisation=1,type=PERSON_TYPE_CLIENT,registration_key='disabled',deactivated=True)
        db.people.insert(id=12,organisation=1,type=PERSON_TYPE_EMPLOYEE,registration_key='disabled',deactivated=True)
        db.people.insert(id=13,organisation=1,type=PERSON_TYPE_AGENCY,registration_key='disabled',deactivated=True)
        db.people.insert(id=14,organisation=1,type=PERSON_TYPE_ADMIN,registration_key='disabled',deactivated=True)
        db.people.insert(id=15,organisation=1,type=PERSON_TYPE_VOLUNTEER,registration_key='disabled',deactivated=True)
    
    def setup_helper(self, function):
        """ Helper Method """
        setup_function(self,'activate',function)
        set_args(1) #add /1 to all urls
        db(db.activation_dates.id>0).delete()
        db(db.people.id>0).delete()
        db(db.organisations.id>0).delete()
        self.seed_data()
    
    def assert_activation_date_record(self, type=None, id=1, length=1):
        if type==None:
            type=request.function
        recs = db( (db.activation_dates.record_type==type) & (db.activation_dates.record_id==id) & (db.activation_dates.de_activate=='activate') ).select()
        self.assertEquals(len(recs), length)
    
class TestDeactivateControllerWithFullAuth(TestDeactivateControllerBase):
    """To be subclassed. Not to be run directly"""
    
    def testClients(self):
        """
        Client deactivate should cascade down to registrations and activities
        """
        self.setup_helper('clients')
        self.assert_redirect(clients, '/clients/view/1')
        self.assertTrue(resource_by_id(db.people, 1))
        self.assertEquals(resource_field_by_id(db.people, 'registration_key', 1), 'disabled')
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 1), False)
        self.assert_activation_date_record()     
    
    def testVolunteers(self):
        """
        Volunteer deactivate should cascade down to registrations and activities
        """
        self.setup_helper('volunteers')
        self.assert_redirect(volunteers, '/volunteers/view/1')
        self.assertTrue(resource_by_id(db.people, 1))
        self.assertEquals(resource_field_by_id(db.people, 'registration_key', 1), '')
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 1), False)
        self.assert_activation_date_record()
    
    def testEmployees(self):
        """
        Employee deactivate should cascade down to registrations and activities
        """
        self.setup_helper('employees')
        self.assert_redirect(employees, '/employees/view/1')
        self.assertTrue(resource_by_id(db.people, 1))
        self.assertEquals(resource_field_by_id(db.people, 'registration_key', 1), '')
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 1), False)
        self.assert_activation_date_record()
        
    def testAgency(self):
        """
        Agency deactivate does not cascade down to anything
        """
        self.setup_helper('agencies')
        self.assert_redirect(agencies, '/agencies/view/1')
        self.assertTrue(resource_by_id(db.people, 1))
        self.assertEquals(resource_field_by_id(db.people, 'deactivated', 1), False)
        self.assertEquals(resource_field_by_id(db.people, 'registration_key', 1), '')
        self.assert_activation_date_record()
        
    def testOrganisation(self):
        """
        Organisations deactivate should NOT cascade down to people 
        """
        self.setup_helper('organisations')
        self.assert_redirect(organisations, '/organisations/view/1')
        self.assertTrue(resource_by_id(db.organisations, 1))
        self.assertEquals(resource_field_by_id(db.organisations, 'deactivated', 1), False)
        self.assert_activation_date_record()


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

class TestDeactivateControllerAsEmployee(TestDeactivateControllerWithNoAuth):
    
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
