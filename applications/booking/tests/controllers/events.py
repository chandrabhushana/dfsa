"""
This file is loaded automatically by tests/controllers/runner.py
To execute manually:
>   python web2py.py -S booking -M -R applications/booking/tests/controllers/events.py
"""
from applications.booking.tests.base import TestBase

class TestEventsControllerBase(TestBase):
    
    def setup_db(self):
        db(db.events.id>0).delete()  # Clear the database
        db(db.event_types.id>0).delete()
        db.event_types.insert(id=1,name='Fitting')
        db.event_types.insert(id=2,name='Mentoring')
        db.events.insert(id=1,type=1,name='Fitting 1', slots=1, is_full=True, date=date.today(), start_time='09:00', end_time='20:00', remaining_slots=1)
        db.events.insert(id=2,type=1,name='Fitting 2', date=date(1999, 01, 01), start_time='09:00', end_time='20:00', remaining_slots=1)
        db.events.insert(id=3,type=1,name='Fitting 1', date=date.today(), start_time='09:00', end_time='20:00', deactivated=True)
        db.events.insert(id=4,type=2,name='Mentoring 1', date=date.today(), start_time='09:00', end_time='20:00', remaining_slots=1)
        db.events.insert(id=5,type=2,name='Mentoring 2', date=date(1999, 01, 01), start_time='09:00', end_time='20:00', remaining_slots=1)
        db.events.insert(id=6,type=2,name='Mentoring 2', date=date(1999, 01, 01), start_time='09:00', end_time='20:00', deactivated=True)
    
    def setup_helper(self, function, resetdb=True,e='html'):
        """helper method for setup before each test"""
        setup_function(self,'events',function,e=e)
        if resetdb:
            self.setup_db()
    
    def create_helper(self, preset_type=False, ajax=False):
        """helper method for create functionality"""
        
        method=create
        if preset_type:
            request.vars = request.get_vars = Storage(type='Fitting')
        
        resp = create()
        form = resp.get('form')
        self.html = render_helper(resp)
        self.assertInHtml('<h2>Create Event</h2>')
        
        if not preset_type:
            self.assertEquals(type(form.custom.widget.type), gluon.html.SELECT)
        else:
            self.assertEquals(type(form.custom.widget.type), int)
            self.assertEquals(form.custom.widget.type, 1) #Assume the event being updated is Fitting
        
        #Post an invalid form
        request.vars = request.post_vars = Storage(_formname=form.formname, _formkey=form.formkey)
        form = create().get('form')
        self.assertTrue(form.errors)
        
        
        #Get a new form in case to handle preset type
        if preset_type:
            request.vars = request.get_vars = Storage(type='Fitting')
            form = create().get('form')
            request.post_vars = Storage(name='Fitting 3', date='01-01-2001', 
                                        start_time='09:00', end_time='12:00', slots='5',
                                        _formname=form.formname, _formkey=form.formkey)
            
        else:
            request.vars = request.get_vars = Storage()
            form = create().get('form')        
            request.post_vars = Storage(type='1', name='Fitting 3', date='01-01-2001', 
                                        start_time='09:00', end_time='12:00', slots='5',
                                        _formname=form.formname, _formkey=form.formkey)
        
        
        #post the valid form
        request.ajax=ajax
        if ajax:
            form = method().get('form')
            self.assertEquals(str(response.flash), 'Event created successfully')
            self.assertTrue('onEventCreated' in response.js)
        else:
            self.assert_redirect(method, '/events')
            self.assertEquals(str(session.flash), 'Event created successfully')
    
    
    def update_helper(self, ajax=False, person=False):
        """helper method for update functionality"""
        
        if person:
            request.vars = Storage(person='1')
        
        resp = update() #get the form
        form = resp.get('form')
        self.html = render_helper(resp)
        self.assertInHtml('<h2>Edit Event</h2><br/>')
        
        #make sure type is readonly
        self.assertEquals(type(form.custom.widget.type), str)
        self.assertEquals(form.custom.widget.type, 'Fitting') #Assume the event being updated is Fitting
        
        if person:
            self.assertEquals(resp.get('readonly'), True)
            return
        
        self.assertEquals(resp.get('readonly'), False)    
        
        #Post an invalid form
        request.vars = request.post_vars = Storage(_formname=form.formname, _formkey=form.formkey)
        resp = update()
        form = resp.get('form')
        self.assertTrue(form.errors)
        
        #build valid vars with the new formkey.
        ##Note, the slots are being changed in order to test the is_full change
        request.vars = request.post_vars = Storage(name='Fitting 3', date='01-01-2001', 
                               start_time='09:00', end_time='12:00', slots='5',
                               _formname=form.formname, _formkey=form.formkey)
        
        #post the valid form
        request.ajax=ajax
        if ajax:
            resp = update()
            self.assertEquals(str(response.flash), 'Event successfully updated')
            #check that slots and is_full changed
            self.assertEquals(resp.get('slots'), 5)
        else:
            self.assert_redirect(update, c='events')
            self.assertEquals(str(session.flash), 'Event successfully updated')
        
        self.assertEquals(resource_field_by_id(db.events, 'is_full', 1), False) #is_full goes back to False


