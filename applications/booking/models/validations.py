### People Validations - running these in models since they're needed in default/index, not only people controllerskaren.mcleish@email.com
import datetime

if request.controller in ['appadmin', 'default', 'agencies', 'clients', 'employees', 'volunteers']:
    
    db.people.type.requires = IS_IN_SET(PEOPLE_TYPES_SET, zero=None)
    #db.people.age_range.requires = IS_NULL_OR(IS_IN_SET(AGE_RANGES_SET))
    #db.people.age_range.requires = IS_NULL_OR(IS_MATCH('^[0-9]+$', error_message='This is not a valid age'))
    db.people.ethnicity.requires = IS_NULL_OR(IS_IN_SET(ETHNICITIES_SET))
    db.people.title.requires = IS_NULL_OR(IS_IN_SET(TITLE_SET))
    db.people.first_name.requires = IS_NOT_EMPTY(error_message='Please enter a first name')
    db.people.last_name.requires = IS_NOT_EMPTY(error_message='Please enter a last name')
    db.people.mobile.requires = [IS_NOT_EMPTY(error_message='Please enter a contact number')]
    db.people.mobile.requires = IS_MATCH('^[ 0-9 ]+$', error_message='This is not a valid number')
    db.people.contact_number.requires = IS_NULL_OR(IS_MATCH('^[ 0-9 ]+$', error_message='This is not a valid number'))
    db.people.second_contact_number.requires = IS_NULL_OR(IS_MATCH('^[ 0-9 ]+$', error_message='This is not a valid number'))
    
    
    if request.controller in ['clients']:
         db.people.mobile.requires=[IS_NOT_IN_DB(db, 'people.mobile', error_message='Please enter a unique contact number')]
         db.people.mobile.requires=IS_MATCH('^[ 0-9 ]+$', error_message='This is not a valid number')
         db.people.second_contact_number.requires = IS_NULL_OR(IS_MATCH('^[ 0-9 ]+$', error_message='This is not a valid number'))
         db.people.contact_number.requires = IS_MATCH('^[ 0-9 ]+$', error_message='This is not a valid number')
         db.people.ttw_paid.requires = IS_IN_SET(TTW_PAID_SET,error_message='Please enter Yes or No')

    # refferal agencies for clients only , and sponsors for volunteers####
    if request.controller in ['clients','agencies']:
        
        db.people.organisation.requires=IS_IN_DB(db((db.organisations.organisations_types=='Referral Organisation')& (db.organisations.deactivated==False)),'organisations.id','organisations.name', zero='', error_message='Please choose an existing Organisation or request Admin to create a new Organisation')
    elif request.controller in ['volunteers']:
        db.people.organisation.requires=IS_NULL_OR(IS_IN_DB(db((db.organisations.organisations_types=='Sponsor')& (db.organisations.deactivated==False)),'organisations.id','organisations.name', zero='', error_message='Please choose an existing Organisation or request Admin to create a new Organisation'))

    # backend will list all the available orgs
    if request.controller in ['appadmin']:
        db.people.organisation.requires=IS_NULL_OR(IS_IN_DB(db(db.organisations.deactivated==False),'organisations.id','organisations.name', zero='', error_message='Please choose an existing Organisation or request Admin to create a new Organisation'))
        
    
    if is_admin  and request.controller in ['default']:
        db.people.organisation.requires=IS_NULL_OR(IS_IN_DB(db(db.organisations.deactivated==False and db.organisations.organisations_types=='Sponsor'),'organisations.id','organisations.name', zero='', error_message='Please choose an existing Organisation or request Admin to create a new Organisation'))
    elif request.controller in ['default']:
        db.people.organisation.requires=IS_IN_DB(db(db.organisations.deactivated==False and db.organisations.organisations_types=='Referral Organisation'),'organisations.id','organisations.name', zero='', error_message='Please choose an existing Organisation or request Admin to create a new Organisation')
        db.people.suburb_addr.requires = IS_NULL_OR(IS_IN_SET(SUBURB_SET,error_message='Please select a Suburb'))
        db.people.city_addr.requires = IS_NULL_OR(IS_IN_SET(CITY_SET))
    
    if request.controller in ['clients']:
        #Rel-3 Req R3_10 made date of birth mandatory and displaying the validation message on 23rd Jan by Subhasmita
        db.people.date_of_birth.requires=[IS_NOT_EMPTY(error_message='Please enter a Date of Birth')]
        # Validation added for DOB on 3/06/2015 by Meenakshi
        db.people.date_of_birth.requires = IS_DATE_IN_RANGE(format=T('%d-%m-%Y'),minimum=datetime.date(1915,1,1),maximum=None,error_message='Date of Birth must be greater than 01-01-1915!')
        # Suburb and City made as Dropdown
        db.people.postcode_addr.requires=IS_NULL_OR(IS_MATCH('^[ 0-9 ]+$', error_message='This is not a valid Postcode!'))
        db.people.suburb_addr.requires = IS_IN_SET(SUBURB_SET,error_message='Please select a Suburb')
        db.people.city_addr.requires = IS_NULL_OR(IS_IN_SET(CITY_SET))
        db.people.registration_key.default='pending' #prevents login
    else:
        db.people.registration_key.default='' #allows login for TP since email is required
       
    if request.controller=='clients' or (request.controller=='default' and is_client):
        zero = None if request.functon=='update' or request.args(0)=='profile' else ''
        db.people.gender.requires=IS_IN_SET(GENDERS_SET, zero=zero, error_message='Please choose a gender')
        #Rel-3 Req R3_5 Removed validation message for shoe size on 22nd Jan by Subhasmita
        db.people.shoe_size.requires = IS_NULL_OR(IS_IN_SET(SHOE_SIZES_SET, zero=zero, error_message=''))
        #Rel-3 Req R3_5 Removed validation message for Clothing size on 22nd Jan by Subhasmita
        db.people.clothing_size.requires = IS_NULL_OR(IS_IN_SET(CLOTHING_SIZES_SET, zero=zero, error_message=''))
        db.people.contact_name.requires = IS_NOT_EMPTY()
        #db.people.contact_number.requires = IS_NOT_EMPTY()
    
    else:
        db.people.gender.requires=IS_NULL_OR(IS_IN_SET(GENDERS_SET,error_message='Please choose a gender'))
        db.people.shoe_size.requires = IS_NULL_OR(IS_IN_SET(SHOE_SIZES_SET))
        db.people.clothing_size.requires = IS_NULL_OR(IS_IN_SET(CLOTHING_SIZES_SET))

