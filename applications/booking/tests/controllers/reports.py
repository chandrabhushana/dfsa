"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/reports.py

"""
from applications.booking.tests.base import TestBase
from gluon.storage import Storage
from datetime import datetime, timedelta

class TestReportsControllerBase(TestBase):
    """ Helpers only. To be subclassed"""
    
    START_DATE = datetime(2000,01,01)
    END_DATE = datetime(2000,02,01,1,1,1)
    START_DATE_STR = START_DATE.strftime('%d-%m-%Y')
    END_DATE_STR = END_DATE.strftime('%d-%m-%Y')
    
    ALL_FITTING_CSV = """fitting_date,visit,visits,first_name,last_name,contact,gender,age_range,ethnicity,shoe_size,clothing_size
1999-12-30,1,6,FName1,LName1,,Female,,,,
1999-12-31,2,6,FName1,LName1,,Female,,,,
2000-01-01,3,6,FName1,LName1,,Female,,,,
2000-01-02,4,6,FName1,LName1,,Female,,,,
2000-02-01,5,6,FName1,LName1,,Female,,,,
2000-02-02,6,6,FName1,LName1,,Female,,,,
2000-01-02,1,1,FName4,LName4,,Male,,,,
"""
 
    def result(self, resp):
        return resp.get('result')
    
    def result_length(self, resp):
        return len(self.result(resp))
    
    def setup_helper(self, function='index'):
        """ Helper method """
        setup_function(self,'reports',function)
    
    def setup_client_db(self):
        db(db.people.id>0).delete()
        db(db.activities.id>0).delete()
        db(db.organisations.id>0).delete()
        
        """Report Data: 
        Client 1 
            - 1 first time visit before the start filter
            - 5 return visits. one before the start filter, 1 on start filter, 1 between filters, 1 on end filter, 1 after end filter
            - 1 no show
            - 1 non Fitting (should not show up)
        
        Client 2 - no activities (tests that no activities will not cause issues)
        
        Client 3 (deactivated client) - some activities
            *tests that being deactivated and having no organisation will have no effect
            -1 activity between the date filters
        
        Volunteer 1 - tests that only client data gets returned
        """
        
        CLIENT_1 = 1
        CLIENT_2 = 2
        CLIENT_3 = 3
        VOLUNTEER_1 = 4
        VOLUNTEER_2 = 5
        EMPLOYEE_1=6
        AGENCY_USER = 7

        db.people.insert(id=CLIENT_1,type=PERSON_TYPE_CLIENT, gender='Female', first_name='FName1', last_name='LName1', mobile='1', organisation=1,date_of_birth=request.now.date())
        db.people.insert(id=CLIENT_2,type=PERSON_TYPE_CLIENT, gender='Female', first_name='FName2', last_name='LName2', mobile='2', organisation=2,date_of_birth=request.now.date())        
        db.people.insert(id=CLIENT_3,type=PERSON_TYPE_CLIENT, gender='Male', first_name='FName4', last_name='LName4', mobile='4', organisation=None, date_of_birth=request.now.date(), deactivated=True)
        db.people.insert(id=VOLUNTEER_1,type=PERSON_TYPE_VOLUNTEER, gender='Female', first_name='FName2', last_name='LName2', mobile='2', organisation=1, date_of_birth=request.now.date())
        db.people.insert(id=VOLUNTEER_2,type=PERSON_TYPE_VOLUNTEER, gender='Male', first_name='FName2', last_name='LName2', mobile='2', organisation=2, date_of_birth=request.now.date())
        db.people.insert(id=EMPLOYEE_1,type=PERSON_TYPE_EMPLOYEE, gender='Male', first_name='FName2', last_name='LName2', mobile='2', organisation=1, date_of_birth=request.now.date())
        db.people.insert(id=AGENCY_USER,type=PERSON_TYPE_AGENCY, first_name='FName2', last_name='LName2', mobile='2', date_of_birth=request.now.date())
        
        """ 7 total Fitting (across 2 clients) """ 
        db.activities.insert(person_id=CLIENT_1,type='Fitting', date=self.START_DATE-timedelta(days=2)) #first visit
        db.activities.insert(person_id=CLIENT_1,type='Fitting', date=self.START_DATE-timedelta(days=1)) #return before start filter (should not be in fitlered result)
        db.activities.insert(person_id=CLIENT_1,type='Fitting', date=self.START_DATE)                   #return on start filter (should be in filtered result) 
        db.activities.insert(person_id=CLIENT_1,type='Fitting', date=self.START_DATE+timedelta(days=1)) #return between filters
        db.activities.insert(person_id=CLIENT_1,type='Fitting', date=self.END_DATE)                     #return on end filter   (should be in filtered result)
        db.activities.insert(person_id=CLIENT_1,type='Fitting', date=self.END_DATE+timedelta(days=1))   #return after end filter (should not be in fitlered result)
        db.activities.insert(person_id=CLIENT_3,type='Fitting', date=self.START_DATE+timedelta(days=1)) #first visit
        
        #add some items provided
        db(db.activities.person_id==CLIENT_1).update(gender='Female', nbr_skirts=1)
        db(db.activities.person_id==CLIENT_3).update(gender='Male', nbr_golfshirts=1)
        
        """No shows - 3 within date filters"""
        db.activities.insert(person_id=CLIENT_1,type='Fitting', is_no_show=True, date=self.START_DATE+timedelta(days=1)) #should be included with date filter for no show
        db.activities.insert(person_id=CLIENT_1,type='Other', is_no_show=True, date=self.START_DATE) #should be counted with date filter
        db.activities.insert(person_id=CLIENT_1,type='Other', is_no_show=True, date=self.END_DATE) #should be counted with date filter
        db.activities.insert(person_id=CLIENT_1,type='Other', is_no_show=True, date=self.END_DATE+timedelta(days=1)) #should not be counted with date filter
        db.activities.insert(person_id=CLIENT_3,type='Other', is_no_show=True, date=self.START_DATE-timedelta(days=1)) #should not be counted with date filter 
        
        #Volunteer and non-Fitting activity should not be in result
        db.activities.insert(person_id=CLIENT_1,type='NonFitting') #should not be in any results
        db.activities.insert(person_id=VOLUNTEER_1,type='Fitting', gender='Female', date=self.START_DATE+timedelta(days=1), start_time='09:00', end_time='12:30')
        db.activities.insert(person_id=VOLUNTEER_2,type='Fitting', gender='Male', date=self.START_DATE-timedelta(days=1), start_time='09:00', end_time='12:30')
        db.activities.insert(person_id=VOLUNTEER_2,type='NonFitting', gender='Both', date=self.END_DATE+timedelta(days=1), start_time='09:00', end_time='12:30')
        
        
        """ For Organisation """
        db.organisations.insert(name='XYZ', desc='Services', created_on=self.START_DATE)
        db.organisations.insert(name='XYZ', desc='Services', created_on=self.START_DATE, deactivated=True)
        db.organisations.insert(name='XYZ', desc='Services', created_on=self.START_DATE-timedelta(days=1))
        db.organisations.insert(name='XYZ', desc='Services', created_on=self.START_DATE+timedelta(days=1))
        
        db.organisations.insert(name='XYZ', desc='Services', created_on=self.END_DATE)
        db.organisations.insert(name='XYZ', desc='Services', created_on=self.END_DATE, deactivated=True)
        db.organisations.insert(name='XYZ', desc='Services', created_on=self.END_DATE-timedelta(days=1))
        db.organisations.insert(name='XYZ', desc='Services', created_on=self.END_DATE+timedelta(days=1))
        

class TestReportsControllerWithAuth(TestReportsControllerBase):
    
    def testIndex(self):
        self.setup_helper()
        resp = index()
        #check for no render failures
        self.html = render_helper(resp)
        self.assertInHtml('<h2>Reports</h2>')

            
    def testVolunteerActivities(self):
        self.setup_helper()
        self.setup_client_db()

        """no filters and no form post"""
        resp = all_volunteers_activities()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

       

        """all activities after start date filter"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, gender='All')
        resp = all_volunteers_activities()
        self.assertEquals(self.result_length(resp), 2)
        self.html = render_helper(resp)

        """all activities between dates"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR, gender='All')
        resp = all_volunteers_activities()
        self.assertEquals(self.result_length(resp), 1)
        self.html = render_helper(resp)

        """all activities Female"""
        request.vars = Storage(view='X', gender='Female')
        resp = all_volunteers_activities()
        self.assertEquals(self.result_length(resp), 2)
        self.html = render_helper(resp)

        """all activities Male"""
        request.vars = Storage(view='X', gender='Male')
        resp = all_volunteers_activities()
        self.assertEquals(self.result_length(resp), 2)
        self.html = render_helper(resp)
        
    def testEmployeeActivities(self):
        self.setup_helper()
        self.setup_client_db()

        """no filters and no form post"""
        resp = employee_activities()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

       

        """all activities after start date filter"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, gender='All')
        resp = employee_activities()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

        """all activities between dates"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR, gender='All')
        resp = employee_activities()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

        """all activities Female"""
        request.vars = Storage(view='X', gender='Female')
        resp = employee_activities()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

        """all activities Male"""
        request.vars = Storage(view='X', gender='Male')
        resp = employee_activities()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
    def testClientFittings(self):
                
        self.setup_helper()
        self.setup_client_db()
        
        """no filters and no form post"""
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """all fittings """
        request.vars = Storage(view='X', gender='All')
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 7)
        self.html = render_helper(resp)
        
        """all fittings after start date filter"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, gender='All')
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 5)
        self.html = render_helper(resp)
        
        """all fittings between dates"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR, gender='All')
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 4)
        self.html = render_helper(resp)
        
        """all fitting Female"""
        request.vars = Storage(view='X', gender='Female')
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 6)
        self.html = render_helper(resp)
        
        """all fitting Male"""
        request.vars = Storage(view='X', gender='Male')
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 1)
        self.html = render_helper(resp)
        
        """only first visits"""
        request.vars = Storage(view='X', gender='All')
        set_args([FITTING_REPORTS.FIRST_VISITS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 2)
        self.html = render_helper(resp)
        
        """only first visits between dates"""
        request.vars = Storage(view='X', gender='All', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR)
        set_args([FITTING_REPORTS.FIRST_VISITS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 1)
        self.html = render_helper(resp)
        
        """first visits Female"""
        request.vars = Storage(view='X', gender='Female')
        set_args([FITTING_REPORTS.FIRST_VISITS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 1)
        self.html = render_helper(resp)
        
        """first visits Male"""
        request.vars = Storage(view='X', gender='Male')
        set_args([FITTING_REPORTS.FIRST_VISITS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 1)
        self.html = render_helper(resp)
        
        """only return visits"""
        request.vars = Storage(view='X', gender='All')
        set_args([FITTING_REPORTS.RETURN_VISITS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 5)
        self.html = render_helper(resp)
        
        """only return visits between dates"""
        request.vars = Storage(view='X', gender='All', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR)
        set_args([FITTING_REPORTS.RETURN_VISITS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 3)
        self.html = render_helper(resp)
        
        """return visits female"""
        request.vars = Storage(view='X', gender='Female')
        set_args([FITTING_REPORTS.RETURN_VISITS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 5)
        self.html = render_helper(resp)
        
        """return visits male"""
        request.vars = Storage(view='X', gender='Male')
        set_args([FITTING_REPORTS.RETURN_VISITS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        
        """only no-shows"""
        request.vars = Storage(view='X', gender='All')
        set_args([FITTING_REPORTS.NO_SHOWS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 2)
        self.assertTrue(self.result(resp)[0].get('activity type') in ['Fitting', 'Other'])
        self.assertTrue(self.result(resp)[1].get('activity type') in ['Fitting', 'Other'])
        self.assertEquals(resp.get('total'), 5)
        self.html = render_helper(resp)
        
        """only no shows between the dates"""
        request.vars = Storage(view='X', gender='All', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR)
        set_args([FITTING_REPORTS.NO_SHOWS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 2)
        self.assertTrue(self.result(resp)[0].get('activity type') in ['Fitting', 'Other'])
        self.assertTrue(self.result(resp)[1].get('activity type') in ['Fitting', 'Other'])
        self.assertEquals(resp.get('total'), 3)
        self.html = render_helper(resp)
        
        """no-shows Female"""
        request.vars = Storage(view='X', gender='Female')
        set_args([FITTING_REPORTS.NO_SHOWS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 2)
        self.assertEquals(resp.get('total'), 4)
        self.html = render_helper(resp)
        
        """no-shows Male"""
        request.vars = Storage(view='X', gender='Male')
        set_args([FITTING_REPORTS.NO_SHOWS])
        resp = client_fittings()
        self.assertEquals(self.result_length(resp), 1)
        self.assertEquals(self.result(resp)[0].get('activity type'), 'Other')
        self.assertEquals(resp.get('total'), 1)
        self.html = render_helper(resp)
        
        
        """ all fittings download """
        request.vars = Storage(download='X', gender='All')
        set_args() #clear to get all
        resp = client_fittings()
        
        #check a couple lines
        #self.assertTrue('1999-12-30,1,6,1,FName1,LName1,1,,,,,' in resp)        
        #print resp
        #self.assertEquals(resp.replace('\r',''),self.ALL_FITTING_CSV)

    def testOrganisationsTotal(self):
        """
        For now, 'total' queries are based purely on an 'effective date' and the created_on datetime.
        A future release may track all deactivate and reactivate datetimes 
        to see if an entity was actually 'active' at any given time.
        """
        
        self.setup_helper()
        self.setup_client_db()
                
        """no filters and no form post"""
        resp = organisations_all()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """ no filters (all orgs) """
        request.vars = Storage(view='X')
        resp = organisations_all()
        self.assertEquals(self.result_length(resp), 6) #not deactivated for 'total'
        
        """all fittings after start date filter"""
        request.vars = Storage(view='X', effective_date=self.START_DATE_STR)
        resp = organisations_all()
        self.assertEquals(self.result_length(resp), 3)
        self.html = render_helper(resp)
        
        """all fittings between dates"""
        request.vars = Storage(view='X', effective_date=self.END_DATE_STR)
        resp = organisations_all()
        self.assertEquals(self.result_length(resp), 5)
        self.html = render_helper(resp)

    def testClientsTotal(self):
        """
        For now, 'total' queries are based purely on an 'effective date' and the created_on datetime.
        A future release may track all deactivate and reactivate datetimes 
        to see if an entity was actually 'active' at any given time.
        """
        
        self.setup_helper()
        self.setup_client_db()
                
        """no filters and no form post"""
        resp = total_clients()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """ no filters (all orgs) """
        request.vars = Storage(view='X')
        resp = total_clients()
        self.assertEquals(self.result_length(resp), 2) #not deactivated for 'total'
        
        """all fittings after start date filter"""
        request.vars = Storage(view='X', effective_date=self.START_DATE_STR)
        resp = total_clients()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """all fittings between dates"""
        request.vars = Storage(view='X', effective_date=self.END_DATE_STR)
        resp = total_clients()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

    def testEmployeesTotal(self):
        """
        For now, 'total' queries are based purely on an 'effective date' and the created_on datetime.
        A future release may track all deactivate and reactivate datetimes 
        to see if an entity was actually 'active' at any given time.
        """
        
        self.setup_helper()
        self.setup_client_db()
                
        """no filters and no form post"""
        resp = total_employees()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """ no filters (all orgs) """
        request.vars = Storage(view='X')
        resp = total_employees()
        self.assertEquals(self.result_length(resp), 1) #not deactivated for 'total'
        
        """all fittings after start date filter"""
        request.vars = Storage(view='X', effective_date=self.START_DATE_STR)
        resp = total_employees()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """all fittings between dates"""
        request.vars = Storage(view='X', effective_date=self.END_DATE_STR)
        resp = total_employees()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
    def testVolunteerTotal(self):
        """
        For now, 'total' queries are based purely on an 'effective date' and the created_on datetime.
        A future release may track all deactivate and reactivate datetimes 
        to see if an entity was actually 'active' at any given time.
        """
        
        self.setup_helper()
        self.setup_client_db()
                
        """no filters and no form post"""
        resp = all_volunteers()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """ no filters (all orgs) """
        request.vars = Storage(view='X')
        resp = all_volunteers()
        self.assertEquals(self.result_length(resp), 2) #not deactivated for 'total'
        
        """all fittings after start date filter"""
        request.vars = Storage(view='X', effective_date=self.START_DATE_STR)
        resp = all_volunteers()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """all fittings between dates"""
        request.vars = Storage(view='X', effective_date=self.END_DATE_STR)
        resp = all_volunteers()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
    def testAgencyUserTotal(self):
        """
        For now, 'total' queries are based purely on an 'effective date' and the created_on datetime.
        A future release may track all deactivate and reactivate datetimes 
        to see if an entity was actually 'active' at any given time.
        """
        
        self.setup_helper()
        self.setup_client_db()
                
        """no filters and no form post"""
        resp = all_agencies()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """ no filters (all orgs) """
        request.vars = Storage(view='X')
        resp = all_agencies()
        self.assertEquals(self.result_length(resp), 1) #not deactivated for 'total'
        
        """all fittings after start date filter"""
        request.vars = Storage(view='X', effective_date=self.START_DATE_STR)
        resp = all_agencies()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """all fittings between dates"""
        request.vars = Storage(view='X', effective_date=self.END_DATE_STR)
        resp = all_agencies()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
    
    def testEmployeesActive(self):
        
        self.setup_helper()
        self.setup_client_db()

        """no filters and no form post"""
        resp = active_employees()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

        """all fittings after start date filter"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR)
        resp = active_employees()
        self.assertEquals(self.result_length(resp), 1)
        self.html = render_helper(resp)
        
        """all fittings between dates"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR)
        resp = active_employees()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

    def testEmployeeHours(self):
        
        self.setup_helper()
        self.setup_client_db()

        """no filters and no form post"""
        resp = employee_hours()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

        """ all hours with no filters """
        request.vars = Storage(view='X', gender='All')
        resp = employee_hours()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), 0) #3 volunteer activities
        self.assertEquals(resp.get('time_count'), '0:00:00')
        
        """hours after start date filter"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, gender='All')
        resp = employee_hours()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), 0) #3 volunteer activities
        self.assertEquals(resp.get('time_count'), '0:00:00')
        
        """hours between dates"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR, gender='All')
        resp = employee_hours()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), 0) #3 volunteer activities
        self.assertEquals(resp.get('time_count'), '0:00:00')
        
        """ all Female hours with no date filters """
        request.vars = Storage(view='X', gender='Female')
        resp = employee_hours()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), 0) #1 Female + 1 Both
        self.assertEquals(resp.get('time_count'), '0:00:00')
        
        """ all Male hours with no date filters """
        request.vars = Storage(view='X', gender='Male')
        resp = employee_hours()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), 0) #1 Male + 1 Both
        self.assertEquals(resp.get('time_count'), '0:00:00')

    def testAgenciesTotal(self):
        """
        For now, 'total' queries are based purely on an 'effective date' and the created_on datetime.
        A future release may track all deactivate and reactivate datetimes 
        to see if an entity was actually 'active' at any given time.
        """
        
        self.setup_helper()
        self.setup_client_db()
                
        """no filters and no form post"""
        resp = total_employees()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """ no filters (all orgs) """
        request.vars = Storage(view='X')
        resp = all_agencies()
        self.assertEquals(self.result_length(resp), 1) #not deactivated for 'total'
        
        """all fittings after start date filter"""
        request.vars = Storage(view='X', effective_date=self.START_DATE_STR)
        resp = all_agencies()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """all fittings between dates"""
        request.vars = Storage(view='X', effective_date=self.END_DATE_STR)
        resp = all_agencies()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

    def testOrganisationsNew(self):
        
        self.setup_helper()
        self.setup_client_db()
        
        """no filters and no form post"""
        resp = organisations_new()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """ no filters (all orgs) """
        request.vars = Storage(view='X')
        resp = organisations_new()
        self.assertEquals(self.result_length(resp), 8) #even deactivated for 'new'
        
        """ new orgs after start date filter"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR)
        resp = organisations_new()
        self.assertEquals(self.result_length(resp), 7)
        self.html = render_helper(resp)
        
        """ new orgs before end date filter"""
        request.vars = Storage(view='X', end_date=self.END_DATE_STR)
        resp = organisations_new()
        self.assertEquals(self.result_length(resp), 7)
        self.html = render_helper(resp)
        
        """all fittings between dates"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR)
        resp = organisations_new()
        self.assertEquals(self.result_length(resp), 6)
        self.html = render_helper(resp)
            
    def testVolunteersActive(self):
        
        self.setup_helper()
        self.setup_client_db()

        """no filters and no form post"""
        resp = active_volunteers()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

        """all fittings after start date filter"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR)
        resp = active_volunteers()
        self.assertEquals(self.result_length(resp), 2)
        self.html = render_helper(resp)
        
        """all fittings between dates"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR)
        resp = active_volunteers()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

    def testVolunteeringHours(self):
        
        self.setup_helper()
        self.setup_client_db()

        """no filters and no form post"""
        resp = volunteer_hours()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)

        """ all hours with no filters """
        request.vars = Storage(view='X', gender='All')
        resp = volunteer_hours()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), 3) #3 volunteer activities
        self.assertEquals(resp.get('time_count'), '10:30:00')
        
        """hours after start date filter"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, gender='All')
        resp = volunteer_hours()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), 2) #3 volunteer activities
        self.assertEquals(resp.get('time_count'), '7:00:00')
        
        """hours between dates"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR, gender='All')
        resp = volunteer_hours()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), 1) #3 volunteer activities
        self.assertEquals(resp.get('time_count'), '3:30:00')
        
        """ all Female hours with no date filters """
        request.vars = Storage(view='X', gender='Female')
        resp = volunteer_hours()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), 2) #1 Female + 1 Both
        self.assertEquals(resp.get('time_count'), '7:00:00')
        
        """ all Male hours with no date filters """
        request.vars = Storage(view='X', gender='Male')
        resp = volunteer_hours()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), 2) #1 Male + 1 Both
        self.assertEquals(resp.get('time_count'), '7:00:00')
    
    
    def testItemsDistributed(self):
        
        self.setup_helper()
        self.setup_client_db()

        """no filters and no form post"""
        resp = items_distributed()
        self.assertEquals(self.result_length(resp), 0)
        self.html = render_helper(resp)
        
        """all fittings after start date filter"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, gender='All')
        resp = items_distributed()
        self.assertEquals(self.result_length(resp), len(ACTIVITIES_ITEMS_BOTH))
        self.html = render_helper(resp)
        
        """all fittings between dates"""
        request.vars = Storage(view='X', start_date=self.START_DATE_STR, end_date=self.END_DATE_STR, gender='All')
        resp = items_distributed()
        self.assertEquals(self.result_length(resp), len(ACTIVITIES_ITEMS_BOTH))
        self.html = render_helper(resp)
        
        """all items for Female """
        request.vars = Storage(view='X', gender='Female')
        resp = items_distributed()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), len(ACTIVITIES_ITEMS_FEMALE))
        for row in self.result(resp):
            if row['Item Type']=='Skirts':
                self.assertEquals(row['Count'], 6)
        
        
        """all items for Male """
        request.vars = Storage(view='X', gender='Male')
        resp = items_distributed()
        self.html = render_helper(resp)
        self.assertEquals(self.result_length(resp), len(ACTIVITIES_ITEMS_MALE))
        for row in self.result(resp):
            if row['Item Type']=='Golfshirts':
                self.assertEquals(row['Count'], 1)
        

