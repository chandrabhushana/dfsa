### Event Validations
db.events.slots.requires = IS_INT_IN_RANGE(0, 100)
db.events.type.requires = IS_IN_DB(queryr(db.event_types, select=False), 'event_types.id', 'event_types.name', zero=None)
db.events.start_time.requires = IS_IN_SET(create_time_list(9, 23), zero=None)
db.events.end_time.requires = IS_IN_SET(create_time_list(9, 23), zero=None)
db.events.date.requires = IS_DATE(format=T('%d-%m-%Y'))

import logging
@auth.requires(has_auth)
def index():

    if (auth.user.type==PERSON_TYPE_CLIENT or request.vars.person_type==PERSON_TYPE_CLIENT):
        types = queryr(db.event_types,[db.event_types.name!='Volunteer Roster']) 
    else:
        types = queryr(db.event_types) #for the dropdown
    if (len(types)==0):
        error = T('There are no event types created yet.')
        session.flash = dict(error=error)
        if request.ajax:
            response.view = 'error.load'
            return dict(error=error)
        elif can('create','event_types'):
            redirect(URL(c='event_types', f='index'))
        else:
            redirect(URL(c='default', f='index'))
    
    return dict(types=types)

@auth.requires(has_auth)
def list():
    if request.vars.person:
        person_registrations = registrations_by_person(long(request.vars.person))
    else:
        person_registrations = None
    if request.vars.person != None:    
        associataedPeople= db(db.people.id==long(request.vars.person)).select()
        for row in associataedPeople:
            requestorType = row.type
    else:
        requestorType = "None"

    if (auth.user.type==PERSON_TYPE_CLIENT or requestorType ==PERSON_TYPE_CLIENT):
        event_types = db(db.event_types.name!='Volunteer Roster').select()
    else:
        event_types = db(db.event_types.id>0).select()
            
    return dict(events=events_from_vars(request.vars), event_types=event_types, event_color=event_color, person_registrations=person_registrations)

@auth.requires(can('view',entity)) #intentionally skipping has_auth here to return read-only form
def update():
    """
    Only requires auth.is_logged_in() as it shows a read-only view to non admin users
    """
    event_id = request.vars.event or request.args(0)
    event = db.events(event_id)
    
    #Don't redirect in case of invalid or deactivated event due to the ajax. 
    #The view should have a message if form=None 
    if not event or event.deactivated:
        return dict(form=None,event_id=event_id)
    
    resp = dict()
    readonly = (not has_auth) or bool(request.vars.person) #Readonly if accessed from a person page
    db.events.type.writable=False
    slots = event.slots
    display_name=event.display_name
    
    form = SQLFORM(db.events, event,
                   readonly=readonly,
                   submit_button='Update Event',
                   _action=URL(c=entity,f='update', extension=request.extension, vars=event_vars()))
    
    if form.accepts(request.post_vars,session, onvalidation=event_form_processing):
        #if the number of slots changes, need to return the new val to the view and also need to recalc is_full
        if slots!=request.post_vars.slots:
            slots = long(request.post_vars.slots)
            reg_count = len(registrations_by_event(event.id).find(lambda row: row.type==PERSON_TYPE_CLIENT))
            events = db(db.events.id==event_id).update(remaining_slots=(slots-reg_count))
            is_full = (slots-reg_count)<=0
            if is_full!=event.is_full:
                db(db.events.id==event.id).update(is_full=is_full)
        
        events = db(db.events.id==event_id).update(display_name=display_name)
          
        flash = T('Event successfully updated')
        if request.ajax:
            response.flash = flash
        else:
            session.flash = flash
            redirect(URL(c=entity,f='index'))
    
    elif form.errors:
        response.flash = T('Event details are invalid')
    
    form.custom.widget.type = resource_field_by_id(db.event_types, 'name', event.type)
    return dict(form=form,event_id=event_id,slots=slots,readonly=readonly)


