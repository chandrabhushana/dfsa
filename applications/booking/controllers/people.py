"""
These functions contain the base functionality of people. 
Any subclass specific logic should be in that controller before or after calling these functions. 
"""
people_is_owner = lambda person: person.organisation==auth.user.organisation
import logging

def people_index(type, change_view=True):
    can_view_all = can('view-all', entity)
    org_filter = None if can_view_all else db.people.organisation==auth.user.organisation
    if len(request.args):
        page = int(request.args[0])
    else:
        page = 0
    items_per_page=49
    #if page!=0:
     #   limitby=((page*items_per_page)+1,(page+1)*items_per_page+2)
    #else:
    limitby=((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
    if request.vars.first_name or request.vars.last_name or request.vars.mobile or request.vars.email:
        people = list_people(type, filters=[org_filter])
        people = people.find(lambda person:
                               (lower_or(request.vars.first_name) in person.first_name.lower())
                               & (lower_or(request.vars.last_name) in person.last_name.lower())
                               & (lower_or(request.vars.mobile) in person.mobile.lower())
                               & (lower_or(request.vars.email) in person.email.lower()))
    
    elif (request.vars.first_name=='' and request.vars.last_name=='' and request.vars.mobile=='' and request.vars.email=='') or len(request.args)>0:
        people=list_people(type, filters=[org_filter],limitby=limitby,orderby=db.people.type)
        
    else:
        people=None    
    
    if change_view:
        response.view = 'people/index.' + request.extension
    return dict(people=people,page=page,items_per_page=items_per_page)


def people_create(type, change_view=True, required_email=False, can_assign_orgs=can('assign', 'organisations')):

        
   #ReqR3_12 for populating agent details in create client form on 31st Jan By Subhasmita
   
    #request.vars.email = auth.user.referral_contact_email
    if is_agency:
        request.vars.contact_name = auth.user.first_name
        request.vars.contact_number = auth.user.mobile
        request.vars.referral_contact_email = auth.user.email
    if can_assign_orgs:
        db.people.organisation.writable = True
    else:
        db.people.organisation.default = auth.user.organisation
        db.people.organisation.writable = False
    db.people.password.writable = True
    db.people.type.default = type
    db.people.password.default = auth.random_password()
    mobile = request.vars.mobile
    
    import re

    # genrate a flag to decide whether dummy email is to be genrated for client , only if mobile number
    # entered is valid
    
    if mobile:
        if re.match("^[ 0-9 ]*$", mobile):
            flag_to_genrate_dummy_email = True
        else:
            flag_to_genrate_dummy_email = False

        
    if not required_email and request.vars.email=='' and request.vars.mobile!=''and flag_to_genrate_dummy_email:    
        request.vars.email = (request.vars.mobile + '@email.com').replace(' ','')
    person_client = db(db.people.email==request.vars.email).select()
   # if person_client and not required_email and request.vars.mobile != '' and flag_to_genrate_dummy_email:
         #     request.vars.email = (request.vars.mobile + '@email.com').replace(' ','')
    if request.vars.date_of_birth == None:
        request.vars.date_of_birth = parse_date('2011-01-01')
    
    #Added for validation of empty organisation table
    if type == PERSON_TYPE_CLIENT:
        if not request.vars.organisation:
            request.vars.organisation = -1  
               
    form = SQLFORM(db.people, deletable=False, hidden=dict(key='type'), _name='createform')
    
    if form.accepts(request.vars,session, onvalidation=person_create_processing):
        
        session.flash = T(type + ' added!')
        redirect(URL(c=entity, f='view', args=form.vars.id))
    
    if not can_assign_orgs:
        form.custom.widget.organisation = resource_field_by_id(db.organisations, 'name', auth.user.organisation, default='None')
        
    if change_view:
        response.view = 'people/create.' + request.extension
    
    return dict(form=form)


def people_update(type, change_view=True, is_owner=people_is_owner, can_assign_orgs=can('assign', 'organisations')):
    person = db.people(request.args(0)) or redirect(URL(c=entity,f='index'))
    redirect_if_not_authorized_on(is_owner(person))
    can('activate', entity) or redirect_if_deactivated(person)
    db.people.organisation.writable = True if can_assign_orgs else False 
    db.people.password.writable = False
    
    if can('create', entity):
        if request.vars.email == person.email:
            db.people.password.writable = False
            #ReqR3_12 for populating agent details in create client form on 31st Jan By Subhasmita
            if is_agency:
                request.vars.contact_name = auth.user.first_name
                request.vars.contact_number = auth.user.mobile
                request.vars.referral_contact_email = auth.user.email
        elif request.vars.email != person.email:
            db.people.password.writable = True
            db.people.password.default = auth.random_password()
    
    
    if request.vars.date_of_birth==None:
        request.vars.date_of_birth = parse_date('2011-01-01')
    
    form = SQLFORM(db.people, person, deletable=False, hidden=dict(key='type'), _name='updateform')    
    if form.accepts(request.vars,session,onvalidation=person_create_processing):
        session.flash = T(type + ' updated!')
        redirect(URL(c=entity, f='view', args=str(person.id)))
    
    if not can_assign_orgs:
        form.custom.widget.organisation = resource_field_by_id(db.organisations, 'name', person.organisation, default='None')
    
    if change_view:
        response.view = 'people/update.' + request.extension
    
    return dict(form=form, person=person)

def people_view(type, change_view=True, is_owner=people_is_owner, get_activities=True):
    person_id = request.args(0)
    person = db.people(person_id) or redirect(URL(c=entity,f='index'))
    redirect_if_not_authorized_on(is_owner(person))
    can('activate',entity) or redirect_if_deactivated(person)
    activities = db(db.activities.person_id==person.id).select(orderby=db.activities.date) if get_activities else None
    
    if change_view:
        response.view = 'people/view.' + request.extension
    return dict(person=person, activities=activities)


def person_create_processing(form):
        
    from datetime import datetime
    if request.vars.date_of_birth==None:
        form.vars.date_of_birth = request.now.date()
    elif form.vars.date_of_birth!=None:
        try:
            date_of_birth = datetime.strptime(str(request.vars.date_of_birth),"%d-%m-%Y").date()
        except Exception as var:
            date_of_birth = None
        if not date_of_birth:
            try:
                date_of_birth = datetime.strptime(str(request.vars.date_of_birth),"%Y-%m-%d").date()
            except Exception as var:
                date_of_birth = None
        if form.vars.date_of_birth >= request.now.date() or (not date_of_birth )or (date_of_birth < datetime.strptime('01-01-1900',"%d-%m-%Y").date()): 
            form.errors.date_of_birth = 'Date of birth is invalid'
   
            
def people_login_set(enable, is_owner=people_is_owner):
    person_id = request.args(0)
    person = db.people(person_id) or redirect(URL(c=entity,f='index'))
    status = '' if enable else 'disabled'
    person.update_record(registration_key=status)
    redirect(URL(c=entity,f='view',args=person_id))
