##Not a physical table. To be referenced in all other tables. 
##The _by columns cannot reference db.auth_user due to the cyclical dependency.
auditing = db.Table(db, 'auditing',
    Field('created_on', 'datetime', default=request.now, writable=False, readable=False),
    Field('created_by', 'integer', default=auth.user_id, writable=False, readable=False),
    Field('updated_on', 'datetime', update=request.now, writable=False, readable=False),
    Field('updated_by', 'integer', update=auth.user_id, writable=False, readable=False),
    Field('deactivated', 'boolean', default=False, readable=False, writable=False, notnull=True))

#Not a physical table. To be referenced by people and activities
shared_career_services = db.Table(db, 'shared_career_services',
    Field('pref_jobsearch', 'boolean', default=False, label=T('Job Search')),
    Field('pref_presentation', 'boolean', default=False, label=T('Presentation Skills')),
    Field('pref_resume', 'boolean', default=False, label=T('Resume Writing')),
    Field('pref_computer', 'boolean', default=False, label=T('Computer Skills')),
    Field('pref_interview', 'boolean', default=False, label=T('Interview Skills')),
    Field('pref_workshops', 'boolean', default=False, label=T('Workshops')),
    #Rel-3 reqR3_8 Client Add tick box in Client Record for Job Obtained on Jan 22 by Mukesh
    Field('job_obtained','boolean',default=False,label=T('Job Obtained')),
    Field('pref_mentoring', 'boolean', label=T('Mentoring')),
    Field('pref_lifeskills', 'boolean', label=T('Life Skills')),
    Field('pref_socialmedia', 'boolean', label=T('Social Media')),
    Field('pref_other', 'string', label=T('Other')),
    )

#define organisations before people fields
db.define_table('organisations',
    #Field('abn', 'string', label=T('ABN or Non-Profit ID')),
    Field('name', 'string', notnull=True, default='', label=T('Organisation Name')),
    Field('desc', 'text', default='', label=T('Description')),
    Field('contact_name', 'string', default=None, label=T('Contact Name')),
    Field('contact_phone', 'string', default=None, label=T('Contact Phone')),
    Field('contact_mobile', 'string', default=None, label=T('Contact Mobile')),
    Field('contact_email', 'string', default=None, label=T('Contact Email')),
    #Field('second_contact_number', 'string', label=T('Alternate Contact Number')), # fixed for defect R2_PT_Defect_35
    Field('comments', 'text', label=T('Comments')),
    
    Field('street_addr', 'text', notnull=True, default='', label=T('Street Address')),
    Field('suburb_addr', 'string',default='',label=T('Suburb')),
    Field('city_addr', 'string',default='',label=T('City')),
    Field('postcode_addr','string', default='',label=T('Postcode')),
    Field('organisations_types', 'string', notnull=True, default='',label=T('Organisation Type')),
    Field('is_disability_ref', 'boolean', default=False, label=T('Disability Employment Services')),
    Field('is_jobservice_aus_ref', 'boolean', default=False, label=T('Job Service Australia')),
    Field('is_community_ref', 'boolean', default=False, label=T('Community')),
    Field('is_education_ref', 'boolean', default=False, label=T('Education')),
    Field('other_ref', 'string',label=T('Other')),
    Field('is_in_kind_doanations', 'boolean', default=False, label=T('In Kind Donations')),
    Field('is_financial_sponsor', 'boolean', default=False, label=T('Financial')),
    Field('is_volunteer_sponsor', 'boolean', default=False, label=T('Volunteering')),
    Field('other_sponsor', 'string', label=T('Other')),
    Field('is_dept_employment', 'boolean', default=False, label=T('Dept.of Employment, Economic Development and Innovation')),
    Field('is_dept_corrective', 'boolean', default=False, label=T('Dept.of Corrective Services')),
    Field('is_job_placement_service', 'boolean', default=False, label=T('Job Placement Services')),
    Field('is_work_income', 'boolean', default=False, label=T('Work and Income')),
    auditing)

