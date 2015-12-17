def li_link(text,c,f,verb=None,entity=None,_class=None,args=None,check_auth=True):
    verb = verb or f
    entity = entity or c
    if check_auth and not can(verb, entity): 
        return ''
    else:
        return LI(A(text,_href=URL(c=c,f=f,args=args)),_class=_class)

def link(text,f=None,args=[],c=None,e='',vars={},_class='',_onclick=None, check_auth=False):
    c = c or entity
    f = f or action
    if check_auth and not can(f,c):
        return ''
    else:
        return SPAN(A(text,_class=_class,_onclick=_onclick,_href=URL(r=request,c=c,f=f,extension=e,args=args,vars=vars)))

def button(text,f=None,args=[],c=None,e='',vars={},_class='button',_onclick=None, check_auth=False):
    return link(text,f,args,c,e,vars,_class,_onclick,check_auth)

def deactivate_link(text='Deactivate',c='deactivate',f=request.controller,e='',args=[],vars={},_onclick=''):
    return SPAN('[',A(text, _class='deactivate', _onclick=_onclick, _href=URL(r=request,c=c,f=f,extension=e,args=args,vars=vars)),']')

def deactivate_button(text='Deactivate',c='deactivate',f=request.controller,e='',args=[],vars={},_onclick=None, check_auth=True,_class='deactivate button'):
    if check_auth and not can(c,f):
        return ''
    else:
        return SPAN(A(text,_class=_class,_onclick=_onclick, _href=URL(r=request,c=c,f=f,extension=e,args=args,vars=vars)))
##Rohit Added Here
def deactivate_event_button(text='Deactivat Event',c='deactivate',f=request.controller,e='',args=[],vars={},_onclick=None, check_auth=True):
    if check_auth and not can(c,f):
        return ''
    else:
        return SPAN(A(text,_class='deactivate_event button',_onclick=_onclick, _href=URL(r=request,c=c,f=f,extension=e,args=args,vars=vars)))

def activate_button(text='Activate',c='activate',f=request.controller,e='',args=[],vars={},_onclick=None, check_auth=True):
    if check_auth and not can(c,f):
        return ''
    else:
        return SPAN(A(text,_class='activate button',_onclick=_onclick, _href=URL(r=request,c=c,f=f,extension=e,args=args,vars=vars)))

def stylesheet_rel(file, path='css', media='all'):
    scr = URL(request.application, 'static', path + '/' + file )
    return XML('<link rel="stylesheet" type="text/css" href="' + scr + '" media="' + media + '" />')

def javascript_rel(file, path='js'):
    scr = URL(request.application, 'static', path + '/' + file ) 
    return XML('<script type="text/javascript" src="' + scr + '"></script>')

def sticky_val(name):
    return request.vars.get(name) or ''

def required_message():
    return XML('<span class="required-message">(<span class="m">*</span>) required field</span>')

def required_indicator(required):
    return XML('<span class="m">*</span> ') if required else '' 

def form_row(form, field, label=None, mandatory=False):
    field_label = label or  form.custom.label[field]
    label_prefix = str(SPAN('* ', _class='m')) if mandatory else '' 
    label = XML(label_prefix + field_label + ':')
    return TR(TD(label, _class='w2p_fl label', _for=field),
              TD(form.custom.widget[field], _class='w2p_fw'),
              TD(_class='w2p_fc'),
              _id=field + '__row')

def event_vars():
    return subdict(request.vars, ['type', 'event', 'person', 'slots'])

def event_vars_wo_id():
    return subdict(request.vars, ['type', 'client'])

def redirect_if_deactivated(resource):
    if resource.deactivated and not request.vars.show_deactivated!=None:
        session.flash = dict(error='Selected resource is no longer active')
        redirect(URL(c=entity,f='index'))
