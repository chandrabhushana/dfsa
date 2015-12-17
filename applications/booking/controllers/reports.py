from gluon.storage import Storage
from datetime import timedelta
import time
import logging
from google.appengine.api import taskqueue

PER_PAGE = 49

"""Single auth check for the whole file"""
if not can('index', 'reports'):
    redirect(URL(c='default',f='user',args='not_authorized'))

def index():
    return dict()

def total_clients():

    if len(request.args):
        page = int(request.args[0])
    else: 
        page = 0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
    e_date = request.vars.effective_date if request.vars.effective_date else None
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        e_date = request.vars.effective_date if request.vars.effective_date else request.vars.e_date 
    else:
        if len(request.args)>1:
            e_date = request.args[1]
    result = []
    #Rel-3 reqR3_8 Client Add tick box in Client Record for Job Obtained added field job_obtained on Jan 22 by Mukesh
    colnames = ['created_on', 'title', 'first_name', 'last_name', 'contact_number', 'email', 'alternate_contact_number', 'date_of_birth', 'street_addr', 'suburb','city', 'postcode', 'gender', 'ethnicity', 'shoe_size', 'clothing_size', 'age', 'length_of_time_unemployed','ttw_paid','single_parent', 'type_of_job', 'educational_level', 'referring_organisation', 'referral_contact_name', 'referral_contact_number', 'referral_contact_email', 'permission_to_photo', 'permission_to_follow_up', 'permission_to_invite_events', 'comments', 'pref_jobsearch', 'pref_presentation', 'pref_interview', 'pref_resume', 'pref_computer',  'pref_mentoring', 'pref_workshops','job_obtained' ,'pref_other']  
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result = [],page=page,items_per_page=items_per_page,colnames=colnames)
    if request.vars.download:
        result_list = total_query(db.people,[db.people.type==PERSON_TYPE_CLIENT])
    else:
        result_list = total_query(db.people,[db.people.type==PERSON_TYPE_CLIENT],limitby=limitby)
        
    organisation = total_query(db.organisations)
    
    for x in result_list:
        convert_date = time.strptime(str(x['date_of_birth']),"%Y-%m-%d")if x['date_of_birth'] else None 
        x['date_of_birth'] = time.strftime('%Y-%m-%d',convert_date) if convert_date else None
        x.created_on = x.created_on.date()
    
        if x.organisation != None:
            org = db(db.organisations.id==x.organisation).select()
            for y in org:
                x.organisation = y.name
           
        #Rel-3 reqR3_8 Client Add tick box in Client Record for Job Obtained added field job_obtained on Jan 22 by Mukesh            
        pref_list = ['pref_jobsearch','pref_presentation','pref_resume','pref_computer','pref_interview','pref_workshops','job_obtained','pref_mentoring','pref_permission_to_photo','pref_permission_to_follow_up',
'pref_permission_to_invite_events','pref_other']
        for y in pref_list:
                if x[y]==False:
                    x[y] = "No"
                else:
                    x[y] = "Yes"
         #Rel-3 reqR3_8 Client Add tick box in Client Record for Job Obtained added field job_obtained on Jan 22 by Mukesh
        result.append(Storage(first_name=x.first_name,last_name=x.last_name,date_of_birth=x.date_of_birth,created_on=x.created_on.strftime('%Y-%m-%d'),comments=x.comments,title=x.title,email=x.email,gender=x.gender,age=x.age_range,ethnicity=x.ethnicity,shoe_size=x.shoe_size,clothing_size=x.clothing_size,pref_jobsearch=x.pref_jobsearch,job_obtained=x.job_obtained,pref_presentation=x.pref_presentation,pref_resume=x.pref_resume,pref_computer=x.pref_computer,pref_interview=x.pref_interview,pref_workshops=x.pref_workshops,pref_mentoring=x.pref_mentoring,pref_other=x.pref_other,contact_number=x.mobile,alternate_contact_number=x.second_contact_number,referring_organisation=x.organisation,street_addr=x.street_addr,
suburb=x.suburb_addr,city=x.city_addr,postcode=x.postcode_addr,
type_of_job=x.type_of_job,referral_contact_name=x.contact_name,referral_contact_number=x.contact_number,
referral_contact_email=x.referral_contact_email,length_of_time_unemployed=x.length_of_time_unemployed,ttw_paid=x.ttw_paid,single_parent=x.single_parent,job_type=x.job_type,educational_level=x.educational_level,
permission_to_photo=x.pref_permission_to_photo,permission_to_follow_up=x.pref_permission_to_follow_up,permission_to_invite_events=x.pref_permission_to_invite_events))
    
    return view_or_download(result=result, e_date=e_date, page=page, items_per_page=items_per_page, colnames=colnames)

def all_agencies():

    if len(request.args):
        page = int(request.args[0])
    else:
        page = 0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
    result = []  
    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
       
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
        
    else:
         if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]
    
    colnames = ['first_name', 'last_name', 'created_on', 'contact','second_contact_number', 'email','pref_other','organisation'] 
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result = [],page=page,items_per_page=items_per_page,)
    if request.vars.download:
        result = total_query(db.people,[db.people.type==PERSON_TYPE_AGENCY])
    else:
        result = total_query(db.people,[db.people.type==PERSON_TYPE_AGENCY],limitby=limitby)
    for x in result:
        x.created_on = x.created_on.date().strftime('%Y-%m-%d')
        if x.organisation != None:
            org = db(db.organisations.id==x.organisation).select()
            for y in org:
                x.organisation = y.name
        x.contact = x.mobile
  
    return view_or_download(result=result,page=page, st_date=st_date, en_date=en_date,items_per_page=items_per_page, colnames=colnames)

def all_volunteers():

    if len(request.args):
        page = int(request.args[0])
    else:
        page = 0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
    #e_date = request.vars.effective_date if request.vars.effective_date else None
    
    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        #e_date = request.vars.effective_date if request.vars.effective_date else request.vars.e_date 
        
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
        
    else:
         if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]
    
    result = []
    colnames = ['first_name', 'last_name', 'created_on', 'contact', 'email', 'second_contact_number','date_of_birth','date_trained', 'street_addr', 'suburb_addr','city_addr', 'postcode_addr', 'organisation','contact_name', 'contact_number','medical_conditions','pref_police','pref_induction','pref_children_check','comments','pref_shadow', 'pref_showroom','pref_fitting','pref_admin','pref_collection','pref_donations','pref_careers','pref_going_places_network','pref_professional_womens_group','pref_mentoring','pref_other']
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result = [],page=page,items_per_page=items_per_page)
    
    if request.vars.download:
        result_list = total_query(db.people,[db.people.type==PERSON_TYPE_VOLUNTEER])
    else:
        result_list = total_query(db.people,[db.people.type==PERSON_TYPE_VOLUNTEER],limitby=limitby)
        
    for x in result_list:
        x.created_on = x.created_on.date().strftime('%Y-%m-%d')
        if x.organisation != None:
            org = db(db.organisations.id==x.organisation).select()
            for y in org:
                x.organisation = y.name
        pref_list = ['pref_police','pref_induction','pref_children_check','pref_shadow','pref_showroom','pref_fitting','pref_admin','pref_collection','pref_donations','pref_careers','pref_going_places_network','pref_professional_womens_group','pref_mentoring']
        for y in pref_list:
                if x[y]==False:
                    x[y] = "No"
                else:
                    x[y] = "Yes"
        result.append(Storage(first_name=x.first_name,last_name=x.last_name,contact=x.mobile,email=x.email,second_contact_number=x.second_contact_number,date_of_birth=x.date_of_birth,date_trained=x.date_trained,street_addr=x.street_addr,suburb_addr=x.suburb_addr,city_addr=x.city_addr,postcode_addr=x.postcode_addr,organisation=x.organisation,created_on=x.created_on,contact_name=x.contact_name,contact_number=x.contact_number,medical_conditions=x.medical_conditions,pref_police=x.pref_police,pref_induction=x.pref_induction,pref_children_check=x.pref_children_check,comments=x.comments,pref_shadow=x.pref_shadow,pref_showroom=x.pref_showroom,pref_fitting=x.pref_fitting,pref_admin=x.pref_admin,pref_collection=x.pref_collection,pref_donations=x.pref_donations,pref_careers=x.pref_careers,pref_going_places_network=x.pref_going_places_network,pref_professional_womens_group=x.pref_professional_womens_group,pref_mentoring=x.pref_mentoring,pref_other=x.pref_other))

    return view_or_download(result=result,page=page, st_date=st_date, en_date=en_date,items_per_page=items_per_page, colnames=colnames)

