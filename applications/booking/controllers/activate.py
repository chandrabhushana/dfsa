#Single controller to maintain all fake-deleting due to the manual referential integrity 
#Assumes if someone has access to deactivate an entity they also have access to 'deactivate' the dependancies 

#redefine since action and entity are reversed from their defaults
action=request.controller
entity=request.function
has_auth = can(action, entity)

@auth.requires(has_auth)
def clients():
    id = request.args(0) or request.vars.client
    __activate_person_and_dependancies(id, enable_login=False)
    redirect(URL(c=request.function, f='view',args=id))

@auth.requires(has_auth)
def employees():
    id = request.args(0) or request.vars.employee 
    __activate_person_and_dependancies(id, enable_login=True)
    redirect(URL(c=request.function, f='view',args=id))

@auth.requires(has_auth)
def volunteers():
    id = request.args(0) or request.vars.volunteer
    __activate_person_and_dependancies(id, enable_login=True)
    redirect(URL(c=request.function, f='view',args=id))

@auth.requires(has_auth)
def agencies():
    id = request.args(0) or request.vars.thirdparty
    __activate_person_and_dependancies(id, enable_login=True, activities=False)
    redirect(URL(c=request.function, f='view',args=id))

@auth.requires(has_auth)
def events():
    id = request.args(0) or request.vars.event
    __activate_event_and_dependancies(id)
    redirect(URL(c=request.function, f='index', vars=event_vars_wo_id()))

@auth.requires(has_auth)
def organisations():
    id = request.args(0) or request.vars.org
    db(db.organisations.id==id).update(deactivated=False)
    db.activation_dates.insert(record_type=request.function,record_id=id,de_activate=request.controller,date=request.now)
    ##Dont deactivate the people (clients, agencies, volunteers)
    redirect(URL(c=request.function, f='view',args=id))

def __activate_event_and_dependancies(id):
    db(db.events.id==id).update(deactivated=False)
    db(db.registrations.event==id).update(deactivated=False)

def __activate_person_and_dependancies(id, enable_login=False, activities=True):
    if enable_login:
        db(db.people.id==id).update(deactivated=False, registration_key='')
    else:
        db(db.people.id==id).update(deactivated=False)
    db.activation_dates.insert(record_type=request.function,record_id=id,de_activate=request.controller,date=request.now)
    if activities:
        db(db.activities.person_id==id).update(deactivated=False)