@auth.requires(has_auth)
def create():
    type = request.get_vars.type
    if type:
        type_id = db(db.event_types.name==type).select().first().id
        db.events.type.default=type_id
        db.events.type.writable=False
    else:
        db.events.type.writable=True
    
    form = SQLFORM(db.events)
    
    if form.accepts(request.post_vars, session, onvalidation=event_form_processing):
        event_id = str(form.vars.id)
        # Updating display name of the event
       # name_event = request.post_vars.name
      #  events = db(db.events.id==event_id).update(display_name=name_event)
        
        flash = T('Event created successfully')
        if request.ajax==True:
            response.flash = flash
            response.js = 'onEventCreated("' + event_id + '")'
        else:
            session.flash = flash
            redirect(URL(c=entity,f='index'))
        
    elif form.errors:
        response.flash = T("Event details are invalid")
    
    return dict(form=form, readonly=request.vars.person)


#####Utility Methods
if action=='list':
    def events_from_vars(request_vars):
        try:
            from datetime import datetime, timedelta
            CAL_START_DTTM = datetime(1970, 1, 1, 0, 0, 0)
            start_time = CAL_START_DTTM + timedelta(seconds=int(request_vars.start))
            end_time = CAL_START_DTTM + timedelta(seconds=int(request_vars.end))
        except :
            start_time = end_time = None
        
        cur_type = request_vars.type
        if cur_type:
            types = queryr(db.event_types)
            cur_type_rows = types.find(lambda row: row.name==cur_type)
            #cur_type_rows = db(db.event_types.name==cur_type).select()
            if len(cur_type_rows)==0:
                return cur_type_rows #return empty set immediately if invalid type 
            filters = [db.events.type==cur_type_rows.first().id]
        else:
            filters = []
        
        
        if start_time:
            filters.append( db.events.date >= start_time.date() )
        rows = queryr(db.events, filters)
        
        #need to do the end_time filter in memory since GQL can only have 1 equality operator
        if end_time:
            rows.find(lambda row: row.date <= end_time.date())
        
        if request.vars.person != None:    
            associataedPeople= db(db.people.id==long(request.vars.person)).select()
            for row in associataedPeople:
                requestorType = row.type
        else:
            requestorType = "None"        
        outcome =[]
        if (auth.user.type==PERSON_TYPE_CLIENT or requestorType ==PERSON_TYPE_CLIENT):
            result = db(db.event_types.name=='Volunteer Roster').select().first()
            for row in rows:
                if row.type != result.id:
                    outcome.append(row)
        else:
            outcome=rows
        return outcome


if action in ['update', 'view']:
    def get_event_or_redirect(event_id):
        event = db.events(event_id)
        if not event:
            error = T('Event %(event_id)s does not exist' % locals())
            if request.ajax:
                resp['error'] = error
                response.view = 'error.load'
            else:
                session.flash = error
                redirect(URL(c=entity,f='index'))
        else:
            return event


#Custom validator run after event validation, but before event db insert
def event_form_processing(form):
    #pass
    import time
    end_time = time.strptime(form.vars.end_time, "%H:%M")
    start_time =  time.strptime(form.vars.start_time, "%H:%M")
    date = form.vars.date
    if end_time <= start_time:
        form.errors.end_time = 'End time must be after start time'
    
    if date < date.today():
        form.errors.date = 'Date cannot be less than Current Date'
        
    if not form.vars.remaining_slots:
        slots = form.vars.slots
        form.vars.remaining_slots = slots

def event_color(event, event_types):
    from datetime import date
    
    event_type = event_types.find(lambda row: event.type==row.id).first()
    event_type_name = event_type.name
    
    if event.date < date.today():
        color = 'grey'
        textcolor = 'white'
    #elif event.slots <= count_registrations_by_event(event.id, type=PERSON_TYPE_CLIENT):
    #elif event.is_full:
    #    color = 'grey'
    #    textcolor = 'black'
    else:
        event_type_color = event_type.color
        textcolor = 'black'
        color = event_type_color or ''
    
    return color, textcolor, event_type_name