def total_employees():

    if len(request.args):
        page = int(request.args[0])
    else:
        page=0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))

    #e_date = request.vars.effective_date if request.vars.effective_date else None
    
    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        #e_date = request.vars.effective_date if request.vars.effective_date else request.vars.e_date 
        
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
    else:
        #if len(request.args)>1:
         #   e_date = request.args[1]
    
       if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]
    
    result = []
    colnames = ['first_name', 'last_name', 'created_on', 'contact', 'email', 'second_contact_number', 'street_addr', 'suburb_addr','city_addr','postcode_addr', 'contact_name', 'contact_number', 'pref_showroom', 'pref_fitting', 'pref_admin', 'pref_collection', 'pref_donations', 'pref_careers', 'pref_other'] 
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result = [],page=page,items_per_page=items_per_page)
    if request.vars.download:
        result_list = total_query(db.people,[db.people.type==PERSON_TYPE_EMPLOYEE])
    else:
        result_list = total_query(db.people,[db.people.type==PERSON_TYPE_EMPLOYEE],limitby=limitby)
    for x in result_list:
        x.created_on = x.created_on.date()
        pref_list = ['pref_showroom','pref_fitting','pref_admin','pref_collection','pref_donations','pref_careers','pref_other']
        for y in pref_list:
                if x[y]==False:
                    x[y] = "No"
                else:
                    x[y] = "Yes"
        result.append(Storage(first_name=x.first_name,last_name=x.last_name,contact=x.mobile,email=x.email,created_on=x.created_on.strftime('%Y-%m-%d'),second_contact_number=x.second_contact_number,street_addr=x.street_addr,suburb_addr=x.suburb_addr,city_addr=x.city_addr,postcode_addr=x.postcode_addr,contact_name=x.contact_name,
contact_number=x.contact_number,pref_showroom=x.pref_showroom,pref_fitting=x.pref_fitting,pref_admin=x.pref_admin,pref_collection=x.pref_collection,pref_donations=x.pref_donations,pref_careers=x.pref_careers,pref_other=x.pref_other))
    #return view_or_download(result=result,page=page,e_date=e_date,items_per_page=items_per_page,colnames=colnames)
    
    return view_or_download(result=result,page=page,st_date=st_date, en_date=en_date,items_per_page=items_per_page,colnames=colnames)

def all_activities():
    if len(request.args):
        page = int(request.args[0])
    else:
        page=0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))

    result = []
    #Rel-3 reqR3_8 Client Add tick box in Client Record for Job Obtained added field job_obtained on Jan 24 by Mukesh
    colnames = ['activity_date', 'activity_type', 'is_no_show', 'gender', 'type_of_clothing', 'shoe_size', 'clothing_size', 'nbr_suits', 'nbr_coats', 'nbr_jackets', 'nbr_shirts', 'nbr_pants', 'nbr_shoes', 'nbr_knitwear', 'nbr_misc', 'nbr_socks', 'nbr_golfshirts', 'nbr_tshirts', 'nbr_belts', 'nbr_cufflinks', 'nbr_ties', 'nbr_skirts', 'nbr_dresses', 'nbr_softtops', 'nbr_kneehighs', 'nbr_scarves', 'nbr_handbags', 'nbr_makeup', 'nbr_esteem_jewellery', 'nbr_boots', 'nbr_underwear', 'nbr_bra', 'nbr_camisole', 'nbr_stocking', 'pref_jobsearch', 'pref_presentation', 'pref_resume', 'pref_computer', 'pref_interview', 'pref_workshops', 'job_obtained','pref_mentoring','pref_lifeskills','pref_socialmedia', 'pref_other']
    
    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
    else:
        if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]

    convert_start_date = time.strptime(request.vars.start_date,"%d-%m-%Y") if request.vars.start_date else None
    stt_date = time.strftime('%Y-%m-%d',convert_start_date) if convert_start_date else None

    convert_end_date = time.strptime(request.vars.end_date,"%d-%m-%Y") if request.vars.end_date else None
    enn_date = time.strftime('%Y-%m-%d',convert_end_date) if convert_end_date else None
    
    start_filter = parse_date(st_date, as_datetime=False)
    end_filter = parse_date(en_date, as_datetime=False)
    
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result = [],page=page,items_per_page=items_per_page)
    
    if request.vars.download:
        activities = activities_query(type='Dressings', use_date_filters=True, orderby=db.activities.date)
    else:
        activities = activities_query(type='Dressings', use_date_filters=True, orderby=db.activities.date, limitby=limitby)
        
    gender = request.vars.gender
    if gender=='All':
        gender = None
        
    for activity in activities:
        if gender and not (activity.gender==gender or activity.gender=='Both'):
            continue
        if not ((start_filter and activity.date<start_filter)
            or (end_filter and activity.date>end_filter)):
                row = Storage()
                row['activity_date'] = activity.date.strftime('%Y-%m-%d')
                row['is_no_show'] = activity.is_no_show
                row['activity_type'] = activity.type
                row['gender'] = activity.gender
                row['type_of_clothing'] = activity.type_of_clothing
                row['nbr_cufflinks'] = activity.nbr_cufflinks
                row['nbr_ties'] = activity.nbr_ties
                row['nbr_suits'] = activity.nbr_suits
                row['nbr_coats'] = activity.nbr_coats
                row['nbr_jackets'] = activity.nbr_jackets
                row['nbr_shirts'] = activity.nbr_shirts
                row['nbr_pants'] = activity.nbr_pants
                row['nbr_shoes'] = activity.nbr_shoes
                row['nbr_knitwear'] = activity.nbr_knitwear
                row['nbr_misc'] = activity.nbr_misc
                row['nbr_socks'] = activity.nbr_socks
                row['nbr_golfshirts'] = activity.nbr_golfshirts
                row['nbr_belts'] = activity.nbr_belts
                row['nbr_tshirts'] = activity.nbr_tshirts
                row['nbr_skirts'] = activity.nbr_skirts
                row['nbr_dresses'] = activity.nbr_dresses 
                row['nbr_softtops'] = activity.nbr_softtops
                row['nbr_kneehighs'] = activity.nbr_kneehighs
                row['nbr_scarves'] = activity.nbr_scarves
                row['nbr_handbags'] = activity.nbr_handbags
                row['nbr_makeup'] = activity.nbr_makeup
                row['nbr_esteem_jewellery'] = activity.nbr_esteem_jewellery
                row['nbr_boots'] = activity.nbr_boots
                row['nbr_underwear'] = activity.nbr_underwear 
                row['nbr_bra'] = activity.nbr_bra
                row['nbr_camisole'] = activity.nbr_camisole 
                row['nbr_stocking'] = activity.nbr_stocking 
                
                result.append(row)
        
    return view_or_download(result=result, page=page, st_date=st_date,en_date=en_date,items_per_page=items_per_page, colnames=colnames)

