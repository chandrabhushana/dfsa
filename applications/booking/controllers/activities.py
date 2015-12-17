### Activity Validations
db.activities.person_id.requires = IS_IN_DB(queryr(db.people, select=False), 'people.id', zero=None, error_message='Invalid Client ID')
# Activity type dropdown should not have Volunteer Roster
db.activities.type.requires = IS_IN_DB(queryr(db.event_types,[db.event_types.name !='Volunteer Roster'],select=False),'event_types.name', error_message='Please select a valid activity type')
db.activities.date.requires = [IS_NOT_EMPTY(error_message='Please select a date'),IS_DATE(format=T('%d-%m-%Y'))]
db.activities.image.requires =  [IS_NULL_OR(IS_IMAGE(extensions=('bmp', 'gif', 'jpeg', 'png'),minsize=(0,0), error_message='invalid image')),IS_NULL_OR(IS_LENGTH(minsize=0,maxsize=512000,error_message='Please choose an image of size < 500KB '))]

@auth.requires(has_auth)
def create():
    global items_list
    global person #to be accessed in activity_processing
    person_id = request.vars.person
    person = resource_by_id(db.people, person_id)
    redirect_if_not_authorized_on(person)
    set_person_validations(person)
   
    form = SQLFORM(db.activities)
       
    if form.vars.type != 'Dressings':
        form.vars.type_of_clothing = ''
         
    if form.accepts(request.vars,session, onvalidation=activity_processing):
        session.flash = T('Activity added!')
        activity_accepts_redirect(person)
    
    #change the input field type so it displays better and has spinner in chrome  
    for nbr in form.elements(_class='integer'):
        nbr['_type'] = 'number'
        nbr['_size'] = '1'
    
    response.view = entity + '/manage.' + request.extension
    return dict(form=form, person=person, readonly=False)

@auth.requires(has_auth)
def update():
    return view_update(readonly=False)

@auth.requires(has_auth)
def view():
    return view_update(readonly=True)

def view_update(readonly):
    global person #to be accessed in activity_processing
    activity = db.activities(request.args(0))
    if not activity:
        session.flash = dict(error=T('The selected activity does not exist'))
        redirect(URL(c='default',f='index'))

   
    # added to set vars when data is migrated from R1 to R2
    # this piece of code below is added to set vars to zero because of extra fields in items_distributed in R2
    if activity.type=="Career Support Program":
        for i in ACTIVITIES_ITEMS_BOTH:
            request.vars[i] = 0
                    
    person_id = activity.person_id
    person = resource_by_id(db.people, person_id)
    redirect_if_not_authorized_on(person)
    set_person_validations(person)
    
    form = SQLFORM(db.activities, activity, readonly=readonly, deletable=False, hidden=dict(key='person_id'))
    if form.accepts(request.vars, session, onvalidation=activity_processing):
        session.flash = T('Activity updated!')
        activity_accepts_redirect(person)





   
    #change the input field type so it displays better and has spinner in chrome
    for nbr in form.elements(_class='integer'): 
        nbr['_type'] = 'number'
        nbr['_size'] = '1'
    
    response.view = entity + '/manage.' + request.extension
    return dict(form=form, person=person,activity=activity, readonly=readonly)


"""Unexposed Helper methods from here down"""

def redirect_if_not_authorized_on(person):
    """
    Override redirect_if_not_authorized_on function from roles_perms.py
    Scenarios to check are activities added/updated for self, others in same org, or others in different org
    """
    if person==None:
        session.flash = 'Invalid person id'
        redirect(URL(c='default',f='index'))
    elif person.id==auth.user_id:
        return
    elif can(action + '-for-all', entity):
        return
    elif person.type==PERSON_TYPE_CLIENT:
        if can(action + '-for-all-clients', entity):
            return
        elif person.organisation == auth.user.organisation and can(action+'-for-clients-by-org', entity):    
            return
    
    redirect(URL(c='default',f='user',args='not_authorized'))