class TestEventsControllerWithFullAuth(TestEventsControllerBase):
    """to be subclassed by role specific test class. not to be run directly"""
    
    def testIndex(self):
        self.setup_helper(function='index')
        resp = index()
        self.assertEquals(len(resp['types']), 2)
        self.html = render_helper(resp)
        #print self.html
        self.assertInHtml('<div id="event_event_types">')
        self.assertInHtml('<div id="event_types_legend">')
        self.assertInHtml('<li class="clickable" style="background-color:None; color:white">Fitting</li>')
        self.assertInHtml('<div id="calendar"></div>')
        self.assertInHtml('<div id="single_event">')
        self.assertInHtml('<div id="current_event_content">Select an Event</div>')
        self.assertInHtml('<div id="new_event_content"/>')
    
    
    def testIndexWithNoEventTypes(self):
        self.setup_helper(function='index', resetdb=False)
        db(db.event_types.id>0).delete()
        
        #handle different redirects by role in case of no event types
        if is_admin:
            self.assert_redirect(index, c='event_types')
            self.assertEquals(session.flash['error'], 'There are no event types created yet.')
        else:
            self.assert_redirect(index, c='')
            self.assertEquals(session.flash['error'], 'There are no event types created yet.')
    
    """
    The following test all the input variations using type, start and end
    Start and End are in seconds from 1970-01-01  
    """
    
    def testList1PrepDB(self):
        self.setup_helper(function='list', resetdb=True, e='json')
    
    def testListWithNoVarsAndSomeEvents(self):
        #self.setup_helper(function='list')
        request.vars = request.get_vars = Storage()
        resp = list()
        self.assertEquals(len(resp[entity]), 4, 'There should be 4 events')
        json = render_helper(resp) #actually json
        json = json.replace('\r\n','').replace(' ','')
        #print json
        str_today = str(date.today())
        expected = '[{"i":"0","id":"1","title":"Fitting1","start":"%sT09:00","end":"%sT20:00","type":"Fitting","description":"","slots":"1","remaining_slots":"1","color":"","textColor":"black","className":"event_type_Fitting","is_full":"True","is_registered":"False"},' % (str_today,str_today)
        self.assertTrue(expected in json)
    
    def testListWithTypeFilterAndSomeEvents(self):
        #self.setup_helper(function='list')
        request.vars = request.get_vars = Storage(type='Fitting')
        resp = list()
        length = len(resp['events'])
        self.assertEquals(length, 2, 'There should only be 2 Fitting events, not %i' % length)
    
    def testListWithTypeFilterAndNoResults(self):
        #self.setup_helper(function='list')
        request.vars = request.get_vars = Storage(type='XYZ')
        resp = list()
        self.assertEquals(len(resp['events']), 0)
    
    def testListWithInvalidStartTimeAndNoType(self):
        #self.setup_helper(function='list')
        request.vars = request.get_vars = Storage(start='XYZ')
        resp = list()
        self.assertEquals(len(resp['events']), 4)
    
    def testListWithWValidStartAndEndRageAndNoType(self):
        #Times are in seconds since 1970-01-01
        #self.setup_helper(function='list')
        request.vars = Storage(start='1293840000', end='2524608000') #2011-01-01 to 2050-01-01
        resp = list()
        self.assertEquals(len(resp['events']), 2)
    
    def testListWithWValidStartAndEndRageAndType(self):
        #Times are in seconds since 1970-01-01
        #self.setup_helper(function='list')
        request.vars = request.get_vars = Storage(type='Fitting', start='1293840000', end='2524608000') #2011-01-01 to 2050-01-01
        resp = list()
        self.assertEquals(len(resp['events']), 1)
    
    def testListZWithNoVarsAndNoEvents(self):
        #This 'list' once gets run last since it deletes from from the DB.
        #self.setup_helper(function='list', resetdb=False)
        db(db.events.id>0).delete()
        cache.ram.clear()
        resp = list()
        self.assertEquals(len(resp['events']), 0, 'There should be 0 events')
    
    
    """
    The create variants include ajax or not, and whether the type is selected from the drop down already.
    If the type is selected from the index drop down and passed to create, it should be default in the controller and be readonly.
    """
    
    def testCreate(self):
        self.setup_helper(function='create', resetdb=True) #make sure the event type is there to avoid issues
        self.create_helper()
    
    def testCreateAjax(self):
        self.setup_helper(function='create', resetdb=False)
        self.create_helper(ajax=True)
    
    def testCreatePresetType(self):
        self.setup_helper(function='create', resetdb=False)
        self.create_helper(preset_type=True)
    
    def testCreatePresetTypeAndAjax(self):
        self.setup_helper(function='create', resetdb=False)
        self.create_helper(preset_type=True, ajax=True)
    
    """
    Update variations are: ajax or not, and whether the function is accessed from the client page. 
    If accessed from the client page, it should return a readonly form and the readonly flag.
    In all update cases, the event type field is readonly. 
    """
    
    def testUpdate(self):
        #this one needs to run first to setup the DB
        self.setup_helper(function='update', resetdb=True)
        set_args([1]) #uses event=1
        self.update_helper(ajax=False)
    
    def testUpdateAjax(self):
        self.setup_helper(function='update', resetdb=False)
        set_args([1]) #uses event=1
        self.update_helper(ajax=True)
    
    def testUpdateWithPersonInVars(self):
        self.setup_helper(function='update', resetdb=False)
        set_args([1]) #uses event=1
        self.update_helper(ajax=True, person=True)
    
    def testUpdateWithInvalidEvent(self):
        #Not expecting a redirect due to the ajax support. Form should be None
        self.setup_helper(function='update', resetdb=False)
        set_args([9999999]) #uses event=9999999
        resp = update()
        self.assertEquals(resp.get('form'), None)
        self.assertTrue('event' not in resp)
        
    def testUpdateWithDeletedEvent(self):
        #Not expecting a redirect due to the ajax support. Form should be None
        self.setup_helper(function='update', resetdb=False)
        set_args([3]) #uses event=3
        resp = update()
        self.assertEquals(resp.get('form'), None)
        self.assertTrue('event' not in resp)
    

