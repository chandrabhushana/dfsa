# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import logging
db.people.date_of_birth.requires = IS_NULL_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='Invalid date. Please enter date in dd-mm-yyyy format'))
db.people.date_trained.requires = IS_NULL_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='Invalid date. Please enter date in dd-mm-yyyy format'))
@auth.requires(auth.is_logged_in())
def index():
     if is_admin or is_employee or is_volunteer or is_client or is_agency:
        person = auth.user
        logging.info('person==============')
        logging.info(person)
        activities = db(db.activities.person_id==person.id).select(orderby=db.activities.date)
        response.view = 'people/view.html'
        return dict(person=auth.user,activities=activities,entity=entity_by_person_type(person.type),action=action)
     else:
        return dict ()

##Need the double underscore to prevent it from being exposed
def __profile():
    can_assign_orgs = can('assign-own', 'organisations') 
    if not can_assign_orgs:
        db.people.organisation.writable = False
         
    form = auth()
    person = auth.user
    if not can_assign_orgs:
        form.custom.widget.organisation = resource_field_by_id(db.organisations, 'name', auth.user.organisation, default='None')
    
    response.view = 'default/profile.html'
    return form
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires(boolean)
        @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    action = request.args(0)
    
    if action=='login' and auth.user:
        url = request.get_vars._next or request.post_vars._next or URL(c='default',f='index')
        if request.post_vars.email and request.post_vars.email!=auth.user.email:
            session.flash = dict(main_error='You are already logged in with %s on this browser. You can only have 1 login at a time per browser' % auth.user.email)
        else:
            session.flash = dict(main_notice='You are already logged in.')
        redirect(url)
    
    if action and action=='profile':
        form = __profile()
    else:
        form = auth()
    
    return dict(form=form)


def download():
    """
    allows downloading of uploaded files
    URL=/[app]/default/download/[filename]
    """
    return response.download(request,db)


#def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
#    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
