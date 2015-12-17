### Registration Validations
#reg_person_type = PERSON_TYPE_EMPLOYEE if request.vars.employee else PERSON_TYPE_CLIENT
import logging
if request.vars.employee:
    reg_person_type = PERSON_TYPE_EMPLOYEE
elif request.vars.volunteer:
    reg_person_type = PERSON_TYPE_VOLUNTEER
else:
    reg_person_type = PERSON_TYPE_CLIENT
db.registrations.event.requires=IS_IN_DB(db,'events.id', '%(id)s - %(name)s')
#Rel-3 R3_13 for referral_contact_email & name added on Jan 28 by Mukesh
#db.registrations.person.requires=IS_IN_DB(list_people(reg_person_type, select=False), 'people.id', '%(first_name)s %(last_name)s (%(mobile)s)', zero=None)
db.registrations.person.requires=IS_IN_DB(list_people(reg_person_type, select=False), 'people.id', '%(first_name)s %(last_name)s (%(mobile)s %(contact_name)s) %(referral_contact_email)s', zero=None)


@auth.requires(has_auth)
def manage():
    """
    This function gets loaded by ajax into the event edit view.
    Both register and unregister are handled in the same function 
    since LOAD with ajax=True will trap any form submits.
    
    GAE Note: even if registrations are selected after a registration
    is added or deactivated, it may not be part of the set. 
    So the registered or unregister email is handled explicitly in the registration list.
    See http://code.google.com/appengine/articles/transaction_isolation.html   
    """
    global event_id
    event_id = request.vars.event
    if event_id==None:
        response.view = 'error.load'
        return T('No event id provided')
    
    __init_globals()
    
    if can('manage-others', entity):
        __manage_person()
    elif can('manage-self', entity):
        __manage_self(readonly=False)
    else:
        __manage_self(readonly=True)
    
    resp = dict(
        event_id = event_id,
        is_registered = is_registered,
        remaining_slots = slots_available,
        registrations = registrations,
        person = person,
        person_name = person_name,
        registration_message = registration_message,        
        form = form,
        slots_message = T('Client spots available: ') + str(slots_available),
        is_full=is_full,
        #event=event,
    )
    
    return resp

def __init_globals():
    global registrations, slots_available, register_action, unregister_action 
    global is_registered, can_manage_this_person, can_manage_all, form
    global registration_message
    global person, person_name, is_full, event
   # global displayname_array
    
    register_action = request.post_vars.register #hidden form field
    unregister_action = request.post_vars.unregister #hidden form field
    is_registered = can_manage_this_person = False
    can_manage_all = can('manage-all', entity)
    form = person = person_name = registration_message = None
    
    #avoid fetching event from db if slots and date are in query string
    if request.vars.slots:
        total_slots = request.vars.slots
    else:
        event = db.events(event_id)
        total_slots = event.slots        
    
    registrations = registrations_by_event(event_id)
    slots_available = int(total_slots)
    for reg in registrations.find(lambda row: row.type==PERSON_TYPE_CLIENT):
        slots_available -= 1
        db(db.events.id==event_id).update(remaining_slots=slots_available)
       # db.events.insert(remaining_slots=slots_available)
    #db.events.insert(remaining_slots=slots_available)
    is_full = slots_available<=0 
    #displayname_array = []
    displayname_list = ''
    
def __manage_person():
    """
    In the case of an admin, there are 2 different scenarios:
        1. email in the url query params - originated from the person page
            -build register button for for that user only
        2. no email in the url.
            -build register drop-down for all available emails
    
    In both admin scenarios, it will still build unregister form for 
    all registered users. The reason form button is used over a link 
    is that the form gets trapped by web2py_ajax automatically. 
    To use normal Delete links (although would look better) would 
    require writing the ajax functionality.
    """
    __retrieve_and_register_person()
    __unregister_person()
    __create_form_for_person()
    __set_registration_message()


