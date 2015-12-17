#db.organisations.name.requires=[IS_NOT_EMPTY(error_message='Name cannot be empty'), IS_NOT_IN_DB(db, 'organisations.name', error_message='Name already exists'), IS_MATCH('[-a-z A-Z 0-9]+', strict=True, 
#error_message='This is not a valid name')] 

db.organisations.name.requires=[IS_NOT_EMPTY(error_message='Name cannot be empty'), IS_NOT_IN_DB(db, 'organisations.name', error_message='Name already exists'), IS_MATCH('[-&()!.,/\' a-z A-Z 0-9]+', strict=True, error_message='This is not a valid name')]

db.organisations.street_addr.requires=[IS_NOT_EMPTY(error_message='Street Address cannot be empty')]
#db.organisations.postcode_addr.requires=[IS_NOT_EMPTY(error_message='Postcode cannot be empty')]
db.organisations.postcode_addr.requires=IS_NULL_OR(IS_MATCH('^[ 0-9 ]+$', error_message='This is not a valid Postcode!'))

is_owner = lambda org: org.id==auth.user.organisation

@auth.requires(has_auth)
def index():
    
    if len(request.args):
        page = int(request.args[0])
    else:
        page = 0
    items_per_page=49
    #if page==0:
    limitby=((page*items_per_page)+page,(page+1)*items_per_page+(page+1))
    #else:
        #limitby=((page*items_per_page),(page+1)*items_per_page+page)
    
    
    #if request.vars.name or request.vars.abn:
    if request.vars.name :
        orgs = list_organisations()
        orgs = orgs.find(lambda org:(
                            lower_or(request.vars.name) in org.name.lower()))
                           # & (lower_or(request.vars.abn) in org.abn.lower()))
   # elif (request.vars.name=='' and request.vars.abn=='')or len(request.args)>0:
    elif (request.vars.name=='' )or len(request.args)>0:
        orgs = list_organisations(limitby=limitby)
    else:
        orgs=None
    return dict(organisations=orgs,page=page,items_per_page=items_per_page)

@auth.requires(has_auth)
def create():
    form = SQLFORM(db.organisations)
    if form.accepts(request.post_vars, session, onvalidation = organisation_processing):
        new_id = str(form.vars.id)
        session.flash = T('Organisation created successfully')
        redirect(URL(c=entity, f='view', args=new_id))
    elif form.errors:
        response.flash = T("Organisation details are invalid")
    
    return dict(form=form)

@auth.requires(has_auth)
def view():
    id = request.args(0) or request.vars.org
    organisation = db.organisations(id) or redirect(URL(c=entity,f='index'))
    redirect_if_not_authorized_on(is_owner(organisation))
    can('activate', entity) or redirect_if_deactivated(organisation)
    return dict(organisation=organisation)

@auth.requires(has_auth)
def update():
    id = request.args(0) or request.vars.org
    organisation = db.organisations(id) or redirect(URL(c=entity,f='index'))
    redirect_if_not_authorized_on(is_owner(organisation))
    redirect_if_deactivated(organisation)
    form = SQLFORM(db.organisations, organisation)
    if form.accepts(request.post_vars, session, onvalidation = organisation_processing):
        session.flash = T('Organisation successfully updated')
        redirect(URL(c=entity, f='view', args=organisation.id))
    elif form.errors:
        response.flash = T("Organisation details are invalid")
    
    return dict(organisation=organisation, form=form)

### Organisations Utils
def list_organisations(filters=[], select=True, limitby=None, orderby=db.organisations.name):
    show_deactivated = True if can('activate', entity) else False
    return queryr(db.organisations, filters, show_deactivated, select, orderby, limitby=limitby)
def organisation_processing(form):
    id = request.args(0) or request.vars.org
    referral_agency_list = ['is_disability_ref','is_jobservice_aus_ref','is_community_ref','is_education_ref','is_dept_employment','is_dept_corrective','is_job_placement_service','is_work_income','other_ref']
    sponsor_list = ['is_in_kind_doanations','is_financial_sponsor','is_volunteer_sponsor','other_sponsor']
    if form.vars.organisations_types == "Referral Organisation":
        for y in sponsor_list:
            form.vars.y = False
        form.vars.other_sponsor = 'None'
    if form.vars.organisations_types == "Sponsor":
        for y in referral_agency_list:
            form.vars.y = False
        form.vars.other_ref = 'None'