def active_employees():

    if len(request.args):
        page = int(request.args[0])
    else:
        page=0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))

    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
    else:
        if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]
    
    
    colnames = ['first_name','last_name', 'contact',  'organisation', 'created_on','pref_showroom','pref_fitting','pref_admin','pref_collection','pref_donations','pref_careers','pref_other']
    result=[]
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result=[], page=page, items_per_page=items_per_page)

    activation_type = 'employees'
    
    if request.vars.download:
        result_list = active_query(db.people, [db.people.type==PERSON_TYPE_EMPLOYEE],activation_type=activation_type)
    else:
        result_list = active_query(db.people, [db.people.type==PERSON_TYPE_EMPLOYEE],activation_type=activation_type, limitby=limitby)
        
    for x in result_list:
        list = ['pref_showroom','pref_fitting','pref_admin','pref_collection','pref_donations','pref_careers']
        for y in list:
            if x[y]==False:
                x[y] = "No"
            else:
                x[y] = "Yes"
        result.append(Storage(first_name=x.first_name,last_name=x.last_name,contact=x.mobile,organisation=x.organisation,created_on=x.created_on.strftime('%Y-%m-%d'),pref_showroom=x.pref_showroom,pref_fitting=x.pref_fitting,pref_admin=x.pref_admin,pref_collection=x.pref_collection,pref_donations=x.pref_donations,pref_careers=x.pref_careers,pref_other=x.pref_other))
    return view_or_download(result=result, page=page, st_date=st_date,en_date=en_date,items_per_page=items_per_page, colnames=colnames)

def employee_hours():
    
    if len(request.args):
        page = int(request.args[0])
    else:
        page=0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))

    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
    else:
        if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]
    
    result = []
    colnames = ['employee', 'type', 'date', 'gender','total_time']
    
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result=[], page=page,items_per_page=items_per_page,colnames=colnames)

    
    
    activities = activities_query(use_date_filters=True,filters=[db.activities.person_type==PERSON_TYPE_EMPLOYEE])
    activities.exclude(lambda r: r.is_no_show==True)
    
    #going to do gender filter while looping instead of pushing down to db, to avoid building index just for reports
    gender = request.vars.gender
    if gender=='All':
        gender = None
    if request.vars.download:
        volunteers = queryr(db.people, [db.people.type==PERSON_TYPE_EMPLOYEE],show_deactivated=True)
    else:
        volunteers = queryr(db.people, [db.people.type==PERSON_TYPE_EMPLOYEE],show_deactivated=True,limitby=limitby)
    
    total_delta = timedelta(0)
    activity_list = []
    
    for activity in activities:
        
        if gender and not (activity.gender==gender or activity.gender=='Both'):
            continue
        
        employee = volunteers.find(lambda v: v.id==activity.person_id).first()
        #continue for non-volunteer activities (client and employee)
        if employee==None:
            continue
        
        start_time = parse_time(activity.start_time)
        end_time = parse_time(activity.end_time)
        if not start_time or not end_time:
            continue #in case the value in the db was empty or invalid 
        
        delta = end_time - start_time
        total_delta += delta #must be added after the is volunteer check
        result.append(Storage(employee=display_name(employee),type=activity.type,date=activity.date.strftime('%Y-%m-%d'),gender=activity.gender,total_time=str(delta)))
    return view_or_download(result=result, colnames=colnames, st_date=st_date, en_date=en_date, page=page,items_per_page=items_per_page, time_count=str(total_delta))


def no_shows():
    """ list the no shows by activity type 
        still need to use clients so we dont include volunteer no shows
        
    looping though all clients and get their activities under the assumption that no shows list will be relatively small
    """

    if len(request.args):
        page = int(request.args[0])
    else:
        page=0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))

    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
    else:
        if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]
    
    #check if the form was submitted. otherwise return empty result and show form 
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result=[], page=page, items_per_page=items_per_page, total=0)
    
    #see if it is all, first visits, returning visits, or no shows 
    visit_filter = request.args(0)
    if visit_filter==FITTING_REPORTS.NO_SHOWS:
        return no_shows()
    #Added for req R3_4 for firstname and lastname in no_show report on 8th Feb by Subhasmita
    #Added for req R3_4 for firstname and lastname in no_show report on 26th Feb by Mukesh Include the Date field in the �No Show Report�
    colnames = ['activity_date','first_name', 'last_name', 'activity_type', 'is_no_show']         
    
    #fetch ALL records from the database initially
    #    date filters are not done up-front since we need to determine first time visit vs return visit BEFORE applying the date filters from the form
    #employees = db(db.people.type==PERSON_TYPE_EMPLOYEE).select()
    filters=[]
    filters.append(db.activities.person_type==PERSON_TYPE_CLIENT)
    
    if request.vars.download:
        activities = activities_query(filters=[db.activities.is_no_show==True,db.activities.person_type==PERSON_TYPE_CLIENT], use_date_filters=True, client_fitting=True)
    else:
        activities = activities_query(filters=[db.activities.is_no_show==True,db.activities.person_type==PERSON_TYPE_CLIENT], use_date_filters=True, client_fitting=True, limitby=limitby)

    if activities!=None:
       clients = db(db.people.type==PERSON_TYPE_CLIENT).select()
    else:
        return dict(result=[], page=page, items_per_page=items_per_page, total=0)
    
    convert_start_date = time.strptime(request.vars.start_date,"%d-%m-%Y") if request.vars.start_date else None
    stt_date = time.strftime('%Y-%m-%d',convert_start_date) if convert_start_date else None

    convert_end_date = time.strptime(request.vars.end_date,"%d-%m-%Y") if request.vars.end_date else None
    enn_date = time.strftime('%Y-%m-%d',convert_end_date) if convert_end_date else None
    
    start_filter = parse_date(stt_date, as_datetime=False)
    end_filter = parse_date(enn_date, as_datetime=False)
    counter_dict = {}
    total = 0
    result = []
    #list_one = [,'nbr_makeup', 'nbr_esteem_jewellery','nbr_boots', 'nbr_underwear', 'nbr_bra',  'nbr_camisole','nbr_stocking']
    #Helper method for adding records to the result array based on form filters and type of report
    #def add_to_result(activity, employee):                   
    #going to do gender filter while looping instead of pushing down to db, to avoid building index just for reports
    gender = request.vars.gender
    if gender=='All':
        gender = None

    activities_dict = {}           

    person_set = set() 
    for activity_person in activities:
        person_set.add(activity_person.person_id)

    for person_id in person_set:
        person_activity_list = []
        for acts in activities:
            if person_id == acts.person_id:
                person_activity_list.append(acts)
                activities_dict[acts.person_id] = person_activity_list
                
          
    
    #process employees one-by-one and get their activities.
    for client in clients:       
    
        #In memory filter of the activities using the dict rather than a db lookup for each client
        it_activities = activities_dict.get(client.id, [])
        
        for y in it_activities:
            if y.is_no_show == True:
                y.is_no_show = "Yes"
            else:
                y.is_no_show = "No"
            
        for activity in it_activities:
            if gender and not (activity.gender==gender or activity.gender=='Both'):
                continue
            if client.id in person_set:
                if not ((start_filter and activity.date<start_filter)
                or (end_filter and activity.date>end_filter)):
                    row = Storage()
                    row['activity_date'] = activity.date.strftime('%Y-%m-%d')                     
                    row['activity_type'] = activity.type
                    row['is_no_show'] = activity.is_no_show
                    row['client_id'] = client.id
                    for k in client:
                        row[k] = client.get(k)
                        row['contact']=client.get('mobile')
                        row['gender'] = activity.gender
                    result.append(row)
                #add_to_result(activity, employee)
            else:
                continue
    
    return view_or_download(result=result, page=page, items_per_page=items_per_page, st_date=st_date, en_date=en_date, colnames=colnames)