class TestReportsControllerWithNoAuth(TestReportsControllerBase):
    
    def testExec(self):
        self.request = request
        self.assert_not_authorized(self.setup_helper) #fails on exec_file(.../reports.py)

class TestReportsControllerAsAdmin(TestReportsControllerWithAuth):
    
    def setUp(self):
        set_is_admin()

class TestReportsControllerAsClient(TestReportsControllerWithNoAuth):
    
    def setUp(self):
        set_is_client()
    
class TestReportsControllerAsEmployee(TestReportsControllerWithNoAuth):
    
    def setUp(self):
        set_is_employee()

class TestReportsControllerAsAgency(TestReportsControllerWithNoAuth):
    
    def setUp(self):
        set_is_agency()
    
class TestReportsControllerAsVolunteer(TestReportsControllerWithNoAuth):
    
    def setUp(self):
        set_is_volunteer()

def add_tests():
    suite.addTest(unittest.makeSuite(TestReportsControllerAsAdmin))
    suite.addTest(unittest.makeSuite(TestReportsControllerAsEmployee))
    suite.addTest(unittest.makeSuite(TestReportsControllerAsClient))
    suite.addTest(unittest.makeSuite(TestReportsControllerAsAgency))
    suite.addTest(unittest.makeSuite(TestReportsControllerAsVolunteer))
    
if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed from runner.py
    add_tests()
