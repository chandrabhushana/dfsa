import unittest
import gluon
import re

class TestBase(unittest.TestCase):
    
    global appname
    appname = 'booking'
    
    def assertInHtml(self, str):
        self.assertTrue(str in self.html, 'Didn\'t find ' + str)
    
    def assertNotInHtml(self, str):
        self.assertFalse(str in self.html, 'Shouldn\'t have found ' + str)
    
    def assertNoInternalErrors(self):
        self.assertFalse('Internal Error' in self.html)
    
    def assert_not_authorized(self, callable=None):
        if not self:
            self = klass
        if not callable:
            callable=function
        self.assert_redirect(callable, '/user/not_authorized' % globals())
    
    def assert_redirect(self, callable, url=None, c=None, f=None, a=None):
        if c==None: #since '' is false
            c = self.request.controller
        if c=='default':
            c = ''
        if f==None or f=='index':
            f=''
        else:
            f='/' + f
        a = a or ''
        a = '/' + a if a else ''
        url = url or '/' + c + f + a
        
        try:
            resp = callable()
            
            if 'form' in resp and resp['form'].errors:
                self.fail('%s expected redirect but form had errors: \n%s' % (callable.__name__, resp['form'].errors))
            elif 'errors' in resp:
                self.fail('%s did not redirect. Error: \n%s' % (callable.__name__, resp.errors))
            else:
                self.fail('%s did not redirect. Resp: \n%s' % (callable.__name__, str(resp)))
        
        except gluon.http.HTTP, e:
            if url=='/':
                self.assertTrue(url==e.headers['Location'],
                        'Wrong redirection url on %s() : actual="%s" expected="%s"' %
                        (callable.__name__, e.headers['Location'],url))
            else:
                self.assertTrue(re.match(url, e.headers['Location']),
                        'Wrong redirection url on %s() : actual="%s" expected="%s"' %
                        (callable.__name__, e.headers['Location'],url))
        else:
            self.fail('%s should raise an HTTP exception\n%s' % (callable.__name__, e))
        