def client_fittings():

    if len(request.args):
        page = int(request.args[0])
        logging.info(page)
    else:
        page=0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))

    logging.info("Limitby")
    logging.info(limitby)

    gender = request.vars.gender
    if gender=='All':
        gender = None
    logging.info(gender)
    
    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    if request.vars.view or request.vars.download:
        logging.info("Help me")
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
    else:
        logging.info("Good Good")
        if len(request.args)>3:
            st_date=request.args[2]
            en_date=request.args[3]
            gender = request.args[4]
            logging.info("Inside len(request.args)")
            
     
    
    #check if the form was submitted. otherwise return empty result and show form 
    if not (request.vars.download or request.vars.view):
        if(len(request.args)<3 and page==0):
            logging.info("I m coming out")
            return dict(result=[], page=page,items_per_page=items_per_page,total=0)
    
    #see if it is all, first visits, returning visits, or no shows 
    visit_filter = request.args(1)
    if visit_filter==FITTING_REPORTS.NO_SHOWS:
        return no_shows()
    logging.info("Visit Filter")
    logging.info(visit_filter)
    colnames = ['fitting_date', 'visit', 'visits', 'first_name', 'last_name', 'contact', 'gender', 'age_range', 'ethnicity', 'shoe_size', 'clothing_size']    

    #going to do gender filter while looping instead of pushing down to db, to avoid building index just for reports
    
        
    #fetch ALL records from the database initially
    #    date filters are not done up-front since we need to determine first time visit vs return visit BEFORE applying the date filters from the form
    #clients = db(db.people.type==PERSON_TYPE_CLIENT).select()
    filters = []
    filters.append(db.activities.person_type==PERSON_TYPE_CLIENT)
    if gender!=None:
        filters.append(db.activities.gender==gender)
        logging.info("Gender None")
    
    if request.vars.download:
        activities = activities_query(type='Dressings', filters=filters, use_date_filters=True, orderby=db.activities.date, client_fitting=True)
    else:
        activities = activities_query(type='Dressings', filters=filters, use_date_filters=True, orderby=db.activities.date,limitby=limitby,client_fitting=True)
    logging.info("Length of activities")    
    logging.info(len(activities))
    
    if activities != None:
        clients = db(db.people.type==PERSON_TYPE_CLIENT).select()
        logging.info("Clients")
        logging.info(len(clients))
    else:
        return dict(result=[], page=page,items_per_page=items_per_page,total=0)
    
    convert_start_date = time.strptime(request.vars.start_date,"%d-%m-%Y") if request.vars.start_date else None
    stt_date = time.strftime('%Y-%m-%d',convert_start_date) if convert_start_date else None

    convert_end_date = time.strptime(request.vars.end_date,"%d-%m-%Y") if request.vars.end_date else None
    enn_date = time.strftime('%Y-%m-%d',convert_end_date) if convert_end_date else None
    
    start_filter = parse_date(st_date, as_datetime=False)
    end_filter = parse_date(en_date, as_datetime=False)
    
    result = []
    
    #Helper method for adding records to the result array based on form filters and type of report
    def add_to_result(activity, client, visit, visits):
        if not ((start_filter and activity.date<start_filter)
            or (end_filter and activity.date>end_filter)
            or (visit_filter==FITTING_REPORTS.RETURN_VISITS and visit==1)
            or (visit_filter==FITTING_REPORTS.FIRST_VISITS and visit>1)):
                row = Storage(visit=visit, visits=visits)
                row['fitting_date'] = activity.date.strftime('%Y-%m-%d')
                row['client_id'] = client.id
                for k in client:
                    row[k] = client.get(k)
                    row['contact']=client.get('mobile')
                result.append(row)
                              
    
        
    activities_dict = {}
    
    logging.info("Length of activities")           
    logging.info(len(activities))
    person_set = set() 
    for activity_person in activities:
        person_set.add(activity_person.person_id)
    logging.info(person_set)

    for person_id in person_set:
        person_activity_list = []
        for acts in activities:
            if person_id == acts.person_id:
                person_activity_list.append(acts)
                activities_dict[acts.person_id] = person_activity_list
    logging.info("person_set")
    logging.info(len(person_set))
    logging.info("Length of act_dict")
    logging.info(len(activities_dict))
                
    #process clients one-by-one and get their activities.
    for client in clients:
        #if gender and client.gender!=gender:
            #continue
        
        #In memory filter of the activities using the dict rather than a db lookup for each client
        it_activities = activities_dict.get(client.id, [])
        
        #it_activities = activities.exclude(lambda row: row.person_id==client.id)
        #it_activities.exclude(lambda row:row.is_no_show==True)
        #for no_show in it_activities:
             #if no_show.is_no_show==True:
                  #it_activities.remove(no_show) 
        visits = len(it_activities)
        #logging.info(visits)
        #for idx, activity in enumerate(it_activities):
            #add_to_result(activity, client, idx+1, visits)

        for idx,activity in enumerate(it_activities):
            logging.info(activity.id)
            #if gender and not (activity.gender==gender or activity.gender=='Both'):
                #continue
            if client.id in person_set:
                add_to_result(activity, client, idx+1, visits)
            else:
                continue
            
    return view_or_download(result=result,page=page,st_date=st_date,en_date=en_date,gnder=gender,items_per_page=items_per_page, colnames=colnames)

