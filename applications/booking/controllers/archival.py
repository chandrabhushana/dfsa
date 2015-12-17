# coding: utf8
# try something like

import datetime
from google.appengine.api import taskqueue

from google.appengine.api import files
from google.appengine.api import app_identity
import urllib
import logging

GCS_API_ACCESS_ENDPOINT = 'https://storage.googleapis.com'
google_access_id = app_identity.get_service_account_name()

def index(): 
    return dict(message="hello from archival.py")

def archival_handler():
  
    if len(request.args):
       key=(request.args[0])
           
    adminDetails = queryr(db.people,[db.people.type=='Admin'])
    if adminDetails :
        logging.debug ('In try')
        receiverEmail = []
        receiverEmail = map(lambda row : row.email, adminDetails )
        strRecevEmail = ','.join(receiverEmail)
        
    else :
        logging.debug ('In except')
        receiverEmail = []
        strRecevEmail = mail.settings.sender
                
    taskqueue.add(url=URL('archival_process'),params=dict(key = key,receiverEmail=strRecevEmail),method='GET')
    
#    taskqueue.add(url=URL('archival_process'),method='GET')
       
       
    return 'Activities CSV file stored into cloud storage and mailed to the admin.'

    
def archival_process():
     
     from google.appengine.ext import db
     import cloudstorage
     from google.appengine.api import users
     from gluon.tools import Mail
   
    
     filter_date = datetime.date.today() + datetime.timedelta(-(365*(int(request.vars['key']))))
          
     result = db.GqlQuery("SELECT * FROM activities where created_on < :1",filter_date)
   
     
     filename = '/auktestapp_archival/Activities_'+str(datetime.datetime.today())
     gcs_file = cloudstorage.open(filename,mode='w',content_type='text/csv')
     File_headers = 'person_id,'+'type,'+'type_of_clothing,'+'date,'+'is_no_show,'+'clothing_size,'+'comments,'+'shoe_size,'+'start_time,'+'end_time,'+'gender,'+'image,'+'person_type,'+'pref_jobsearch,'+'pref_presentation,'+'pref_resume,'+'pref_computer,'+'pref_interview,'+'pref_workshops,'+'job_obtained,'+'pref_mentoring,'+'pref_other,'+'created_on,'+'created_by,'+'updated_on,'+'updated_by,'+'deactivated,'+'nbr_suits,'+'nbr_coats,'+'nbr_jackets,'+'nbr_shirts,'+'nbr_pants,'+'nbr_knitwear,'+'nbr_misc,'+'nbr_belts,'+'nbr_socks,'+'nbr_golfshirts,'+'nbr_tshirts,'+'nbr_shoes,'+'nbr_cufflinks,'+'nbr_ties,'+'nbr_skirts,'+'nbr_dresses,'+'nbr_softtops,'+'nbr_kneehighs,'+'nbr_scarves,'+'nbr_handbags,'+'nbr_makeup,'+'nbr_esteem_jewellery,'+'nbr_boots,'+'nbr_underwear,'+'nbr_bra,'+'nbr_camisole,'+'nbr_stocking'+'\n'
     gcs_file.write(File_headers)
    # Write into csv
     
     for record in result:
        temp = str(record.person_id)+','+str(record.type)+','+str(record.type_of_clothing)+','+str(record.date)+','+str(record.is_no_show)+','+str(record.clothing_size)+','+str(record.comments)+','+str(record.shoe_size)+','+str(record.start_time)+','+str(record.end_time)+','+str(record.gender)+','+str(record.image)+','+str(record.person_type)+','+str(record.pref_jobsearch)+','+str(record.pref_presentation)+','+str(record.pref_resume)+','+str(record.pref_computer)+','+str(record.pref_interview)+','+str(record.pref_workshops)+','+str(record.job_obtained)+','+str(record.pref_mentoring)+','+str(record.pref_other)+','+str(record.created_on)+','+str(record.created_by)+','+str(record.updated_on)+','+str(record.updated_by)+','+str(record.deactivated)+','+str(record.nbr_suits)+','+str(record.nbr_coats)+','+str(record.nbr_jackets)+','+str(record.nbr_shirts)+','+str(record.nbr_pants)+','+str(record.nbr_knitwear)+','+str(record.nbr_misc)+','+str(record.nbr_belts)+','+str(record.nbr_socks)+','+str(record.nbr_golfshirts)+','+str(record.nbr_tshirts)+','+str(record.nbr_shoes)+','+str(record.nbr_cufflinks)+','+str(record.nbr_ties)+','+str(record.nbr_skirts)+','+str(record.nbr_dresses)+','+str(record.nbr_softtops)+','+str(record.nbr_kneehighs)+','+str(record.nbr_scarves)+','+str(record.nbr_handbags)+','+str(record.nbr_makeup)+','+str(record.nbr_esteem_jewellery)+','+str(record.nbr_boots)+','+str(record.nbr_underwear)+','+str(record.nbr_bra)+','+str(record.nbr_camisole)+','+str(record.nbr_stocking)+'\n'
        
        gcs_file.write(temp)
            
        
     gcs_file.close()
     filename_mail = (filename.split("/")[2]).split("_")[0]
     
     
     #Calling the Sign url function with Expiration limit as 1 week
     signed_url = sign_url(filename, expires_after_seconds=604800)
     

     # Send the GCS file through mail
     mail.send(request.vars['receiverEmail'],
          'Activities Data Archival CSV details as on %s' %(datetime.datetime.today()),
          ('<html><p> Hi,</p>\
               <p>The Activities table has been archived and is stored.</p>\
               <p>Please click on the below link to download the file: <a href=%s>%s</a></p></html>' %(signed_url,filename_mail)))
    # Delete the archived records from the DB 
     result_del = result[0]
     result_del.delete()
     
     
