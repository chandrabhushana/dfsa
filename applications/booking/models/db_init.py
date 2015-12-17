# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from wfs_utils import *

from gluon.tools import Mail, Auth
#from gluon.tools import Crud, Service, PluginManager #, prettydate

mail = Mail()                                  # mailer

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('google:datastore')              # connect to Google BigTable, optional DAL('gae://namespace')
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    mail.settings.server = 'gae'
    #mail.settings.sender = 'obs.brisbane@gmail.com'
    #mail.settings.sender = 'obs.mornington@gmail.com'
    #mail.settings.sender = 'obs.sydney@gmail.com'
    #mail.settings.sender = 'wfs.acn.development@gmail.com'
    mail.settings.sender = 'test.wfs.acn@gmail.com'
    
    
    #http_host = 'obs-bris.appspot.com'
    #http_host = 'brisdevapp2.appspot.com'
    #http_host = 'obs-mpfrankston.appspot.com'
    #http_host = 'obs-mprosebud.appspot.com'
    #http_host = 'syddevapp.appspot.com' 
    http_host = 'auktestapp.appspot.com' #in case behind a proxy
    #http_host = 'dfsdevapp.appspot.com' #in case behind a proxy
    #http_host = 'wfsdemoapp.appspot.com' #in case behind a proxy
    #http_host = 'mpdevapp.appspot.com' #in case behind a proxy
    #http_host = 'mp-devapp.appspot.com'
    #http_host = 'wfsdevapp.appspot.com' #in case behind a proxy
    #http_host = 'wfsdemoapp.appspot.com' #in case behind a proxy
    #http_host = 'dfsdevapp1.appspot.com'
    #http_host = 'mopdevapp.appspot.com' #in case behind a proxy
    #http_host = 'sydneydevapp.appspot.com' #in case behind a proxy
    #http_host = 'obs-melb2.appspot.com' #in case behind a proxy
    #http_host = 'brisdevapp.appspot.com'
    #http_host = 'dfs-syd.appspot.com'
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB
    
    mail.settings.server = 'smtp.gmail.com:587'  # your SMTP server
    mail.settings.sender = 'WFS Mailer <wfsdevmailer@gmail.com>'         # your email
    mail.settings.login = 'wfsdevmailer:mailerpoc'      # your credentials or None
    http_host = request.env.http_host


# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

auth = Auth(db)                                # authentication/authorization
#crud = Crud(db)                                # for CRUD helpers using auth
#service = Service()                            # for json, xml, jsonrpc, xmlrpc, amfrpc
#plugins = PluginManager()                      # for configuring plugins

auth.settings.long_expiration = 600
auth.settings.hmac_key = 'sha512:a39e6020-6e8c-4dbc-9516-2bbca42202d0'   # before define_tables()
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = True
auth.messages.verify_email = 'Click on the link http://'+http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'
auth.messages.registration_verifying = 'Account is not enabled'
auth.messages.registration_pending = 'Account is not enabled'
#auth.settings.allow_basic_login = True
auth.settings.create_user_groups = False
auth.settings.actions_disabled.append('register')
