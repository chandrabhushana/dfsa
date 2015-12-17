from __future__ import with_statement
from google.appengine.api import files
from google.appengine.ext import blobstore
from datetime import datetime, date
#from google.appengine.api import userswith 
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.api import mail
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

import logging
import os
import urllib

def register():
    from datetime import date
    global event_id
    logging.info('Schedular register function started==========================')
    event_detail = queryr(db.events)
    #logging.info(event_detail)
    logging.info(date.today())
    for events in event_detail:
        event_date = events.date
        #logging.info('event_date')
        #logging.info(event_date)
        if event_date >= date.today():
           logging.info('Schedular register function date comparsion start')
           logging.info(event_date)
           event_name=events.name
           logging.info('event_name===========')
           logging.info(event_name)
           event_id=events.id
           logging.info('event_id===========')
           logging.info(event_id)
           event_start=events.start_time
           logging.info('event_start===========')
           logging.info(event_start)
           event_end=events.end_time
           logging.info('event_end===========')
           logging.info(event_end)
           registrations_detail = queryr(db.registrations)
           #logging.info(registrations_detail)
           for registrations in registrations_detail:
               registration_event = registrations.event
               registrations_person = registrations.person
               if event_id == registration_event:
                   logging.info('Getting registrationsddata registration_event===========')
                   logging.info(registration_event)
                   logging.info('Getting registrationsddata registrations_person===========')
                   logging.info(registrations_person)
                   user_details= queryr(db.auth_user, [db.people.type==PERSON_TYPE_CLIENT])
                   #logging.info(user_details)
                   for user in user_details:
                       user_id = user.id
                       if registrations_person == user_id:
                        logging.info('user_id====================') 
                        logging.info(user_id)
                        auth_email = user.email
                        logging.info('auth_email====================')
                        logging.info(auth_email)
                        user_type = user.type
                        logging.info('user_type====================')
                        logging.info(user_type)
                        logging.info(events.name)
                        logging.info(events.start_time)
                        logging.info(events.end_time)
                        logging.info(events.date.strftime('%d-%m-%Y'))
                        mail.send_mail(sender="obs.mornington@gmail.com",to=auth_email,subject = '%s %s %s (Contact Number: %s) has been registered for event \'%s\' %s - %s, %s'%(user.type,user.first_name,user.last_name,user.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')),body="""You has been register for above mentioned Event """)
                        #mail.send(to=auth_email, subject='Event Upadates', message="You have an event")'''
                        logging.info('Mail sent====================')
                        #mail.send(to = auth_email, subject = '%s %s %s (Contact Number: %s) has been registered for event \'%s\' %s - %s, %s'%(user.type,user.first_name,user.last_name,user.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')), message = '%s %s %s (Contact Number: %s) has been registered for event \'%s\' %s - %s, %s'%(user.type,user.first_name,user.last_name,user.mobile,events.name,events.start_time,events.end_time,events.date.strftime('%d-%m-%Y')))
                              
                        logging.info('Schedular register function date comparsion end=========')
    logging.info('Schedular register function end==========================')