def __set_registration_message():
    global registration_message
    if registration_message:
        return
    elif is_registered:
        #registrations.exclude(lambda row:row.person==long(person_id)) #always remove the current person to display on top
        registration_message = XML(person_name + T(' is <strong>registered</strong> for this event.'))
    else:
        registration_message = XML(person_name + T(' is <strong>not registered</strong> for this event.'))

def __create_form_for_person():
    if can_manage_this_person and person:
        global form
        event = db.events(event_id)
        today = request.now.date()
        
        if event.date < today:
            form = 'Cannot register or unregister for an event in the past.'
        elif is_registered:
            action = 'unregister'
            form = FORM(INPUT(_name=action, _value='X', _type='hidden'),
                        INPUT(_class='button register-button', _type='submit', _value=action[0].capitalize() + action[1:]),
                        str(person_name))
        elif (slots_available > 0 or person.type!=PERSON_TYPE_CLIENT):
            action = 'register'
            form = FORM(INPUT(_name=action, _value='X', _type='hidden'),
                        INPUT(_class='button register-button', _type='submit', _value=action[0].capitalize() + action[1:]),
                        str(person_name))
        else:
            form = 'There are no client spots available.'
        

def __unregister_person():
    global is_registered, slots_available, registration_message
    
    if not unregister_action or not person:
        return
    
    if not (can_manage_all or person.organisation==auth.user.organisation):
        registration_message = T('You do not have authorization to unregister this person.')
        return
    
    unregister_id = person.id
    unregister_name = display_name(person)    
    __unregister(unregister_id, unregister_name)
    unregistered_row = registrations.find(lambda row: row.person==unregister_id)
    for row in registrations.exclude(lambda row: row.person==unregister_id):
        if row.type==PERSON_TYPE_CLIENT:
            slots_available += 1
            
            db(db.events.id==event_id).update(remaining_slots=slots_available)
            #db.events.insert(remaining_slots=slots_availabel)
    #db.events.insert(remaining_slots=slots_availabel)
    
    # Updating the event display name based on Volunteer registered
    event=resource_by_id(db.events,event_id)
    event_type=resource_by_id(db.event_types,event.type)
    # Changes for Volunteer and Volunteer Roster event type
    if (person.type==PERSON_TYPE_VOLUNTEER and event_type.name=='Volunteer Roster'):
        name_orig = event.display_name
        name = '('+person.first_name+' '+person.last_name.split()[0][0]+') '
        final_name = name_orig.replace(name,'')
        db(db.events.id==event_id).update(display_name=final_name)
        
    # Changes for Client and event types other than Volunteer Roster
    if (person.type==PERSON_TYPE_CLIENT and event_type.name!='Volunteer Roster'):
        name_orig = event.display_name
        name = '('+person.first_name+' '+person.last_name.split()[0][0]+') '
        final_name = name_orig.replace(name,'')
        db(db.events.id==event_id).update(display_name=final_name)
        
    if unregister_id==person_id:
        is_registered = False

def __retrieve_and_register_person():
    global is_registered, person_id, person, person_name, can_manage_this_person, slots_available, registration_message
    
    person_id = request.vars.person #can only register the person from the query string
    if person_id==None or person_id=='None':
        person_id = person  = None
        registration_message = T('You must use the Client/Employee/Volunteer page for registration or un-registration.')
        return
    
    person_id = long(person_id)
    person = resource_by_id(db.people, person_id)
    if not person:
        registration_message = T('This person does not exist or has been deactivated.')
        return
    
    #If can't manage all (third party), limit to just the same org
    if not (can_manage_all or person.organisation==auth.user.organisation):
        registration_message = T('You do not have authorization to register this person.')
        person = None
        return
    
    can_manage_this_person = True
    person_name = display_name(person)
    
    if register_action:
        __register(person, person_name)
    else:
        is_registered = __is_person_registered(person_id, registrations)    
    