def sign_url(gcs_filename, expires_after_seconds=60):

    from datetime import datetime,timedelta
    import time
    import base64
    import urllib
    from google.appengine.api import app_identity
    
    """ cloudstorage signed url to download cloudstorage object without login
        Docs : https://cloud.google.com/storage/docs/access-control?hl=bg#Signed-URLs
        API : https://cloud.google.com/storage/docs/reference-methods?hl=bg#getobject
    """
    
    method = 'GET'
   
    content_md5, content_type = None, None
    
    # expiration : number of seconds since epoch
    expiration_dt = datetime.utcnow() + timedelta(seconds=expires_after_seconds)
    expiration = int(time.mktime(expiration_dt.timetuple()))

    # Generate the string to sign.
    signature_string = '\n'.join([
        method,
        content_md5 or '',
        content_type or '',
        str(expiration),
        urllib.quote(gcs_filename)])

    signature_bytes = app_identity.sign_blob(signature_string)[1]
    
   # Set the right query parameters. we use a gae service account for the id
    query_params = {'GoogleAccessId': google_access_id,
                    'Expires': str(expiration),
                    'Signature': base64.b64encode(signature_bytes)}

    # Return the built URL.
    result = '{endpoint}{resource}?{querystring}'.format(endpoint=GCS_API_ACCESS_ENDPOINT,
                                                         resource=urllib.quote(gcs_filename),
                                                         querystring=urllib.urlencode(query_params))
    return result

def archival_handler_client():

    if len(request.args):
       key=(request.args[0])
      
    adminDetails = queryr(db.people,[db.people.type=='Admin'])
    if adminDetails :
        logging.debug ('In try')
        receiverEmail = []
        receiverEmail = map(lambda row : row.email, adminDetails )
        strRecevEmail = ','.join(receiverEmail)
        
    else :
        logging.debug ('In except')
        receiverEmail = []
        strRecevEmail = mail.settings.sender
                
    taskqueue.add(url=URL('archival_process_client'),params=dict(key = key,receiverEmail=strRecevEmail),method='GET')
   # archival_process_client()
    return 'Client CSV file stored into cloud storage and mailed to the admin.'
    