def all_volunteers_activities():

    if len(request.args):
        page = int(request.args[0])
    else:
        page=0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))

    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
    else:
        if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]
    
    #check if the form was submitted. otherwise return empty result and show form 
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result=[],page=page,items_per_page=items_per_page,total=0)
    
    #see if it is all, first visits, returning visits, or no shows 
    visit_filter = request.args(0)
    if visit_filter==FITTING_REPORTS.NO_SHOWS:
        return no_shows()
    
    colnames = ['activity_date','activity_type','first_name', 'last_name', 'contact', 'gender',  'start_time', 'end_time']    
    
    #fetch ALL records from the database initially
    #    date filters are not done up-front since we need to determine first time visit vs return visit BEFORE applying the date filters from the form
    #volunteers = db(db.people.type==PERSON_TYPE_VOLUNTEER).select()
    filters = []
    filters.append(db.activities.person_type==PERSON_TYPE_VOLUNTEER)
    if request.vars.download:
        activities = activities_query(filters=filters, orderby=db.activities.date)
    else:
        activities = activities_query(filters=filters, orderby=db.activities.date, use_date_filters=True, limitby=limitby)

    if activities!= None:
        volunteers = db(db.people.type==PERSON_TYPE_VOLUNTEER).select()
    else:
        return dict(result=[],page=page,items_per_page=items_per_page,total=0)
        
    
    convert_start_date = time.strptime(request.vars.start_date,"%d-%m-%Y") if request.vars.start_date else None
    stt_date = time.strftime('%Y-%m-%d',convert_start_date) if convert_start_date else None

    convert_end_date = time.strptime(request.vars.end_date,"%d-%m-%Y") if request.vars.end_date else None
    enn_date = time.strftime('%Y-%m-%d',convert_end_date) if convert_end_date else None
    
    start_filter = parse_date(stt_date, as_datetime=False)
    end_filter = parse_date(enn_date, as_datetime=False)
    
    result = []
    
    #Helper method for adding records to the result array based on form filters and type of report
    #def add_to_result(activity, volunteer):                        
    #going to do gender filter while looping instead of pushing down to db, to avoid building index just for reports
    gender = request.vars.gender
    
    if gender=='All':
        gender = None
    activities_dict = {}           

    person_set = set() 
    for activity_person in activities:
        person_set.add(activity_person.person_id)

    for person_id in person_set:
        person_activity_list = []
        for acts in activities:
            if person_id == acts.person_id:
                person_activity_list.append(acts)
                activities_dict[acts.person_id] = person_activity_list       
    
    #process Volunteers one-by-one and get their activities.
    for volunteer in volunteers:
        
        #In memory filter of the activities using the dict rather than a db lookup for each volunteer
        it_activities = activities_dict.get(volunteer.id, [])
        
        #it_activities = activities.exclude(lambda row: row.person_id==volunteer.id)
        #it_activities.exclude(lambda row: row.is_no_show==True)
        
        for activity in it_activities:
            if gender and not (activity.gender==gender or activity.gender=='Both'):
                continue
            if volunteer.id in person_set:
                if not ((start_filter and activity.date<start_filter)
                or (end_filter and activity.date>end_filter)):
                    row = Storage()
                    row['activity_date'] = activity.date.strftime('%Y-%m-%d')
                    row['start_time'] = activity.start_time
                    row['end_time'] = activity.end_time
                    row['volunteer_id'] = volunteer.id
                    for k in volunteer:
                        row[k] = volunteer.get(k)
                        row['contact']=volunteer.get('mobile')
                        row['activity_type'] = activity.type
                        row['gender'] = activity.gender
                    result.append(row)
            else:
                continue
    
    return view_or_download(result=result,page=page,st_date=st_date,en_date=en_date,items_per_page=items_per_page, colnames=colnames)

def organisations_all():

    if len(request.args):
        page = int(request.args[0])
    else: 
        page = 0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))

    #e_date = request.vars.effective_date if request.vars.effective_date else None
    
    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        #e_date = request.vars.effective_date if request.vars.effective_date else request.vars.e_date 
        
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
        
    else:
        #if len(request.args)>1:
         #   e_date = request.args[1]
        
        if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]
            
    result = []
    #colnames = ['name','abn','desc','created_on','street','suburb','state','postcode','contact_name','contact_phone','contact_mobile','second_contact_number','contact_email','ref_dis','ref_jobsvc','ref_com','ref_edu','ref_dept_employment','ref_dept_corrective','ref_other','sp_fin','sp_don','sp_vol','sp_other','other_ref','other_sponsor']
    # Removed 'second_contact_number' to fixed for defect R2_PT_Defect_35
    colnames = ['name','desc','created_on','street','suburb','city','postcode','organisations_types','contact_name','contact_phone','contact_mobile','contact_email','ref_dis','ref_jobsvc','ref_com','ref_edu','ref_dept_employment','ref_dept_corrective','ref_job_placement_service','ref_work_income','ref_other','sp_fin','sp_don','sp_vol','sp_other','other_ref','other_sponsor']
    
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result = [],page=page,items_per_page=items_per_page)
    
    if request.vars.download:
        result_list = total_query(db.organisations)
    else:
        result_list = total_query(db.organisations, limitby=limitby)
        
    for x in result_list:
        x.created_on = x.created_on.date().strftime('%Y-%m-%d')
        list = ['is_in_kind_doanations','is_education_ref','is_dept_employment','is_dept_corrective','is_job_placement_service','is_work_income','is_disability_ref','is_jobservice_aus_ref','is_community_ref','is_financial_sponsor','is_volunteer_sponsor']
        for y in list:
            if x[y]==False:
                x[y] = "No"
            else:
                x[y] = "Yes"
        result.append(Storage(name=x.name,desc=x.desc,created_on=x.created_on,street=x.street_addr,suburb=x.suburb_addr,city=x.city_addr,postcode=x.postcode_addr,organisations_types=x.organisations_types,contact_name=x.contact_name,contact_phone=x.contact_phone,contact_mobile=x.contact_mobile,contact_email=x.contact_email,ref_dis=x.is_disability_ref,ref_jobsvc=x.is_jobservice_aus_ref,ref_com=x.is_community_ref,ref_edu=x.is_education_ref,ref_dept_employment=x.is_dept_employment,ref_dept_corrective=x.is_dept_corrective,ref_job_placement_service=x.is_job_placement_service,ref_work_income=x.is_work_income,ref_other=x.other_ref,sp_fin=x.is_financial_sponsor,sp_don = x.is_in_kind_doanations,sp_vol=x.is_volunteer_sponsor,sp_other=x.other_sponsor))
    return view_or_download(result=result,page=page,st_date=st_date, en_date=en_date,items_per_page=items_per_page, colnames=colnames)