def __manage_self(readonly=False):
    """
    In the case of a non-admin user, it will build forms to let 
    them register/unregister themselves only.
    """
    global slots_available, is_registered, form, person, person_name, registration_message
    
    person = auth.user
    person_name = display_name(person)
    
    if readonly:
        is_registered = __is_person_registered(person.id, registrations)
    else:
        if register_action:
            __register(person, person_name)
        elif unregister_action:
            __unregister(person.id, person_name='You')
            if is_client:
                slots_available += 1
                db(db.events.id==event_id).update(remaining_slots=slots_available)
                
        else:
            is_registered = __is_person_registered(person.id, registrations)
    
    
    if is_registered:
        registration_message = XML(T('You are <strong>registered</strong> for this event.'))
    else:
        registration_message = XML(T('You are <strong>not registered</strong> for this event.'))
    
    if not readonly and (slots_available > 0 or is_registered or not is_client):
        action = 'unregister' if is_registered else 'register'
        form = FORM(INPUT(_name=action, _value='X', _type='hidden'), 
                    INPUT(_class='button register-button', _type='submit', _value=action))
    

def __register(person, person_name):
    global is_registered, slots_available, registration_message
    
    use_slots = True if person.type==PERSON_TYPE_CLIENT else False
    if use_slots and (slots_available<1):
        message = T('We\'re sorry, but there are no spots available.')
        is_registered = False
    elif (__is_person_registered(person.id, registrations)):
        message = person_name + T(' has already been registered for this event.')
        is_registered = True
    else:
        db.registrations.insert(event=event_id, person=person.id, type=person.type)
        
        # Updating the event display name based on Volunteer registered
        event=resource_by_id(db.events,event_id)
        event_type=resource_by_id(db.event_types,event.type)
        # Changes for Volunteer and Volunteer Roster event type
        if (person.type==PERSON_TYPE_VOLUNTEER and event_type.name=='Volunteer Roster'):
            name = event.display_name+' ('+person.first_name+' '+person.last_name.split()[0][0]+') '
            db(db.events.id==event_id).update(display_name=name)
            
        # Changes for Client and event types other than Volunteer Roster
        if (person.type==PERSON_TYPE_CLIENT and event_type.name!='Volunteer Roster'):
            name = event.display_name+' ('+person.first_name+' '+person.last_name.split()[0][0]+') '
            db(db.events.id==event_id).update(display_name=name)
            
        message = XML (person_name + T(' has been <strong>registered</strong> for this event.'))
        is_registered = True
        if use_slots:
            slots_available -= 1
            db(db.events.id==event_id).update(remaining_slots=slots_available)
            if slots_available <= 0:
                __set_full(True)
    events=resource_by_id(db.events,event_id)
    #Rel-3 R3_13 for referral_contact_email & name added on Jan 28 by Mukesh
    #Rel-2 R3_13 as per Dany mail referral_contact_email & name has been removed for Volunteer & EMployee
    person_detail = queryr(db.people, [db.people.type==PERSON_TYPE_ADMIN])
    client_detail = queryr(db.people, [db.people.id==person.id])
    for email in client_detail:
        client_email = email.email
        client_type = email.type
        logging.info('client_type==============')
        logging.info(client_type)
        for email in person_detail:
            person_email = email.email
        
            if client_type==PERSON_TYPE_CLIENT:
            #Rel-3 R3_13 for referral_contact_email & name added on Jan 28 by Mukesh
            #mail.send(to = person_email, subject = '%s %s %s (Contact Number: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
                mail.send(to = person_email, subject = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
            if client_type==PERSON_TYPE_EMPLOYEE or client_type==PERSON_TYPE_VOLUNTEER:
            #Rel-3 R3_13 for referral_contact_email & name added on Jan 28 by Mukesh
            #mail.send(to = person_email, subject = '%s %s %s (Contact Number: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
                mail.send(to = person_email, subject = '%s %s %s (Contact Number: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
                
    #ReqR3_14 for autogenerated mail to agency user on 30th Jan by Subhasmita
    #logging.info(person.referral_contact_email)
    #logging.info(db.people.referral_contact_email)
    #if person.referral_contact_email != '':
        #logging.info('person.referral_contact_email')
        #ogging.info(person.referral_contact_email)
        #logging.info('Sending mail to referral agency for registered')
        #mail.send(to = person.referral_contact_email, subject = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
        #logging.info('Sending mail to referral agency for registered after mail')
        
    #R3_9 for autogenerated mail to client user on Feb01 by Mukesh
    client_detail = queryr(db.people, [db.people.id==person.id])
    for email in client_detail:
        client_email = email.email
        client_type = email.type
        if client_type==PERSON_TYPE_CLIENT:
            logging.info('Sending mail to client')
            mail.send(to = client_email, subject = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
            logging.info('Sending mail to client after')
    registration_message = response.flash = message

def __unregister(person_id, person_name='person'):
    global registration_message
    
    filters = [db.registrations.event==event_id, db.registrations.person==person_id]
    set = queryr(db.registrations, filters, select=False, push_down_deactivated=False)
    set.delete()
    
    ###Slots available is calculated afterwards since while looping
    ###through the registrations in order to check the person type
    if is_full:
        client_slots_freed = len(registrations.find(lambda row: (row.person==person_id)&(row.type==PERSON_TYPE_CLIENT)))        
        if slots_available+client_slots_freed>0:
            __set_full(False)
    
    if person_name=='You':
        flash = XML(T('You have been <strong>un-registered</strong> for this event.'))
    else:
        flash = XML(person_name + T(' has been <strong>un-registered</strong> for this event.'))
    response.flash = flash
    events=resource_by_id(db.events,event_id)
     #Rel-3 R3_13 for referral_contact_email & name added on Jan 28 by Mukesh
    #Rel-2 R3_13 as per Dany mail referral_contact_email & name has been removed for Volunteer & EMployee
    person_detail = queryr(db.people, [db.people.type==PERSON_TYPE_ADMIN])
    client_detail = queryr(db.people, [db.people.id==person.id])
    for email in client_detail:
        client_email = email.email
        client_type = email.type
        logging.info('client_type==============')
        logging.info(client_type)
        for email in person_detail:
            person_email = email.email
            if client_type==PERSON_TYPE_CLIENT:
                #Rel-3 R3_13 for referral_contact_email & name added on Jan 28 by Mukesh
                #mail.send(to = person_email, subject = '%s %s %s (Contact Number: %s) has been unregistered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s) has been unregistered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
                mail.send(to = person_email, subject = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been unregistered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been unregistered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
            if client_type==PERSON_TYPE_EMPLOYEE or client_type==PERSON_TYPE_VOLUNTEER:
            #Rel-3 R3_13 for referral_contact_email & name added on Jan 28 by Mukesh
            #mail.send(to = person_email, subject = '%s %s %s (Contact Number: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s) has been registered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
                mail.send(to = person_email, subject = '%s %s %s (Contact Number: %s) has been unregistered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s) has been unregistered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
     #ReqR3_14 for autogenerated mail to agency user on 30th Jan by Subhasmita
     #if person.referral_contact_email != '':
        #logging.info('Sending mail to referral agency for unregistered')
        #mail.send(to = person.referral_contact_email, subject = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been unregistered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been unregistered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
        #logging.info('Sending mail to referral agency for unregistered after mail')
        #logging.info('person.referral_contact_email')
        
    #R3_9 for autogenerated mail to client user on Feb01 by Mukesh
    client_detail = queryr(db.people, [db.people.id==person.id])
    for email in client_detail:
        client_email = email.email
        client_type = email.type
        if client_type==PERSON_TYPE_CLIENT:
            mail.send(to = client_email, subject = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been unregistered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s, Agent Name: %s, Agent Email: %s) has been unregistered for event \'%s\' %s - %s, %s'%(person.type,person.first_name,person.last_name,person.mobile,person.contact_name,person.referral_contact_email,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
    registration_message = flash        

def __set_full(local_is_full):
    global is_full
    is_full = local_is_full
    db(db.events.id==event_id).update(is_full=is_full)
    
def __is_person_registered(person_id, registrations):
    rec = registrations.find(lambda row: row.person==person_id)
    return True if rec else False
