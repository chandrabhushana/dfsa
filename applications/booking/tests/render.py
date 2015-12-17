import re, os, sys

"""
Copying the web2py render methods in order to have better error message 
"""
def render(response, *a, **b):
    
    #from compileapp import run_view_in
    if len(a) > 2:
        raise SyntaxError, 'Response.render can be called with two arguments, at most'
    elif len(a) == 2:
        (view, response._vars) = (a[0], a[1])
    elif len(a) == 1 and isinstance(a[0], str):
        (view, response._vars) = (a[0], {})
    elif len(a) == 1 and hasattr(a[0], 'read') and callable(a[0].read):
        (view, response._vars) = (a[0], {})
    elif len(a) == 1 and isinstance(a[0], dict):
        (view, response._vars) = (None, a[0])
    else:
        (view, response._vars) = (None, {})
    response._vars.update(b)
    
    response._view_environment.update(response._vars)
    #if view:
    #    print 'hello'
    #    (obody, oview) = (response.body, response.view)
    #(response.body, response.view) = (cStringIO.StringIO(), view)
    #print response.body
    import cStringIO
    response.body = cStringIO.StringIO()
    run_view_in(response._view_environment)
    #    page = response.body.getvalue()
    #response.body.close()
    #    (response.body, response.view) = (obody, oview)
    #else:
    #    print 'world'
    #    run_view_in(response._view_environment)
    page = response.body.getvalue()
    
    #custom mod. clean up the response view env after use 
    for k in response._vars:
        del response._view_environment[k] 
    return page

from template import parse_template
def run_view_in(environment):
    """
    Executes the view for the requested action.
    The view is the one specified in `response.view` or determined by the url
    or `view/generic.extension`
    It tries the pre-compiled views_controller_function.pyc before compiling it.
    """
    from http import HTTP
    import rewrite
    
    request = environment['request']
    response = environment['response']
    folder = request.folder
    path = os.path.join(folder, 'compiled')
    badv = 'invalid view (%s)' % response.view
    patterns = response.generic_patterns or []
    regex = re.compile('|'.join(fnmatch.translate(r) for r in patterns))
    short_action =  '%(controller)s/%(function)s.%(extension)s' % request
    allow_generic = patterns and regex.search(short_action)
    
    if not isinstance(response.view, str):
        ccode = parse_template(response.view, os.path.join(folder, 'views'), context=environment)
        restricted(ccode, environment, 'file stream')
    elif os.path.exists(path):
        x = response.view.replace('/', '_')
        files = ['views_%s.pyc' % x]
        if allow_generic:
            files.append('views_generic.%s.pyc' % request.extension)
        # for backward compatibility
        if request.extension == 'html':
            files.append('views_%s.pyc' % x[:-5])
            if allow_generic:
                files.append('views_generic.pyc')
        # end backward compatibility code
        for f in files:
            filename = os.path.join(path,f)
            if os.path.exists(filename):
                code = read_pyc(filename)
                restricted(code, environment, layer=filename)
                return
        raise HTTP(404, rewrite.thread.routes.error_message % badv, web2py_error=badv)
    else:
        filename = os.path.join(folder, 'views', response.view)
        if not os.path.exists(filename) and allow_generic:
            response.view = 'generic.' + request.extension
            filename = os.path.join(folder, 'views', response.view)
        if not os.path.exists(filename):
            raise HTTP(404, rewrite.thread.routes.error_message % badv, web2py_error=badv)
        layer = filename
        #if is_gae:
        #    ccode = getcfs(layer, filename,
        #                   lambda: compile2(parse_template(response.view,
        #                                    os.path.join(folder, 'views'),
        #                                    context=environment),layer))
        #else:
        ccode = parse_template(response.view, os.path.join(folder, 'views'), context=environment)
        restricted(ccode, environment, layer)

def restricted(code, environment={}, layer='Unknown'):
    """
    runs code in environment and returns the output. if an exception occurs
    in code it raises a RestrictedError containing the traceback. layer is
    passed to RestrictedError to identify where the error occurred.
    """
    environment['__file__'] = layer
    try:
        #import types
        #if type(code) == types.CodeType:
        #    ccode = code
        #else:
        ccode = compile2(code,layer)
        exec ccode in environment
    #except HTTP:
    #    raise
    except Exception, error:
        raise Exception(layer, error)
        #raise error
        # XXX Show exception in Wing IDE if running in debugger
        #if __debug__ and 'WINGDB_ACTIVE' in os.environ:
        #    etype, evalue, tb = sys.exc_info()
        #    sys.excepthook(etype, evalue, tb)
        #raise RestrictedError(layer, code, '', environment)

def compile2(code,layer):
    """
    The +'\n' is necessary else compile fails when code ends in a comment.
    """
    return compile(code.rstrip().replace('\r\n','\n')+'\n', layer, 'exec')
