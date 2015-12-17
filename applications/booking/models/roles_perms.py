"""
Moved this to its own file for the controller tests to be able to re-execute it after changing a global var

'action' means user can perform that action on some/any, but maybe not all
'action-all' means user can perform that action on all entities, regardless of relationship
if user has 'action' permission, but not 'action-all', then 'owner' should be true  
"""
global is_admin, is_employee, is_agency, is_client, is_volunteer

permissions = {'clients': {
                      'view': is_admin or is_agency or is_employee or is_volunteer, #client views themselves through default/index, not through clients/view
                      'view-all': is_admin or is_employee or is_volunteer, #client can only view self. third-parties can view by org
                      'index': is_admin or is_agency or is_employee or is_volunteer,
                      'create': is_admin or is_agency or is_employee,
                      'update': is_admin or is_agency or is_employee, #clients can update themselves through default/user/profile, not through clients/update
                      'update-all': is_admin or is_employee, #third_party can only edit by org
                      'activate': is_admin,
                      'deactivate': is_admin or is_employee,
                      'disable_login': is_admin or is_employee,
                      'enable_login': is_admin or is_employee,
                      },
               'employees': {
                      'view': is_admin or is_employee,
                      'view-all': is_admin or is_employee,
                      'index': is_admin or is_employee,
                      'create': is_admin or is_employee,
                      'update': is_admin,
                      'update-all': is_admin,
                      'activate': is_admin,
                      'deactivate': is_admin or is_employee,
                      'disable_login': is_admin or is_employee,
                      'enable_login': is_admin or is_employee,
                      },
               'volunteers': {
                      'view': is_admin or is_employee, #volunteers view themselves through default/index, not volunteers/view
                      'view-all': is_admin or is_employee,
                      'index': is_admin or is_employee,
                      'create': is_admin or is_employee,
                      'update': is_admin or is_employee,
                      'update-all': is_admin or is_employee, #volunteers update themselves through default/user/profile, not volunteers/update
                      'delete': is_admin,
                      'activate': is_admin,
                      'deactivate': is_admin or is_employee,
                      'disable_login': is_admin or is_employee,
                      'enable_login': is_admin or is_employee,
                      },
               'agencies': {
                      'view': is_admin or is_employee or is_agency,
                      'view-all': is_admin or is_employee, #third-parties can only view by same org
                      'index': is_admin or is_employee or is_agency,
                      'create': is_admin or is_employee,
                      'update': is_admin or is_employee, #third-parties can update themselves through default/user/profile
                      'update-all': is_admin or is_employee,
                      'activate': is_admin,
                      'deactivate': is_admin or is_employee,
                      'disable_login': is_admin or is_employee,
                      'enable_login': is_admin or is_employee,
                      },
               'organisations': {
                      'view': is_admin,
                      'view-all': is_admin,
                      'index': is_admin,
                      'create': is_admin,
                      'update': is_admin,
                      'update-all': is_admin,
                      'activate': is_admin,
                      'deactivate': is_admin or is_employee,
                      'assign': is_admin or is_employee,
                      'assign-own': is_admin,
                      
                      },
               'admin': {
                         'index': is_admin,
                         'update': is_admin,
                         'view-all': is_admin,
                         'assign-own': is_admin,
                         },
               'activities': {
                      'view': auth.is_logged_in(), #gives view-self automatically
                      'view-for-all': is_admin or is_employee,
                      'view-for-all-clients': is_volunteer,
                      'view-for-clients-by-org': is_agency,
                      'create': is_admin or is_employee or is_volunteer,
                      'create-for-all-clients': is_volunteer,
                      'create-for-all': is_admin or is_employee,
                      'update': is_admin or is_employee or is_volunteer,
                      'update-for-all-clients': is_volunteer,
                      'update-for-all': is_admin or is_employee,
                      'activate': is_admin,
                      'deactivate': is_admin,
                      },
               'event_types': {
                      'index': auth.is_logged_in(),
                      'create': is_admin,
                      'update': is_admin,
                      'activate': is_admin,
                      'deactivate': is_admin,
                      },
               'events': {
                      'index': auth.is_logged_in(),
                      'list': auth.is_logged_in(),
                      'view': auth.is_logged_in(),
                      'create': is_admin or is_employee,
                      'update': is_admin or is_employee,
                      'activate': is_admin,
                      'deactivate': is_admin or is_employee,
                      },
               'registrations': {
                      'index': auth.is_logged_in(),
                      'manage': auth.is_logged_in(), #read-only view
                      'manage-others': is_admin or is_agency or is_employee,
                      #'manage-self': is_employee, #will be overriden by manage-others anyways 
                      'manage-all': is_admin  or is_employee,
                      },
               'reports': {
                      'index': is_admin,
                      }
               }

def can(verb, entity):
    try:
        return permissions[entity][verb]
    except:
        #print 'Failed to load %s-%s' % (entity,verb)
        return False

entity=request.controller
action=request.function
has_auth = can(action, entity)

def redirect_if_not_authorized_on(owner, e=entity, a=action):
    if not (can(a + '-all', e) or owner):
        redirect(URL(c='default',f='user',args='not_authorized'))