class TestEventsControllerWithReadonlyAuth(TestEventsControllerBase):
    """to be subclassed by role specific test class. not to be run directly"""
    
    """
    can see all event types from the drop down
    """
    def testIndex(self):
        self.setup_helper(function='index')
        resp = index()
        self.assertEquals(len(resp['types']), 2)
    
    """
    different redirect in case of no event types since they can't create event types 
    """
    def testIndexWithNoEventTypes(self):
        self.setup_helper(function='index', resetdb=False)
        db(db.event_types.id>0).delete()
        self.assert_redirect(index, c='')
        self.assertEquals(session.flash['error'], 'There are no event types created yet.')
    
    """
    Only 1 simple listing test for the auth. The auth does not change based on input vars.
    """
    def testList(self):
        self.setup_helper(function='list')
        resp = list()
        self.assertEquals(len(resp['events']), 4, 'There should be 4 events')
    
    """
    Only 1 simple create test for the auth
    """
    def testCreate(self):
        self.setup_helper(function='create', resetdb=False)
        self.assert_not_authorized(create)
    
    """
    should be able to access the update function, but only get a readonly form back
    """
    def testUpdate(self):
        self.setup_helper(function='update')
        set_args([1]) #uses event=1
        resp = update()
        self.assertEquals(resp['readonly'], True)



class TestEventsControllerAsAdmin(TestEventsControllerWithFullAuth):
        
    def setUp(self):
        set_is_admin()

class TestEventsControllerAsEmployee(TestEventsControllerWithFullAuth):
        
    def setUp(self):
        set_is_employee()

class TestEventsControllerAsAgency(TestEventsControllerWithReadonlyAuth):
    
    def setUp(self):
        set_is_agency()

class TestEventsControllerAsVolunteer(TestEventsControllerWithReadonlyAuth):
    
    def setUp(self):
        set_is_volunteer()        

class TestEventsControllerAsClient(TestEventsControllerWithReadonlyAuth):
    
    def setUp(self):
        set_is_client()


def add_tests():
    suite.addTest(unittest.makeSuite(TestEventsControllerAsAdmin))
    suite.addTest(unittest.makeSuite(TestEventsControllerAsAgency))
    suite.addTest(unittest.makeSuite(TestEventsControllerAsClient))
    suite.addTest(unittest.makeSuite(TestEventsControllerAsEmployee))
    suite.addTest(unittest.makeSuite(TestEventsControllerAsVolunteer))
    

if 'suite' not in globals():
    execfile('applications/%(application)s/tests/test_utils.py' % request, globals())
    setup_env()
    add_tests()
    run_tests()
else:
    #executed from runner.py
    add_tests()
