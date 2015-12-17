#####################################################################################
###This file contains table specific util methods to select/delete/update events
#####################################################################################

### Registration Utils (shared by Events)
def count_registrations_by_event(event_id, type=None):
    return len(registrations_by_event(event_id, type=type, push_down_deactivated=False))

def registrations_by_event(event_id, select=True, show_deactivated=False, type=None, push_down_deactivated=False):
    filters = [db.registrations.event==event_id]
    if type:
        filters.append(db.registrations.type==type)
    return queryr(db.registrations, filters, show_deactivated, select, orderby=None, push_down_deactivated=push_down_deactivated)

def registrations_by_person(person_id, select=True, show_deactivated=False, push_down_deactivated=False):
    filters = [db.registrations.person==person_id]
    return queryr(db.registrations, filters, show_deactivated, select, orderby=None, push_down_deactivated=push_down_deactivated)

def apply_filters(set, filters):
    for filter in filters:
        if filter:
            set = set(filter)
    return set

def queryr(resource, filters=None, show_deactivated=False, select=True, orderby=None, push_down_deactivated=True, cache=None, limitby=None):
    if filters==None:
        filters=[]
    
    if not show_deactivated and push_down_deactivated:
        filters.append((resource.deactivated==False))
    
    if len(filters)==0:
        set = db(resource.id>0)
    else:
        #in case the first filter is None, default back to id>0
        f1 = filters.pop() or (resource.id>0)
        set = db(f1)
        set = apply_filters(set, filters)
    
    if not select: 
        return set
    rows = set.select(limitby=limitby, orderby=orderby, cache=cache)

    if not show_deactivated and not push_down_deactivated:
        rows = rows.exclude(lambda row: row.deactivated==False)  
    return rows

def resource_by_id(resource, id, default=None, show_deactivated=False):
    if id==None:
        return default
    filters = [resource.id==id]
    rows = queryr(resource, filters, show_deactivated=show_deactivated, select=True)
    return rows.first() if len(rows)>0 else default

def resource_field_by_id(resource, field, id, default=None):
    rec = resource_by_id(resource, id, show_deactivated=True)
    return rec.get(field) if rec else default

def list_people(type=None, filters=[], show_deactivated=False, select=True, orderby=None,limitby=None):
    if type:
        filters.append((db.people.type==type))
    show_deactivated=True if is_admin else False

    return queryr(db.people, filters, show_deactivated, select, orderby, limitby=limitby)