def set_person_validations(person):
    db.activities.person_id.default = person.id
    
    if person.type==PERSON_TYPE_CLIENT:
        IS_IN_RANGE_0_TO_100 = IS_INT_IN_RANGE(0, 100)
        
        if person.gender == 'Male':
            shoe_sizes_set = SHOE_SIZES_SET_MALE
            clothing_sizes_set = CLOTHING_SIZES_SET_MALE
            items_list = ACTIVITIES_ITEMS_MALE
        else:
            shoe_sizes_set = SHOE_SIZES_SET_FEMALE
            clothing_sizes_set = CLOTHING_SIZES_SET_FEMALE
            items_list = ACTIVITIES_ITEMS_FEMALE
        
        request.vars.gender = person.gender #default to the client's gender for simpler reports
        db.activities.gender.requires = []
        db.activities.shoe_size.requires = IS_NULL_OR(IS_IN_SET(shoe_sizes_set))
        db.activities.clothing_size.requires = IS_NULL_OR(IS_IN_SET(clothing_sizes_set))
        db.activities.start_time.requires = []
        db.activities.end_time.requires = []
        db.activities.type_of_clothing.requires = IS_NULL_OR(IS_IN_SET(TYPE_OF_CLOTHING_SET, error_message='Please choose a Type of clothing'))
        for x in items_list:
            db.activities.get(x).requires = IS_IN_RANGE_0_TO_100
        
    else:
        #Only set time as required for non-client (Volunteer/Employee)
        ACTIVITIES_GENDERS_SET = ('Both','Female','Male')
        db.activities.gender.requires=IS_IN_SET(ACTIVITIES_GENDERS_SET, error_message='Please choose a gender', zero=None)
        #Rel-3 R3_15 Extend hours to 11pm in in volunteer on Jan 22 by Mukesh
        db.activities.start_time.requires = IS_IN_SET(create_time_list(9, 23), zero=None)
        #Rel-3 R3_16 Extend hours to 11pm in in employee on Jan 22 by Mukesh
        db.activities.end_time.requires = IS_IN_SET(create_time_list(9, 23), zero=None)
        db.activities.shoe_size.requires = []
        db.activities.clothing_size.requires = []

def activity_accepts_redirect(person):
    if person.id==auth.user_id:
        redirect(URL(c='default',f='index'))
    else:
        people_entity = entity_by_person_type(person.type)
        redirect(URL(c=people_entity, f='view', args=person.id))

def activity_processing(form):
    #creating checkmark list here so that they can be defaulted to false when no_show is checked#
    career_support_program_checkmarks_list = ['pref_jobsearch' ,'pref_presentation','pref_interview','pref_resume','pref_computer','pref_mentoring','pref_workshops','pref_other','pref_lifeskills','pref_socialmedia']
    #items_list = ACTIVITIES_ITEMS_BOTH
    if person.type == PERSON_TYPE_EMPLOYEE or person.type == PERSON_TYPE_VOLUNTEER:
        if person.type==PERSON_TYPE_EMPLOYEE:
            form.vars.person_type = PERSON_TYPE_EMPLOYEE
        if person.type==PERSON_TYPE_VOLUNTEER:
            form.vars.person_type = PERSON_TYPE_VOLUNTEER
        import time
        end_time = time.strptime(form.vars.end_time, "%H:%M")
        start_time =  time.strptime(form.vars.start_time, "%H:%M")
        if end_time <= start_time:
            form.errors.end_time = 'End time must be after start time'
    if person.gender == "Male":
        items_list = ACTIVITIES_ITEMS_MALE
        list_one = ['nbr_skirts','nbr_makeup','nbr_dresses','nbr_softtops','nbr_kneehighs','nbr_scarves','nbr_handbags' ,'nbr_makeup', 'nbr_esteem_jewellery','nbr_boots', 'nbr_underwear', 'nbr_bra',  'nbr_camisole','nbr_stocking']
        for a in list_one:
            form.vars[a] = 0
    
    elif person.gender == "Female":
        items_list = ACTIVITIES_ITEMS_FEMALE
        list_two = ['nbr_socks','nbr_golfshirts','nbr_tshirts','nbr_cufflinks','nbr_ties']
        for b in list_two:
            form.vars[b] = 0
    else:
        items_list = ACTIVITIES_ITEMS_BOTH
    
       
    if form.vars.is_no_show == "on":
        for y in items_list:
            form.vars[y] = 0
        for z in career_support_program_checkmarks_list:
            if z != "pref_other":
                form.vars[z] = False  
            elif z == "pref_other" :
                form.vars[z] = ""
    if person.type==PERSON_TYPE_VOLUNTEER and form.vars.is_no_show:
        form.vars.gender = ''
        form.vars.start_time = '09:00'
        form.vars.end_time = '09:15'
        pass
    if person.type==PERSON_TYPE_CLIENT:
        form.vars.person_type = PERSON_TYPE_CLIENT
    #person is global var set in controller function
    if person.type==PERSON_TYPE_CLIENT and form.vars.type=='Dressings' and not form.vars.is_no_show:
        #if not form.vars.shoe_size:
         #   form.errors.shoe_size = 'Please choose a shoe size'
        #if not form.vars.clothing_size:
        #    form.errors.clothing_size = 'Please choose a clothing size'
        if not form.vars.type_of_clothing:
            form.errors.type_of_clothing = 'Please choose a type of clothing'
    else:
        form.vars.shoe_size = 'N/A'
        form.vars.clothing_size = 'N/A'
        form.vars.type_of_clothing = 'N/A'