def archival_process_client():
    
    from google.appengine.ext import db
    import cloudstorage
    from google.appengine.api import users
    from gluon.tools import Mail
    from google.appengine.ext import deferred
    
    
    logging.debug ('In Archival ********************')
    
    
    filter_date = datetime.date.today() + datetime.timedelta(-(365*(int(request.vars['key']))))
    #filter_date = datetime.date.today() + datetime.timedelta(-(365*2))
    logging.debug(filter_date)
          
    result = db.GqlQuery("SELECT * FROM auth_user where type ='Client' and created_on < :1",filter_date)
    logging.debug(result.count())
    # Array to store the Client ID for fetching the Activities details
    clientIDArray = []
    
    
    # GCS file to store the Client details
    filename_client = '/auktestapp_archival/Clients_'+str(datetime.datetime.today())
    gcs_file_client = cloudstorage.open(filename_client,mode='w',content_type='text/csv')
    
    File_headers = 'id,'+'first_name,'+'last_name,'+'email,'+'password,'+'registration_key,'+'reset_password_key,'+'type,'+'mobile,'+'title,'+'street_addr,'+'suburb_addr,'+'city_addr,'+'postcode_addr,'+'type_of_job,'+'comments,'+'length_of_time_unemployed,'+'educational_level,'+'date_of_birth,'+'date_trained,'+'gender,'+'age_range,'+'ethnicity,'+'referral_contact_email,'+'medical_conditions,'+'contact_name,'+'contact_number,'+'second_contact_number,'+'organisation,'+'ttw_paid,'+'single_parent,'+'shoe_size,'+'clothing_size,'+'job_type,'+'pref_going_places_network,'+'pref_professional_womens_group,'+'pref_permission_to_photo,'+'pref_permission_to_follow_up,'+'pref_permission_to_invite_events,'+'pref_showroom,'+'pref_fitting,'+'pref_admin,'+'pref_police,'+'pref_children_check,'+'pref_induction,'+'pref_shadow,'+'pref_collection,'+'pref_donations,'+'pref_mentoring,'+'pref_careers,'+'pref_jobsearch,'+'pref_presentation,'+'pref_resume,'+'pref_computer,'+'pref_interview,'+'pref_workshops,'+'job_obtained,'+'pref_lifeskills,'+'pref_socialmedia,'+'pref_other,'+'created_on,'+'created_by,'+'updated_on,'+'updated_by,'+'deactivated'+'\n'
    
    gcs_file_client.write(File_headers)
    
   # logging.debug('In Client archival #############')
    for rec in result:
        #logging.debug(str(rec.key().id_or_name()))
        clientIDArray.append(rec.key().id_or_name())
        temp = str(rec.key().id_or_name())+','+str(rec.first_name)+','+str(rec.last_name)+','+str(rec.email)+','+str(rec.password)+','+str(rec.registration_key)+','+str(rec.reset_password_key)+','+str(rec.type)+','+str(rec.mobile)+','+str(rec.title)+','+str(rec.street_addr)+','+str(rec.suburb_addr)+','+str(rec.city_addr)+','+str(rec.postcode_addr)+','+str(rec.type_of_job)+','+str(rec.comments)+','+str(rec.length_of_time_unemployed)+','+str(rec.educational_level)+','+str(rec.date_of_birth)+','+str(rec.date_trained)+','+str(rec.gender)+','+str(rec.age_range)+','+str(rec.ethnicity)+','+str(rec.referral_contact_email)+','+str(rec.medical_conditions)+','+str(rec.contact_name)+','+str(rec.contact_number)+','+str(rec.second_contact_number)+','+str(rec.organisation)+','+str(rec.ttw_paid)+','+str(rec.single_parent)+','+str(rec.shoe_size)+','+str(rec.clothing_size)+','+str(rec.job_type)+','+str(rec.pref_going_places_network)+','+str(rec.pref_professional_womens_group)+','+str(rec.pref_permission_to_photo)+','+str(rec.pref_permission_to_follow_up)+','+str(rec.pref_permission_to_invite_events)+','+str(rec.pref_showroom)+','+str(rec.pref_fitting)+','+str(rec.pref_admin)+','+str(rec.pref_police)+','+str(rec.pref_children_check)+','+str(rec.pref_induction)+','+str(rec.pref_shadow)+','+str(rec.pref_collection)+','+str(rec.pref_donations)+','+str(rec.pref_mentoring)+','+str(rec.pref_careers)+','+str(rec.pref_jobsearch)+','+str(rec.pref_presentation)+','+str(rec.pref_resume)+','+str(rec.pref_computer)+','+str(rec.pref_interview)+','+str(rec.pref_workshops)+','+str(rec.job_obtained)+','+str(rec.pref_lifeskills)+','+str(rec.pref_socialmedia)+','+str(rec.pref_other)+','+str(rec.created_on)+','+str(rec.created_by)+','+str(rec.updated_on)+','+str(rec.updated_by)+','+str(rec.deactivated)+'\n'
        
        gcs_file_client.write(temp)

    gcs_file_client.close()
        
    for rec in result:
        # De-activating the Clients
        rec.deactivated = True
        rec.put()
        
        deactivate_reg = db.GqlQuery("SELECT * FROM registrations where person = :1",rec.key().id_or_name())
        for reg in deactivate_reg :
            event_unresigter = db.GqlQuery("SELECT * FROM events where __key__ = KEY('events', %s)" % str(reg.event))
            logging.debug('Event Count ****************')
            logging.debug(event_unresigter.count())
            # Updating the Event display name
            for event in event_unresigter :
                name_orig = event.display_name
                name = '('+rec.first_name+' '+rec.last_name.split()[0][0]+') '
                final_name = name_orig.replace(name,'')
                event.display_name = final_name
                if event.is_full:
                    event.is_full = False
                event.put()
            
            # Un-register Clients from the events
            reg.deactivated=True
            reg.put()

    # Delete the archived records from the DB 
    #result_del = result[0]
    #result_del.delete()
    
    filename = '/auktestapp_archival/Client-Activities_'+str(datetime.datetime.today())
    
    # Calling a Taskqueue to fetch the Activities details of the Archived Clients
    for client_id_grp in chunker(clientIDArray,90):
        str_client_id_grp = stringify(client_id_grp)
        taskqueue.add(url=URL('archival_process_client_act'),params=dict(client_id = str_client_id_grp,filename = str(filename)),method='GET')
       # taskqueue.add(url=URL('archival_process_client_act'),params=dict(client_id = str_client_id_grp),method='GET')

    strRecevEmail = request.vars['receiverEmail']
    # Taskqueue for sending the mail
    taskqueue.add(url=URL('mail_client'),params=dict(filename_act = str(filename),filename_client = str(filename_client),receiverEmail=strRecevEmail),method='GET')
    