def client_activities():

    if len(request.args):
        page = int(request.args[0])
    else: 
        page = 0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
            
    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
    else:
        if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]
    
    #check if the form was submitted. otherwise return empty result and show form 
    if not (request.env.request_method == 'POST'):
        return dict(result=[], page=page, items_per_page=items_per_page, total=0)
    
    #see if it is all, first visits, returning visits, or no shows 
    visit_filter = request.args(0)
    if visit_filter==FITTING_REPORTS.NO_SHOWS:
        return no_shows()
    
    gender = request.vars.gender
    
    adminDetails = queryr(db.people,[db.people.type=='Admin'])
    if adminDetails :
        logging.debug ('In try')
        receiverEmail = []
        receiverEmail = map(lambda row : row.email, adminDetails )
        strRecevEmail = ','.join(receiverEmail)
        
    else :
        logging.debug ('In except')
        receiverEmail = []
        strRecevEmail = mail.settings.sender
     
    convert_start_date = time.strptime(request.vars.start_date,"%d-%m-%Y") if request.vars.start_date else None
    stt_date = time.strftime('%Y-%m-%d',convert_start_date) if convert_start_date else None
    
    convert_end_date = time.strptime(request.vars.end_date,"%d-%m-%Y") if request.vars.end_date else None
    enn_date = time.strftime('%Y-%m-%d',convert_end_date) if convert_end_date else None
    
    start_filter = parse_date(stt_date, as_datetime=False)
    end_filter = parse_date(enn_date, as_datetime=False)  
    
    max_count = db(db.people.type==PERSON_TYPE_CLIENT).count()
    
    logging.debug(max_count)
    
    # Calling Taskqueue for further processing
    taskqueue.add(url=URL(c='report_taskqueue',f='client_activities_tq'),params=dict(cursor = '',filename ='', start_date = str(start_filter),end_date = str(end_filter),gender = gender,receiverEmail=strRecevEmail,max_count = str(max_count),fetch_records = str(0)),method='GET')
    #taskqueue.add(url=URL(c='report_taskqueue',f='client_activities_tq'),params=dict(gender = gender,receiverEmail=strRecevEmail),method='GET')
    
    #return 'The report mailed to the user'
    #return response.json({'message', 'The report mailed to the user'})
    return response.render('reports/success.json', dict(message ='The report mailed to the user'))
    

    
def active_volunteers():

    if len(request.args):
        page = int(request.args[0])
    else: 
        page = 0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))

    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
    else:
        if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]

    
    colnames = ['first_name','last_name', 'contact',  'organisation', 'created_on','pref_showroom','pref_fitting','pref_admin','pref_collection','pref_donations','pref_careers','pref_other']
    result=[]
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result=[],page=page, items_per_page=items_per_page)

    activation_type = 'volunteers'
    
    if request.vars.download:
        result_list = active_query(db.people, [db.people.type==PERSON_TYPE_VOLUNTEER], activation_type=activation_type)
    else:
        result_list = active_query(db.people, [db.people.type==PERSON_TYPE_VOLUNTEER], activation_type=activation_type, limitby=limitby)
    for x in result_list:
        list = ['pref_showroom','pref_fitting','pref_admin','pref_collection','pref_donations','pref_careers']
        for y in list:
            if x[y]==False:
                x[y] = "No"
            else:
                x[y] = "Yes"
        result.append(Storage(first_name=x.first_name,last_name=x.last_name,contact=x.mobile,organisation=x.organisation,created_on=x.created_on.strftime('%Y-%m-%d'),pref_showroom=x.pref_showroom,pref_fitting=x.pref_fitting,pref_admin=x.pref_admin,pref_collection=x.pref_collection,pref_donations=x.pref_donations,pref_careers=x.pref_careers,pref_other=x.pref_other))
    return view_or_download(result=result, page=page, items_per_page=items_per_page, st_date=st_date,en_date=en_date,colnames=colnames)

def items_distributed():
    
    if not (request.vars.download or request.vars.view):
        return dict(result=[],sum_total=0) 
    
    result = []
    items = []
    colnames = ['Item Type', 'Count']
    gender = request.vars.gender

      
    if gender=='Male':   
        items.extend(ACTIVITIES_ITEMS_MALE)
    elif gender=='Female':        
        items.extend(ACTIVITIES_ITEMS_FEMALE)
    else:
        gender = None
        items.extend(ACTIVITIES_ITEMS_BOTH)
    
    activities = activities_query(type='Dressings', use_date_filters=True)
    activities.exclude(lambda r: r.is_no_show==True)
    
    #initialize the totals dict
    total = 0
    overall_total = 0
    totals_by_item = dict()
    for item in items:
        totals_by_item[item] = 0 
    
    for activity in activities:
        if gender and activity.gender!=gender:
            continue
        
        for item in items:
            nbr = activity.get(item)
            if nbr!=None:
                totals_by_item[item] += nbr
                total += nbr
    overall_total += total
    #display the items vertically
    for item in items:
        row = Storage()
        if item=='nbr_esteem_jewellery':
            row[colnames[0]] = 'DFS '+ item[4].capitalize() + item[5:10]+' '+item[11].capitalize()+item[12:]
            row[colnames[1]] = totals_by_item.get(item)
        else:
            row[colnames[0]] = item[4].capitalize() + item[5:] #remove nbr_ prefix and captitalize first letter only
            row[colnames[1]] = totals_by_item.get(item)
        result.append(row)
    
    #to display horizontally
    #result_row = Storage()
    #colanmes = []
    #for item in items:
    #    col_name = item[4].capitalize() + item[5:] #remove nbr_ prefix and captitalize first letter only
    #    colnames.append(col_name)
    #    result_row[col_name] = totals_by_item.get(item)
    #result.append(result_row)
    
    return view_or_download(result=result,colnames=colnames,sum_total=str(overall_total))

def volunteer_hours():

    if len(request.args):
        page = int(request.args[0])
    else: 
        page = 0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
    
    result = []
    colnames = ['volunteer', 'type', 'date', 'gender','total_time']

    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
    else:
        if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]
    
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result=[], page=page, items_per_page=items_per_page, colnames=colnames)
    
    activities = activities_query(use_date_filters=True, filters=[db.activities.person_type==PERSON_TYPE_VOLUNTEER])
    activities.exclude(lambda r: r.is_no_show==True)
    
    #going to do gender filter while looping instead of pushing down to db, to avoid building index just for reports
    gender = request.vars.gender
    if gender=='All':
        gender = None
    if request.vars.download:
        volunteers = queryr(db.people, [db.people.type==PERSON_TYPE_VOLUNTEER],show_deactivated=True)
    else:
        volunteers = queryr(db.people, [db.people.type==PERSON_TYPE_VOLUNTEER],show_deactivated=True, limitby=limitby)
    
    total_delta = timedelta(0)
    activity_list = []
    
    for activity in activities:
        
        if gender and not (activity.gender==gender or activity.gender=='Both'):
            continue
        
        volunteer = volunteers.find(lambda v: v.id==activity.person_id).first()
        #continue for non-volunteer activities (client and employee)
        if volunteer==None:
            continue
        
        start_time = parse_time(activity.start_time)
        end_time = parse_time(activity.end_time)
        if not start_time or not end_time:
            continue #in case the value in the db was empty or invalid 
        
        delta = end_time - start_time
        total_delta += delta #must be added after the is volunteer check
        result.append(Storage(volunteer=display_name(volunteer),type=activity.type,date=activity.date.strftime('%Y-%m-%d'),gender=activity.gender,total_time=str(delta)))
    return view_or_download(result=result, page=page, items_per_page=items_per_page, st_date=st_date,en_date=en_date,colnames=colnames, time_count=str(total_delta))

