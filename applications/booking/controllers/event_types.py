###  Event Type Validations
db.event_types.name.requires=[IS_NOT_EMPTY(error_message='Type cannot be empty'), IS_NOT_IN_DB(db, 'event_types.name', error_message='Type already exists')]
db.event_types.color.requires=[IS_NOT_EMPTY(error_message='Color cannot be empty')]
resource=db.event_types

@auth.requires(has_auth)
def index():
    if not request.ajax:
        return dict()
    
    #get the listing before the insert since GAE doesn't always return the new row in the set 
    event_types = queryr(resource, orderby=resource.name) 
    
    form = new_event_type = None
    if can('create', entity):
        form = SQLFORM(resource)
        if form.accepts(request.post_vars, session, formname='create_form'):
            new_event_type = dict(id=form.vars.id, name=request.post_vars.name, color=request.post_vars.color)

    return dict(form=form, new_event_type=new_event_type, event_types=event_types)

@auth.requires(has_auth)
def update():
    id = request.args(0) or request.vars.type
    event_type = resource(id) or redirect(URL(c=entity,f='index'))

    form = SQLFORM(resource, event_type, deletable=False, submit_button='Update')
                        
    if form.accepts(request.vars,session):
        session.flash = dict(success=T('Event Type updated!'))
        redirect(URL(c=entity, f='index'))
    return dict(form=form)