if request.controller in ['organisations']:
    db.organisations.organisations_types.requires=IS_IN_SET(ORGANISATION_TYPES, error_message='Please choose a Organisation Type')
    db.organisations.suburb_addr.requires = IS_IN_SET(SUBURB_SET,error_message='Please select a Suburb')
    db.organisations.city_addr.requires = IS_NULL_OR(IS_IN_SET(CITY_SET))
  
if request.controller in ['agencies']:
        db.people.organisation.requires=IS_IN_DB(db(db.organisations.deactivated==False and db.organisations.organisations_types=='Referral Organisation'),'organisations.id','organisations.name', zero='', error_message='Please choose an existing Organisation or request Admin to create a new Organisation')
        db.people.mobile.requires = IS_MATCH('^[ 0-9 ]+$', error_message='This is not a valid number')
        db.people.second_contact_number.requires = IS_NULL_OR(IS_MATCH('^[ 0-9 ]+$', error_message='This is not a valid number'))

if request.controller in ['employees','volunteers']:
    db.people.registration_key.default='pending' #prevents login
    #db.people.suburb_addr.requires=[IS_MATCH('^[ a-zA-Z ]+$', error_message='This is not a valid Suburb!')]
    db.people.suburb_addr.requires = IS_IN_SET(SUBURB_SET,error_message='Please select a Suburb')
    db.people.city_addr.requires = IS_NULL_OR(IS_IN_SET(CITY_SET))
    db.people.postcode_addr.requires=IS_NULL_OR(IS_MATCH('^[ 0-9 ]+$', error_message='This is not a valid Postcode!'))
    
#if request.controller in ['volunteers']:
#   db.people.date_trained.requires = IS_DATE(error_message='Invalid date. Please enter date in yyyy-mm-dd')
if is_volunteer:
    db.people.pref_police.writable = False
    db.people.pref_induction.writable = False
    db.people.pref_children_check.writable = False
    db.people.date_trained.writable = False
    db.people.pref_shadow.writable = False
else:
    db.people.pref_police.writable = True
    db.people.pref_induction.writable = True
    db.people.pref_children_check.writable = True
    db.people.date_trained.writable = True
    db.people.pref_shadow.writable = True

if request.controller in ['volunteers']:
    db.people.date_of_birth.requires = IS_NULL_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='Invalid date. Please enter date in dd-mm-yyyy format'))
    db.people.date_trained.requires = IS_NULL_OR(IS_DATE(format=T('%d-%m-%Y'),error_message='Invalid date. Please enter date in dd-mm-yyyy format'))
