#Single controller to maintain all fake-deleting due to the manual referential integrity 
#Assumes if someone has access to deactivate an entity they also have access to 'deactivate' the dependancies 

#redefine since action and entity are reversed from their defaults
action=request.controller
entity=request.function
has_auth = can(action, entity)
import logging
@auth.requires(has_auth)
def clients():
    id = request.args(0) or request.vars.client
    __deactivate_person_and_dependancies(id, recalc_is_full=True, registrations=True)
    redirect(URL(c=request.function, f='view',args=id))

@auth.requires(has_auth)
def employees():
    id = request.args(0) or request.vars.employee 
    __deactivate_person_and_dependancies(id, recalc_is_full=False, registrations=True)
    redirect(URL(c=request.function, f='view',args=id))

@auth.requires(has_auth)
def volunteers():
    id = request.args(0) or request.vars.volunteer
    __deactivate_person_and_dependancies(id, recalc_is_full=False, registrations=True)
    redirect(URL(c=request.function, f='view',args=id))

@auth.requires(has_auth)
def agencies():
    id = request.args(0) or request.vars.thirdparty
    __deactivate_person_and_dependancies(id, recalc_is_full=False, registrations=False)
    redirect(URL(c=request.function, f='view',args=id))

@auth.requires(has_auth)
def events():
    id = request.args(0) or request.vars.event
    __deactivate_event_and_dependancies(id)
    db.activation_dates.insert(record_type=request.function,record_id=id,de_activate=request.controller,date=request.now)
    redirect(URL(c=request.function, f='index', vars=event_vars_wo_id()))

@auth.requires(has_auth)
def organisations():
    id = request.args(0) or request.vars.org
    db(db.organisations.id==id).update(deactivated=True)
    db.activation_dates.insert(record_type=request.function,record_id=id,de_activate=request.controller,date=request.now)
    ##Dont deactivate the people (clients, agencies, volunteers)
    redirect(URL(c=request.function, f='view',args=id))

##Handle deleting the event and all dependancies
def __deactivate_event_and_dependancies(id):
    db(db.events.id==id).update(deactivated=True)
    db(db.registrations.event==id).update(deactivated=True)

def __deactivate_person_and_dependancies(id, recalc_is_full=False, registrations=True):
    db(db.people.id==id).update(deactivated=True, registration_key='disabled')
    db.activation_dates.insert(record_type=request.function,record_id=id,de_activate=request.controller,date=request.now)
    person = db(db.people.id==id).select().first()
    
    if registrations:
        # Updating the display_name
        for reg in db(db.registrations.person==id).select():
            event = db(db.events.id==reg.event).select().first()
            name_orig = event.display_name
            name = '('+person.first_name+' '+person.last_name.split()[0][0]+') '
            final_name = name_orig.replace(name,'')
            db(db.events.id==reg.event).update(display_name=final_name)
        
        if recalc_is_full:
            for reg in db(db.registrations.person==id).select():
                reg.update_record(deactivated=True)
                event = db(db.events.id==reg.event).select().first()
                if event.is_full:
                    event.update_record(is_full=False)
        else:
            db(db.registrations.person==id).update(deactivated=True)
