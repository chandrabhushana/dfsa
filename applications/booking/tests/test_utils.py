import traceback, sys, gluon, re, os
import unittest
import random
from gluon.globals import Request
from gluon.storage import Storage, List
from datetime import date, time, datetime, timedelta

from applications.booking.tests.render import *

def setup_env(testdb=True):
    global appname, approot, db, test_db, backup_db, suite
    
    suite = unittest.TestSuite()
    appname = request.application
    approot = 'applications/' + appname
    
    if testdb:
        from copy import copy
        test_db = DAL('sqlite://testing.sqlite')  # Name and location of the test DB file
        for tablename in db.tables:  # Copy tables!
            table_copy = [copy(f) for f in db[tablename]]
            test_db.define_table(tablename, *table_copy)
        
        backup_db = db
        db = test_db
        
        #Copy validations to fake_db
        db.people = db.auth_user
        execfile(approot + '/models/db_utils.py', globals())
        execfile(approot + '/models/validations.py', globals())

def render_helper(d):
    if not response.view:
        response.view = '%(controller)s/%(function)s.%(extension)s' % request
    return render(response, d)

def setup_function(self,c,f,e='html',user_id=1,user_type='',user_org=1,clear_cache=True):
    auth.is_logged_in = lambda: True
    self.request=request
    response.view = None
    request.vars = request.post_vars = request.get_vars = Storage()
    request.args = List()
    request.controller = c
    request.function = f
    request.extension = e
    request.ajax = False
    setup_view_env()
    exec_permissions()
    exec_controller()
    auth.user = gluon.storage.Storage(id=user_id,type=user_type,organisation=user_org,first_name='First',last_name='Last')
    if clear_cache:
        cache.ram.clear()

def setup_view_env():
    response._view_environment['auth'] = auth
    response._view_environment['db'] = db
    response._view_environment['is_admin'] = is_admin
    response._view_environment['is_agency'] = is_agency
    response._view_environment['is_employee'] = is_employee
    response._view_environment['is_client'] = is_client
    response._view_environment['is_volunteer'] = is_volunteer
    response._vars = Storage()
    execfile('applications/%s/modules/wfs_utils.py' % appname, response._view_environment)
    execfile('applications/%s/models/db_utils.py' % appname, response._view_environment)
    execfile('applications/%s/models/roles_perms.py' % appname, response._view_environment)
    execfile('applications/%s/models/utils.py' % appname, response._view_environment)

def run_tests():
    unittest.TextTestRunner(verbosity=2).run(suite)

def set_args(args=[1]):
    if type(args)==int:
        args=[args]
    request.args = List()
    for arg in args:
        request.args.append(arg)

def exec_permissions():
    execfile('applications/%s/models/roles_perms.py' % appname, globals()) #sets has_auth

def exec_controller():
    execfile('applications/%(application)s/controllers/%(controller)s.py' % request, globals()) #re-exec after has_auth is set

def set_is_all_false():
    global is_admin, is_employee, is_agency, is_client, is_volunteer
    is_admin = is_employee = is_agency = is_client = is_volunteer = False

def set_is_admin():
    global is_admin
    set_is_all_false()
    is_admin = True    
    
def set_is_employee():
    set_is_all_false()
    global is_employee
    is_employee = True

def set_is_client():
    set_is_all_false()
    global is_client
    is_client = True

def set_is_agency():
    set_is_all_false()
    global is_agency
    is_agency = True

def set_is_volunteer():
    set_is_all_false()
    global is_volunteer
    is_volunteer = True

    
""" 
" Twill helpers currently not in use

from twill.commands import go, follow, fv, submit, show
import twill

def twill_login(email, password):
    from twill.commands import showforms
    x = go(base_url)
    #showforms()
    if 'user/login' not in x:
        follow('Logout')
    fv('1', 'email', email)
    fv('1', 'password', password)
    submit('Login')
    find('<li><h4><a href="/user/logout">Logout</a></h4></li>')

def twill_register_and_login(first_name, last_name, email, password, person_type):
    register(first_name, last_name, email, password, person_type)
    twill_login(email, password)

def parse_url_for_id():
    #format: <PatchedMechanizeBrowser visiting http://localhost:8001/appname/clients/view/20>
    b = str(twill.get_browser()._browser)
    ind = b.rfind('/')
    return b[ind+1:-1]

def empty_user_db(self):
    db(db.auth_user.id>0).delete()
    db.commit()

def register(first_name, last_name, email, password, person_type):
    rows=db(db.auth_user.email==email).select()
    if len(rows)==0:
        auth.settings.registration_requires_verification = False
        auth.settings.registration_requires_approval = False
        if 'register' in auth.settings.actions_disabled:
            auth.settings.actions_disabled.remove('register')
        
        #db.auth_user.type.writable=db.auth_user.type.readable = True
        db.auth_user.type.default = person_type
        
        _set_args(['register'])
        form = None
        try:
            form = auth() #expect a redirect here when web2py adds ?_next=..... to url
        except gluon.http.HTTP, e:
            #print e.headers['Location']
            pass
                
        request.vars = request.post_vars = Storage(
            first_name=first_name, last_name=last_name, email=email, mobile=str(random.randint(1000000000, 9999999999)), type=person_type,
            password=password, password_two=password, _formname=form.formname, _formkey=form.formkey)
        
        try:
            form=auth() #expect a redirect here when web2py goes to the _next url
        except gluon.http.HTTP, e:
            pass
            #print e.headers['Location']
        else:
            print form.errors
        
        db.commit()

"""

"""

Other unused code

def show_feedback():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print '-'*60
    for line in traceback.format_exception(exc_type, exc_value,exc_traceback):
        print line[:-1]
    print '-'*60

def custom_execfile(test_file):
    #g
    try:
        sys.path.append(os.path.split(test_file)[0]) # to support imports form current folder in the testfiles
        execfile(test_file, globals()) 
    except (WindowsError,ValueError,SystemExit):
        pass # we know about the rotating logger error and SystemExit is not useful to detect
    except:
        show_feedback()
    #return g

"""