def employee_activities():

    if len(request.args):
        page = int(request.args[0])
    else: 
        page = 0
    items_per_page = PER_PAGE
    limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))

    st_date = request.vars.start_date if request.vars.start_date else None
    en_date = request.vars.end_date if request.vars.end_date else None
    if request.vars.view or request.vars.download:
        page = 0
        items_per_page = PER_PAGE
        limitby = ((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
        st_date = request.vars.start_date if request.vars.start_date else request.vars.st_date
        en_date = request.vars.end_date if request.vars.end_date else request.vars.en_date
    else:
        if len(request.args)>2:
            st_date=request.args[1]
            en_date=request.args[2]
    
    #check if the form was submitted. otherwise return empty result and show form 
    if not (request.vars.download or request.vars.view or request.args):
        return dict(result=[], page=page, items_per_page=items_per_page, total=0)
    
    #see if it is all, first visits, returning visits, or no shows 
    visit_filter = request.args(0)
    if visit_filter==FITTING_REPORTS.NO_SHOWS:
        return no_shows()
    
    colnames = ['activity_date', 'first_name', 'last_name', 'contact', 'activity_type', 'is_no_show', 'gender', 'start_time', 'end_time']        
    
    #fetch ALL records from the database initially
    #    date filters are not done up-front since we need to determine first time visit vs return visit BEFORE applying the date filters from the form
    #employees = db(db.people.type==PERSON_TYPE_EMPLOYEE).select()
    filters=[]
    filters.append(db.activities.person_type==PERSON_TYPE_EMPLOYEE)
    
    if request.vars.download:
        activities = activities_query(filters=filters, orderby=db.activities.date)
    else:
        activities = activities_query(filters=filters, orderby=db.activities.date, use_date_filters=True, limitby=limitby)

    if activities!=None:
        employees = db(db.people.type==PERSON_TYPE_EMPLOYEE).select()
    else:
        return dict(result=[], page=page, items_per_page=items_per_page, total=0)
    
    convert_start_date = time.strptime(request.vars.start_date,"%d-%m-%Y") if request.vars.start_date else None
    stt_date = time.strftime('%Y-%m-%d',convert_start_date) if convert_start_date else None

    convert_end_date = time.strptime(request.vars.end_date,"%d-%m-%Y") if request.vars.end_date else None
    enn_date = time.strftime('%Y-%m-%d',convert_end_date) if convert_end_date else None
    
    start_filter = parse_date(stt_date, as_datetime=False)
    end_filter = parse_date(enn_date, as_datetime=False)
    
    result = []
    #list_one = [,'nbr_makeup', 'nbr_esteem_jewellery','nbr_boots', 'nbr_underwear', 'nbr_bra',  'nbr_camisole','nbr_stocking']
    #Helper method for adding records to the result array based on form filters and type of report
    #def add_to_result(activity, employee):                   
    #going to do gender filter while looping instead of pushing down to db, to avoid building index just for reports
    gender = request.vars.gender
    if gender=='All':
        gender = None

    activities_dict = {}           

    person_set = set() 
    for activity_person in activities:
        person_set.add(activity_person.person_id)

    for person_id in person_set:
        person_activity_list = []
        for acts in activities:
            if person_id == acts.person_id:
                person_activity_list.append(acts)
                activities_dict[acts.person_id] = person_activity_list    
    
    #process employees one-by-one and get their activities.
    for employee in employees:
        
    
        #In memory filter of the activities using the dict rather than a db lookup for each client
        it_activities = activities_dict.get(employee.id, [])
        #it_activities = activities.exclude(lambda row: row.person_id==employee.id)
        #it_activities.exclude(lambda row: row.is_no_show==True)
        #visits = len(it_activities)
        for activity in it_activities:
            if gender and not (activity.gender==gender or activity.gender=='Both'):
                continue
            if employee.id in person_set:
                if not ((start_filter and activity.date<start_filter)
                or (end_filter and activity.date>end_filter)):
                    row = Storage()
                    row['activity_date'] = activity.date.strftime('%Y-%m-%d')
                    row['is_no_show'] = activity.is_no_show
                    row['activity_type'] = activity.type
                    row['start_time'] = activity.start_time  
                    row['end_time'] = activity.end_time
                    row['employee_id'] = employee.id
                    for k in employee:
                        row[k] = employee.get(k)
                        row['contact']=employee.get('mobile')
                        row['gender'] = activity.gender
                    result.append(row)
                #add_to_result(activity, employee)
            else:
                continue
    
    return view_or_download(result=result, page=page, items_per_page=items_per_page, st_date=st_date, en_date=en_date, colnames=colnames)

"""Helper methods from here down"""

"""
Reusable method for fetching activites based on the input date filters and other criteria
"""
def activities_query(type=None, filters=None, use_date_filters=False, orderby=None, limitby=None, client_fitting=False):
    if filters==None:
        filters=[]
 
    if type!=None:
        filters.append(db.activities.type==type)
    
    end_filter = None
    if use_date_filters: 
        if client_fitting==True:
            convert_start_date = time.strptime(request.vars.start_date,"%d-%m-%Y") if request.vars.start_date else None
            if not convert_start_date and request.vars.view:
                convert_start_date = time.strptime(request.vars.st_date,"%d-%m-%Y") if request.vars.st_date else None
            elif not convert_start_date and len(request.args)>3:
                convert_start_date = time.strptime(request.args[2],"%d-%m-%Y") if request.args[2] else None
            st_date = time.strftime('%Y-%m-%d',convert_start_date) if convert_start_date else None
        
        
            convert_end_date = time.strptime(request.vars.end_date,"%d-%m-%Y") if request.vars.end_date else None
            if not convert_end_date and request.vars.view:
                convert_end_date = time.strptime(request.vars.en_date,"%d-%m-%Y") if request.vars.en_date else None
            elif not convert_end_date and len(request.args)>3:
                convert_end_date = time.strptime(request.args[3],"%d-%m-%Y") if request.args[3] else None
            en_date = time.strftime('%Y-%m-%d',convert_end_date) if convert_end_date else None
        else:
            convert_start_date = time.strptime(request.vars.start_date,"%d-%m-%Y") if request.vars.start_date else None
            if not convert_start_date and request.vars.view:
                convert_start_date = time.strptime(request.vars.st_date,"%d-%m-%Y") if request.vars.st_date else None
            elif not convert_start_date and len(request.args)>2:
                convert_start_date = time.strptime(request.args[1],"%d-%m-%Y") if request.args[1] else None
            st_date = time.strftime('%Y-%m-%d',convert_start_date) if convert_start_date else None
        
        
            convert_end_date = time.strptime(request.vars.end_date,"%d-%m-%Y") if request.vars.end_date else None
            if not convert_end_date and request.vars.view:
                convert_end_date = time.strptime(request.vars.en_date,"%d-%m-%Y") if request.vars.en_date else None
            elif not convert_end_date and len(request.args)>2:
                convert_end_date = time.strptime(request.args[2],"%d-%m-%Y") if request.args[2] else None
            en_date = time.strftime('%Y-%m-%d',convert_end_date) if convert_end_date else None
        
        
        start_filter = parse_date(st_date, as_datetime=False)
        end_filter = parse_date(en_date, as_datetime=False)
        
        if start_filter:
            filters.append(db.activities.date>=start_filter)
        elif end_filter:
            filters.append(db.activities.date<=end_filter)
    logging.info(limitby)
    #run the query
    activities = queryr(db.activities, filters, show_deactivated=True, orderby=orderby, limitby=limitby)
    logging.info(len(activities))

    if end_filter:
        activities.exclude(lambda a: a.date>end_filter)
    
    return activities


"""
Reusable method for fetching any total records based on the input date filters and other criteria
"""
def total_query(resource, filters=None,limitby=None,e_date=None):
    
    if filters==None:
        filters = []
    
    convert_date = time.strptime(request.vars.effective_date,"%d-%m-%Y") if request.vars.effective_date else None
    #code for pagination
    if not convert_date and request.vars.view:
        convert_date = time.strptime(request.vars.e_date,"%d-%m-%Y") if request.vars.e_date else None
    if not convert_date:
        if len(request.args)> 1:
            e_date = request.args[1]
            if e_date != None:
                convert_date = time.strptime(e_date,"%d-%m-%Y") if e_date!=None else None
            else:
                pass
    date = time.strftime('%Y-%m-%d',convert_date) if convert_date else None
    effective_dttm = parse_date(date, as_datetime=True)
    
    if effective_dttm:
        effective_dttm += timedelta(days=1)
        filters.append(resource.created_on<=effective_dttm)
    
    #result = queryr(resource, filters, limitby=limitby)
    result = new_query(resource, filters, limitby=limitby) 
    return result

"""
Reusable method for fetching any 'new' records based on the input date filters and other criteria
"""
def new_query(resource, filters=None, limitby=None):
    if filters==None:
        filters = []
    
    convert_start_date = time.strptime(request.vars.start_date,"%d-%m-%Y") if request.vars.start_date else None
    # Code for pagination
    if not convert_start_date and request.vars.view:
        convert_start_date = time.strptime(request.vars.st_date,"%d-%m-%Y") if request.vars.st_date else None
    elif not convert_start_date and len(request.args)>2:
        convert_start_date = time.strptime(request.args[1],"%d-%m-%Y") if request.args[1] else None
    st_date = time.strftime('%Y-%m-%d',convert_start_date) if convert_start_date else None
    
    convert_end_date = time.strptime(request.vars.end_date,"%d-%m-%Y") if request.vars.end_date else None
    # Code for pagination
    if not convert_end_date and request.vars.view:
        convert_end_date = time.strptime(request.vars.en_date,"%d-%m-%Y") if request.vars.en_date else None
    elif not convert_end_date and len(request.args)>2:
        convert_end_date = time.strptime(request.args[2],"%d-%m-%Y") if request.args[2] else None
    en_date = time.strftime('%Y-%m-%d',convert_end_date) if convert_end_date else None
    
    start_filter = parse_date(st_date, as_datetime=True)
    end_filter = parse_date(en_date, as_datetime=True)
    
    if start_filter and end_filter:
        end_filter += timedelta(days=1)
        filters.append(resource.created_on>=start_filter)
        result = queryr(resource, filters, show_deactivated=True, limitby=limitby)
        result.exclude(lambda r: r.created_on>end_filter)
    elif start_filter:
        filters.append(resource.created_on>=start_filter)
        result = queryr(resource, filters, show_deactivated=True, limitby=limitby)
    elif end_filter:
        end_filter += timedelta(days=1)
        filters.append(resource.created_on<=end_filter)
        result = queryr(resource, filters, show_deactivated=True, limitby=limitby)
    else:
        result = queryr(resource, filters, show_deactivated=True, limitby=limitby)
    return result



def active_query(resource, filter=None,activation_type=None, limitby=None):
    if filter==None:
        filter = []
        
    result = []
    volunteer_id = []
    record_volunteer = []
    activation_type = activation_type
    
    convert_start_date = time.strptime(request.vars.start_date,"%d-%m-%Y") if request.vars.start_date else None
    if not convert_start_date and request.vars.view:
        convert_start_date = time.strptime(request.vars.st_date,"%d-%m-%Y") if request.vars.st_date else None
    elif not convert_start_date and len(request.args)>2:
        convert_start_date = time.strptime(request.args[1],"%d-%m-%Y") if request.args[1] else None
    st_date = time.strftime('%Y-%m-%d',convert_start_date) if convert_start_date else None
    
    convert_end_date = time.strptime(request.vars.end_date,"%d-%m-%Y") if request.vars.end_date else None
    if not convert_end_date and request.vars.view:
        convert_end_date = time.strptime(request.vars.en_date,"%d-%m-%Y") if request.vars.en_date else None
    elif not convert_end_date and len(request.args)>2:
        convert_end_date = time.strptime(request.args[2],"%d-%m-%Y") if request.args[2] else None
    en_date = time.strftime('%Y-%m-%d',convert_end_date) if convert_end_date else None
        

    start_filter = parse_date(st_date, as_datetime=True)
    end_filter = parse_date(en_date, as_datetime=True)
    result_date = db(db.activation_dates.record_type==activation_type).select()
    #result_volunteer = db(db.people.created_on<=end_filter).select()
    
    if start_filter and end_filter:
        if start_filter>request.now:
            result = queryr(resource, filter, limitby=limitby)
            return result
        #filter.append(resource.created_on<=end_filter)
        end_filter += timedelta(days=1)
        result_volunteer = queryr(resource, filter,show_deactivated=True, limitby=limitby)
        result_volunteer.exclude(lambda r: r.created_on>end_filter)
        for volunteer in result_volunteer:
            volunteer_id.append(volunteer.id)
            
        for x in result_date:
            record_volunteer.append(int(x.record_id))
            
        for volunteer in result_volunteer:
            if not volunteer.id==record_volunteer:
                volunteer.created_on = volunteer.created_on.date()
                if volunteer.organisation != None:
                    org = db(db.organisations.id==volunteer.organisation).select()
                    for y in org:
                        volunteer.organisation = y.name
                result.append(volunteer)
            elif volunteer.id==record_volunteer:
                for date in result_date:
                    if date.date>=start_filter and date.date<=end_filter:           
                        if date.de_activate=='activate' or date.de_activate=='deactivate':
                            volunteer.created_on = volunteer.created_on.date()
                            if volunteer.organisation != None:
                                org = db(db.organisations.id==volunteer.organisation).select()
                                for y in org:
                                    volunteer.organisation = y.name
                            result.append(volunteer)
                            break
                    elif date.date<=start_filter: #and volunteer.deactivated==False:
                        if date.de_activate=='activate' and date.de_activate!='deactivate':
                            volunteer.created_on = volunteer.created_on.date()
                            if volunteer.organisation != None:
                                org = db(db.organisations.id==volunteer.organisation).select()
                                for y in org:
                                    volunteer.organisation = y.name
                            result.append(volunteer)
                            break
    else:
        result = []
        result_volunteer = queryr(resource, filter, show_deactivated=True, limitby=limitby)
        for volunteer in result_volunteer:
            volunteer.created_on = volunteer.created_on.date()
            if volunteer.organisation != None:
                org = db(db.organisations.id==volunteer.organisation).select()
                for y in org:
                    volunteer.organisation = y.name
            result.append(volunteer)
    return result

def view_or_download(result, colnames, page=0, e_date=None, st_date=None, en_date=None, gnder=None, items_per_page=PER_PAGE, **kargs):
    if  request.vars.download:
        return report_download(result, colnames)
    else:
        logging.info(gnder)
        return dict(result=result,colnames=colnames, page=page, st_date=st_date, en_date=en_date, gnder=gnder, items_per_page=items_per_page,e_date=e_date, **kargs)

def report_download(result, colnames):
    import cStringIO
    stream = cStringIO.StringIO()
    render_report_csv(stream, result, colnames=colnames)
    filename = '%s-%s-%s.csv' % (request.function, request.args(0), request.now)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=%s' % filename
    return stream.getvalue()
