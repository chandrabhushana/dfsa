# coding: utf8
# try something like

#from archival import *
import logging
from google.appengine.api import taskqueue
from google.appengine.api import files
from google.appengine.api import app_identity
import urllib

GCS_API_ACCESS_ENDPOINT = 'https://storage.googleapis.com'
google_access_id = app_identity.get_service_account_name()


def index(): return dict(message="hello from report_taskqueue.py")


def client_activities_tq():

    from google.appengine.ext import db
    import cloudstorage
    from gluon.tools import Mail
    #import datetime 
   # from datetime import datetime, date, time
    from datetime import date, time
    import time
    
    logging.debug('Inside TQ $$$$$$$$$$$$$$$$$$$')
    start_date = request.vars['start_date']
    end_date = request.vars['end_date']
    gender = request.vars['gender']
    strRecevEmail = request.vars['receiverEmail']
    max_count = int(request.vars['max_count'])
    fetch_records = int(request.vars['fetch_records'])
    
    if request.vars['cursor']:
        mycursor = request.vars['cursor']
    else:
        mycursor = None
    if request.vars['filename']:
        filename = request.vars['filename']
    else:
        filename = '/auktestapp_report/Client-Activities-Report_'+str(datetime.datetime.today())
    
    start_bol = end_bol = True
    
    if start_date=='None':
        start_bol = False
        start_filter ='None'
    else:
       temp_start_date = start_date.split("-")
       start_filter = datetime.datetime(int(temp_start_date[0]),int(temp_start_date[1]),int(temp_start_date[2].split(" ")[0]))
    
    if end_date=='None':
        end_bol = False
        end_filter ='None'
    else:
        #end_filter = datetime.strptime(end_date,'%Y-%m-%d')
        temp_end_date = end_date.split("-")
        end_filter = datetime.datetime(int(temp_end_date[0]),int(temp_end_date[1]),int(temp_end_date[2].split(" ")[0]))
    
    gender_bol = True
    if gender=='All':
        gender_bol = False
    
    if  gender_bol:
        # Query to fetch all Clients
        clients = db.GqlQuery("SELECT * FROM auth_user where type ='Client' and gender = :1 ",gender)
       
    else:
        clients = db.GqlQuery("SELECT * FROM auth_user where type ='Client' ")
       
    max_count
    
    #logging.debug(query)   
    # Fetching Clients data in parts
    if mycursor:
        clients_data = clients.with_cursor(mycursor).fetch(300)
        
    else:
        clients_data = clients.fetch(300)
    
    fetch_records = fetch_records + 300
   # Temp File for storing the Client Activities in Cloud
    filename_temp = '/auktestapp_report/Client_Activities_temp'
    gcs_file_temp = cloudstorage.open(filename_temp,mode='w',content_type='text/csv')
    
   # filename = '/preprod_archival/Client-Activities-Report_'+str(datetime.today())
   # gcs_file = cloudstorage.open(filename,mode='w',content_type='text/csv')
    
    try:
        fp = cloudstorage.open(filename,mode='r')
        gcs_file_temp.write(fp.read())

    except cloudstorage.NotFoundError:  
        headers = 'activity_date,'+'first_name,'+'last_name,'+'contact,'+'organisation,'+'activity_type,'+'is_no_show,'+'gender,'+'pref_jobsearch,'+'pref_presentation,'+'pref_resume,'+'pref_computer,'+'pref_interview,'+'pref_workshops,'+'job_obtained,'+'pref_mentoring,'+'pref_lifeskills,'+'pref_socialmedia,'+'pref_other,'+'type_of_clothing,'+'shoe_size,'+'clothing_size,'+'nbr_suits,'+'nbr_coats,'+'nbr_jackets,'+'nbr_shirts,'+'nbr_pants,'+'nbr_shoes,'+'nbr_knitwear,'+'nbr_misc,'+'nbr_socks,'+'nbr_golfshirts,'+'nbr_tshirts,'+'nbr_belts,'+'nbr_cufflinks,'+'nbr_ties,'+'nbr_skirts,'+'nbr_dresses,'+'nbr_softtops,'+'nbr_kneehighs,'+'nbr_scarves,'+'nbr_handbags,'+'nbr_makeup,'+'nbr_esteem_jewellery,'+'nbr_boots,'+'nbr_underwear,'+'nbr_bra,'+'nbr_camisole,'+'nbr_stocking'+'\n'
    
        gcs_file_temp.write(headers)
    
    for client in clients_data:
        if client.organisation != None:
            organisation = db.GqlQuery("SELECT * FROM organisations where __key__ = KEY('organisations', %s)" % str(client.organisation))
            for org in organisation :
               # logging.debug(org.name)
                client_org_name = org.name
            activities = db.GqlQuery("SELECT * FROM activities where person_id = :1",client.key().id_or_name())
            for act in activities:
                if not ((start_bol and act.date < datetime.datetime.date(start_filter))
                or (end_bol and act.date > datetime.datetime.date(end_filter))):
                    temp = str(act.date)+','+str(client.first_name)+','+str(client.last_name)+','+str(client.mobile)+','+str(client_org_name)+','+str(act.type)+','+str(act.is_no_show)+','+str(client.gender)+','+str(client.pref_jobsearch)+','+str(client.pref_presentation)+','+str(client.pref_resume)+','+str(client.pref_computer)+','+str(client.pref_interview)+','+str(client.pref_workshops)+','+str(client.job_obtained)+','+str(client.pref_mentoring)+','+str(client.pref_lifeskills)+','+str(client.pref_socialmedia)+','+str(client.pref_other)+','+str(act.type_of_clothing)+','+str(client.shoe_size)+','+str(client.clothing_size)+','+str(act.nbr_suits)+','+str(act.nbr_coats)+','+str(act.nbr_jackets)+','+str(act.nbr_shirts)+','+str(act.nbr_pants)+','+str(act.nbr_shoes)+','+str(act.nbr_knitwear)+','+str(act.nbr_misc)+','+str(act.nbr_socks)+','+str(act.nbr_golfshirts)+','+str(act.nbr_tshirts)+','+str(act.nbr_belts)+','+str(act.nbr_cufflinks)+','+str(act.nbr_ties)+','+str(act.nbr_skirts)+','+str(act.nbr_dresses)+','+str(act.nbr_softtops)+','+str(act.nbr_kneehighs)+','+str(act.nbr_scarves)+','+str(act.nbr_handbags)+','+str(act.nbr_makeup)+','+str(act.nbr_esteem_jewellery)+','+str(act.nbr_boots)+','+str(act.nbr_underwear)+','+str(act.nbr_bra)+','+str(act.nbr_camisole)+','+str(act.nbr_stocking)+'\n'
                    gcs_file_temp.write(temp)
                else:
                    continue
    
    gcs_file_temp.close()
    
    temp_file = cloudstorage.open(filename_temp,mode='r')
    main_file = cloudstorage.open(filename,mode='w',content_type='text/csv')
    main_file.write(temp_file.read())
    main_file.close()
    cloudstorage.delete(filename_temp)
           
    mycursor = clients.cursor()
    
    logging.debug(max_count)
    logging.debug(fetch_records)
    
    if fetch_records <= max_count:
        taskqueue.add(url=URL('client_activities_tq'),params=dict(cursor = mycursor,filename = str(filename),start_date = str(start_filter),end_date = str(end_filter),gender = gender,receiverEmail=strRecevEmail,max_count = str(max_count),fetch_records = str(fetch_records)))
    else :
        taskqueue.add(url=URL('mail_report'),params=dict(filename = str(filename),receiverEmail=strRecevEmail))
    
    
def mail_report():          
    
    from gluon.tools import Mail
    
    filename = request.vars['filename']
    
    #Sending mail to the user with All Clients Activities Report
    
    filename_mail = (filename.split("/")[2]).split("_")[0]
    
    #Calling the Sign url function with Expiration limit as 1 week
    signed_url = sign_url_report(filename, expires_after_seconds=604800)
     
    logging.debug('Before mail')
    logging.debug(request.vars['receiverEmail'])
     # Send the GCS file through mail
    mail.send(request.vars['receiverEmail'],
         'All Clients Activities Report',
         ('<html><p> Hi,</p>\
              <p>Please click on the link to download the Report: <a href=%s>%s</a></p></html>' %(signed_url,filename_mail)))

    
def sign_url_report(gcs_filename, expires_after_seconds=60):

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
