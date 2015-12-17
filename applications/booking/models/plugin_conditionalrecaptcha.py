MAX_LOGIN_FAILURES = 3
RECAPTCHA_PUBLIC_KEY = '6LdlzcgSAAAAANCcnBVffosuuFqcAYEn_-N3WsQG'
RECAPTCHA_PRIVATE_KEY = '6LdlzcgSAAAAAMROchUCWzYRLObUoRXhwc58qN4w'
##puk:'6LdVzMgSAAAAAEgYFvMgY6Me_G35sJSn_b2hK-I5'
##prik:'6LdVzMgSAAAAAAb8o38hyhFKcO5llgeOTBqCnT3j'
def _():
    from gluon.tools import Recaptcha
    key = 'login_from:%s' % request.env.remote_addr
    num_login_attempts = cache.ram(key,lambda:0,None)
    if num_login_attempts >= MAX_LOGIN_FAILURES:
        auth.settings.login_captcha = Recaptcha(
           request,RECAPTCHA_PUBLIC_KEY,RECAPTCHA_PRIVATE_KEY,error_message='Incorrect words entered. Enter both words, separated by a space',label='Type the words')
    def login_attempt(form,key=key,n=num_login_attempts+1):
        cache.ram(key,lambda n=n:n,0)
    def login_success(form,key=key):
        cache.ram(key,lambda:0,0)
    auth.settings.login_onvalidation.append(login_attempt)
    auth.settings.login_onaccept.append(login_success)
_()