def archival_process_client_act():

    import cloudstorage
    from google.appengine.ext import db

    client_id_grp = request.vars['client_id']
    filename_main = request.vars['filename']
    client_id_grp_arr = client_id_grp.split(', ')
   # logging.debug('Client Array string:::')
   # logging.debug(client_id_grp_arr)

    # File for storing the Client Activities in Cloud
    filename = '/auktestapp_archival/Client_Activities_temp'
    gcs_file_client_act = cloudstorage.open(filename,mode='w',content_type='text/csv')
    
    try:
        fp = cloudstorage.open(filename_main,mode='r')
        gcs_file_client_act.write(fp.read())

    except cloudstorage.NotFoundError:    
        File_headers = 'person_id,'+'type,'+'type_of_clothing,'+'date,'+'is_no_show,'+'clothing_size,'+'comments,'+'shoe_size,'+'start_time,'+'end_time,'+'gender,'+'image,'+'person_type,'+'pref_jobsearch,'+'pref_presentation,'+'pref_resume,'+'pref_computer,'+'pref_interview,'+'pref_workshops,'+'job_obtained,'+'pref_mentoring,'+'pref_other,'+'created_on,'+'created_by,'+'updated_on,'+'updated_by,'+'deactivated,'+'nbr_suits,'+'nbr_coats,'+'nbr_jackets,'+'nbr_shirts,'+'nbr_pants,'+'nbr_knitwear,'+'nbr_misc,'+'nbr_belts,'+'nbr_socks,'+'nbr_golfshirts,'+'nbr_tshirts,'+'nbr_shoes,'+'nbr_cufflinks,'+'nbr_ties,'+'nbr_skirts,'+'nbr_dresses,'+'nbr_softtops,'+'nbr_kneehighs,'+'nbr_scarves,'+'nbr_handbags,'+'nbr_makeup,'+'nbr_esteem_jewellery,'+'nbr_boots,'+'nbr_underwear,'+'nbr_bra,'+'nbr_camisole,'+'nbr_stocking'+'\n'
    
        gcs_file_client_act.write(File_headers) 
   
    # Fetching the Activities for the Archived Clients and archiving them
    for id in client_id_grp_arr:
       # logging.debug(id)
        activities_client = db.GqlQuery("SELECT * FROM activities where person_id = :1",int(id) )    
        for rec in activities_client:
          #  logging.debug('After query in loop ******') 
           # logging.debug(rec.type)
            logging.debug('Activities ###############')
            temp = str(rec.person_id)+','+str(rec.type)+','+str(rec.type_of_clothing)+','+str(rec.date)+','+str(rec.is_no_show)+','+str(rec.clothing_size)+','+str(rec.comments)+','+str(rec.shoe_size)+','+str(rec.start_time)+','+str(rec.end_time)+','+str(rec.gender)+','+str(rec.image)+','+str(rec.person_type)+','+str(rec.pref_jobsearch)+','+str(rec.pref_presentation)+','+str(rec.pref_resume)+','+str(rec.pref_computer)+','+str(rec.pref_interview)+','+str(rec.pref_workshops)+','+str(rec.job_obtained)+','+str(rec.pref_mentoring)+','+str(rec.pref_other)+','+str(rec.created_on)+','+str(rec.created_by)+','+str(rec.updated_on)+','+str(rec.updated_by)+','+str(rec.deactivated)+','+str(rec.nbr_suits)+','+str(rec.nbr_coats)+','+str(rec.nbr_jackets)+','+str(rec.nbr_shirts)+','+str(rec.nbr_pants)+','+str(rec.nbr_knitwear)+','+str(rec.nbr_misc)+','+str(rec.nbr_belts)+','+str(rec.nbr_socks)+','+str(rec.nbr_golfshirts)+','+str(rec.nbr_tshirts)+','+str(rec.nbr_shoes)+','+str(rec.nbr_cufflinks)+','+str(rec.nbr_ties)+','+str(rec.nbr_skirts)+','+str(rec.nbr_dresses)+','+str(rec.nbr_softtops)+','+str(rec.nbr_kneehighs)+','+str(rec.nbr_scarves)+','+str(rec.nbr_handbags)+','+str(rec.nbr_makeup)+','+str(rec.nbr_esteem_jewellery)+','+str(rec.nbr_boots)+','+str(rec.nbr_underwear)+','+str(rec.nbr_bra)+','+str(rec.nbr_camisole)+','+str(rec.nbr_stocking)+'\n'
                
            gcs_file_client_act.write(temp)
            
    gcs_file_client_act.close()
    
    temp_file = cloudstorage.open(filename,mode='r')
    main_file = cloudstorage.open(filename_main,mode='w',content_type='text/csv')
    main_file.write(temp_file.read())
    main_file.close()
    cloudstorage.delete(filename)
    
    # Delete the archived Activites records from the DB 
    #result_del = activities_client[0]
    #result_del.delete()
    
      
def mail_client():

    from gluon.tools import Mail
    
    filename_act = request.vars['filename_act']
    filename_client = request.vars['filename_client']
    
    filename_mail_act = (filename_act.split("/")[2]).split("_")[0]
    filename_mail_client = (filename_client.split("/")[2]).split("_")[0]
     
     
     #Calling the Sign url function with Expiration limit as 1 week
    signed_url_act = sign_url(filename_act, expires_after_seconds=604800)
    signed_url_client = sign_url(filename_client, expires_after_seconds=604800)
     

     # Send the GCS file through mail
    mail.send(request.vars['receiverEmail'],
          'Client Data Archival CSV details as on %s' %(datetime.datetime.today()),
          ('<html><p> Hi,</p>\
               <p>The Client data has been archived and is stored.</p>\
               <p>Please click on the link to download the Clients data: <a href=%s>%s</a></p>\
               <p>Please click on the link to download the Client Associated Activities data: <a href=%s>%s</a></p></html>' %(signed_url_client,filename_mail_client,signed_url_act,filename_mail_act)))


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

def stringify(client_id_grp):
    return ', '.join([str(x) for x in client_id_grp])