###Need to use array here and NOT db.Table
custom_auth_fields = [
    #Contact Details
    Field('type', 'string', writable=False, label=T('User Type')),
    Field('mobile', 'string', default='', notnull=True, label=T('Contact Number')),
    #Address Details
    Field('title', 'string', label=T('Title')),
    Field('street_addr', 'text', label=T('Street Address')),
    Field('suburb_addr', 'string', label=T('Suburb')),
    Field('city_addr', 'string', label=T('City')),
    Field('postcode_addr', 'string', label=T('Postcode')),
    #Other Details
    Field('type_of_job', 'string', label=T('Job or Study Area')),
    Field('comments', 'text', label=T('Comments')),
    Field('length_of_time_unemployed','string',label=T('Length of Time Unemployed')),
    Field('educational_level','string',label=T('Educational Level')),
    #Added notnull validation for date of birth on 23rd Jan by Subhasmita
    Field('date_of_birth', 'date', label=T('Date of Birth(dd-mm-yyyy)')),
    Field('date_trained', 'date', label=T('Date Trained(dd-mm-yyyy)')),
    Field('gender', 'string', default=''),
    Field('age_range', 'string', label=T('Age')),
    Field('ethnicity', 'string', label=T('Ethnicity')),
    Field('referral_contact_email', 'string', label=T('Referral Contact Email')),
    Field('medical_conditions', 'string', label=T('Medical Conditions')),
    Field('contact_name', 'string', label=T('Contact Name')), #Referral for clients, Emergency for volunteers
    Field('contact_number', 'string', label=T('Contact Number')), #Referral for clients, Emergency for volunteers
    Field('second_contact_number','string',default='',label=T('Alternate Contact Number')),
    #Field('title','string',default=" ",label=T('Title')),     
    Field('organisation', 'integer'),
    Field('ttw_paid', 'string',default='', label=T('TTW Paid')),
    Field('single_parent', 'boolean', default=False,label=T('Single Parent')),
    Field('shoe_size', 'string', label=T('Shoe Size')),
    Field('clothing_size', 'string', label=T('Clothing Size')),
    Field('job_type', 'string', label=T('Type of Job')), #clients
    Field('comments','text',label=T('Comments')),
    #Employee/Volunteer Preferences (also workshops from shared table)
    Field('pref_going_places_network','boolean',label=T('Going Places Network')),
    Field('pref_professional_womens_group','boolean',label=T('PWG')),
    Field('pref_permission_to_photo','boolean',label=T('Permission to Photograph')),
    Field('pref_permission_to_follow_up','boolean',label=T('Permission to Follow Up')),
    Field('pref_permission_to_invite_events','boolean',label=T('Permission to Invite Events')),

    Field('pref_showroom', 'boolean', label=T('Showroom')), #employee/volunteer
    Field('pref_fitting', 'boolean', label=T('Dressings')), #employee/volunteer
    Field('pref_admin', 'boolean', label=T('Office Administration')), #employee/volunteer
    Field('pref_police', 'boolean', label=T('Police Check Complete')),
    Field('pref_children_check', 'boolean', label=T('Working with Children Check Complete')),
    Field('pref_induction', 'boolean', label=T('Induction Complete')),
    Field('pref_shadow', 'boolean', label=T('Shadow Session Complete')),
    Field('pref_collection', 'boolean', label=T('Clothing Collection')), #employee/volunteer
    Field('pref_donations', 'boolean', label=T('Donation Sourcing')), #employee/volunteer
    Field('pref_mentoring', 'boolean', label=T('Mentoring')),
    Field('pref_careers', 'boolean', label=T('Resource Centre')), #employee/volunteer
    shared_career_services,
    auditing]
    
    #Table to store De-activation and Re-activation Dates
db.define_table('activation_dates',
    Field('record_type','string',label=T('Entity Type')),
    Field('record_id','string',label=T('Entity ID')),
    Field('de_activate', 'string', label=T('De_Activate')),
    Field('date','datetime',label=T('Date')),
    auditing
    )

auth.settings.extra_fields[auth.settings.table_user_name] = custom_auth_fields #needs to be before auth.define_tables()
auth.define_tables() # creates all needed tables
db.people = db[auth.settings.table_user_name]

def int_field(name):
    return Field(name, 'integer', default=0)

a_nbr_fields = []
for i in ACTIVITIES_ITEMS_BOTH:
    a_nbr_fields.append(int_field(i))

db.define_table('activities',
    Field('person_id', 'integer', writable=False, label=T('User')),
    Field('type', 'string', label=T('Activity Type')),
    Field('type_of_clothing', 'string', label=T('Type of clothing')),
    Field('date', 'date', label=T('Date')),
    Field('is_no_show', 'boolean', label=T('No Show?')),
    Field('clothing_size', 'string', label=T('Clothing Size')),
    Field('comments', 'text', label=T('Comments')),
    Field('shoe_size', 'string', label=T('Shoe Size')),
    Field('start_time', 'string', default='09:00', notnull=True),
    Field('end_time', 'string', default='09:15', notnull=True),
    Field('gender', 'string', default='', label=T('Gender Helped')),
    Field('image','upload', label=T('Image(jpg, png, gif, bmp; <500KB)')),
    Field('person_type','string',label=T('Person Type')),
    shared_career_services,
    auditing,
    *a_nbr_fields
    )

db.define_table('event_types',
    Field('name', 'string', label=T('Event Type')),
    Field('color', 'string'),
    auditing)


db.define_table('events',
    Field('type', 'integer', default='', notnull=True, label=T('Event Type')),
    Field('name', 'string', default='', notnull=True, label=T('Event Name')),
    Field('display_name', 'string'),     # New field for displaying Volunteer name along with Event description
    Field('slots', 'integer', default=1, label=T('Total Slots')),
    Field('date', 'date', default=request.now.date or '', notnull=True),
    Field('start_time', 'string', default='10:00', notnull=True),
    Field('end_time', 'string', default='11:00', notnull=True),
    Field('desc', 'text', default='', label=T('Event Description')),
    Field('remaining_slots','integer'),
    #Field('location', 'string'),
    Field('is_full', 'boolean', default=False, notnull=True, writable=False), #storing for efficient checking
    auditing)


db.define_table('registrations',
    Field('event', db.events, default=1, notnull=True, label=T('Event')),
    Field('person', 'integer', default=auth.user_id or 1, notnull=True, label=T('Person ID')),
    Field('type', 'string', default='Client', notnull=True, label=T('Registration/Person Type')),    
    auditing)
