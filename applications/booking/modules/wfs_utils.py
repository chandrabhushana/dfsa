"""
All vars and functions from this module get imported in db_init.py.

Only code that does not needed access to the web2py environment can be included in this file.
Examples of code which can NOT be put in this file: 
    any html helpers (URL, DIV, SPAN, LINK)
    request.*
    response.*
    auth*, db*

Changes to this file are not loaded automatically be web2py. There are 2 way to reload changes from this file:
1. Edit the file in web2py admin console
2. Restart web2py server
"""
import csv
from datetime import datetime
from gluon.storage import Storage

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M'

FITTING_REPORTS = Storage(FIRST_VISITS='First Visits', RETURN_VISITS='Return Visits', NO_SHOWS='No Shows', ALL='All Dressing')

PERSON_TYPE_CLIENT = 'Client'
PERSON_TYPE_AGENCY = 'Agency User'
PERSON_TYPE_EMPLOYEE = 'Employee'
PERSON_TYPE_ADMIN = 'Admin'
PERSON_TYPE_VOLUNTEER = 'Volunteer'


AFFILIATE_BBN = 'obs-bris.appspot.com'
#AFFILIATE_MP = 'obs-mpfrankston.appspot.com'
#AFFILIATE_MELB = 'obs-melb2.appspot.com'
AFFILIATE_SYD = 'dfs-syd.appspot.com'
AFFILIATE_MP_RBUD = 'obs-mprosebud.appspot.com'
AFFILIATE_MP_FSTON = 'obs-mpfrankston.appspot.com'
AFFILIATE_MELB = 'dfsdevapp.appspot.com'
#AFFILIATE_SYD = 'syddevapp1.appspot.com'
#AFFILIATE_MP_RBUD = 'dfsdevapp1.appspot.com'
#AFFILIATE_MP_FSTON = 'mopdevapp.appspot.com'
AFFILIATE_AUCK = 'auktestapp.appspot.com'


PERSON_TYPE_TO_ENTITY = {'admin':PERSON_TYPE_ADMIN,'clients':PERSON_TYPE_CLIENT, 'agencies':PERSON_TYPE_AGENCY, 'employees':PERSON_TYPE_EMPLOYEE,'volunteers':PERSON_TYPE_VOLUNTEER}
entity_by_person_type = lambda person_type : [k for k, v in PERSON_TYPE_TO_ENTITY.iteritems() if v == person_type][0]
person_type_by_entity = lambda entity : PERSON_TYPE_TO_ENTITY[entity]

#Drop down lists to be used in model specific validations 
SHOE_SIZES_SET_MALE = ('7.0','7.5','8.0','8.5','9.0','9.5','10.0','10.5','11.0','11.5','12.0','12.5','13.0','13+')
SHOE_SIZES_SET_FEMALE = ('5.0','6.0','6.5','7.0','7.5','8.0','8.5','9.0','9.5','10.0','10.5','11.0','11.5')
SHOE_SIZES_SET = ('6.0','6.5','7.0','7.5','8.0','8.5','9.0','9.5','10.0','10.5','11.0','11.5','12.0','12.5','13.0','13+')
CLOTHING_SIZES_SET_MALE = ('XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '4XL+')
CLOTHING_SIZES_SET_FEMALE = ('6', '8', '10', '12', '14', '16','18', '20','22', '24','26','28')
CLOTHING_SIZES_SET = ('6', '8', '10', '12', '14', '16','18', '20','22', '24','26','28', 'XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '4XL+')
#AGE_RANGES_SET = ('Under 20', '20-25', '26-35', '36-45', '46-55', 'Over 55')
#Rel-3 reqR3_7 Client Add tick box in Client Record for Job Obtained by Mukesh
ETHNICITIES_SET = ('African', 'American', 'Asian', 'Australian', 'European', 'Indigenous Australian','Maori', 'Middle Eastern', 'New Zealander', 'NZ European', 'Indian','Sri Lankan','Pacific Island' ,'Pakistani','Other')
#STATES_SET = ('ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA')
SUBURB_SET = ('Albert-Eden','Devonport-Takapuna','Franklin','Great Barrier','Henderson-Massey','Hibiscus and Bays','Howick','Kaipatiki','Mangere-Otahuhu','Manuwera','Maungakiekie-Tamaki','Orakei','Otara-Papatoetoe','Papakura','Puketepapa','Rodney','Upper Harbour','Waiheke','Waitakere Ranges','Waitemata','Whau')
CITY_SET = ('Albany Ward','Albert-Eden-Roskill Ward','Franklin Ward','Howick Ward','Manukau Ward','Manurewa-Papakura Ward','Maungakiekie-Tamaki Ward','North Shore Ward','Orakei Ward','Rodney Ward','Waitakere Ward','Waitemata and Gulf Ward','Whau Ward')

GENDERS_SET = ('Female', 'Male')
PEOPLE_TYPES_SET = ('', PERSON_TYPE_CLIENT, PERSON_TYPE_AGENCY, PERSON_TYPE_EMPLOYEE, PERSON_TYPE_ADMIN, PERSON_TYPE_VOLUNTEER)
TITLE_SET = ('Miss', 'Mr', 'Mrs', 'Ms')
TYPE_OF_CLOTHING_SET = ('Court', 'First dressing', 'Second dressing', 'Life Events', 'Mobile Service','Release','Other')
ORGANISATION_TYPES = ('Referral Organisation', 'Sponsor')
from copy import copy
ACTIVITIES_ITEMS_COMMON = ['nbr_suits', 'nbr_coats', 'nbr_jackets', 'nbr_shirts', 'nbr_pants', 'nbr_knitwear', 'nbr_misc','nbr_belts']
ACTIVITIES_ITEMS_MALE = copy(ACTIVITIES_ITEMS_COMMON)
ACTIVITIES_ITEMS_FEMALE = copy(ACTIVITIES_ITEMS_COMMON)
ACTIVITIES_ITEMS_MALE.extend(['nbr_socks', 'nbr_golfshirts', 'nbr_tshirts', 'nbr_shoes','nbr_cufflinks','nbr_ties'])
ACTIVITIES_ITEMS_BOTH = copy(ACTIVITIES_ITEMS_MALE)
ACTIVITIES_ITEMS_FEMALE.extend(['nbr_skirts', 'nbr_shoes','nbr_dresses', 'nbr_softtops', 'nbr_kneehighs', 'nbr_scarves', 'nbr_handbags', 'nbr_makeup', 'nbr_esteem_jewellery','nbr_boots', 'nbr_underwear', 'nbr_bra',  'nbr_camisole','nbr_stocking'])
ACTIVITIES_ITEMS_BOTH.extend(['nbr_skirts', 'nbr_shoes','nbr_dresses', 'nbr_softtops', 'nbr_kneehighs', 'nbr_scarves', 'nbr_handbags', 'nbr_makeup', 'nbr_esteem_jewellery', 'nbr_boots','nbr_underwear', 'nbr_bra', 'nbr_camisole', 'nbr_stocking'])
ACTIVITIES_ITEMS_ONLY_MALE = ['nbr_socks', 'nbr_golfshirts', 'nbr_tshirts', 'nbr_shoes','nbr_cufflinks','nbr_ties']
ACTIVITIES_ITEMS_ONLY_FEMALE = ['nbr_skirts', 'nbr_shoes','nbr_dresses', 'nbr_softtops', 'nbr_kneehighs', 'nbr_scarves', 'nbr_handbags', 'nbr_makeup', 'nbr_esteem_jewellery','nbr_boots', 'nbr_underwear', 'nbr_bra',  'nbr_camisole','nbr_stocking']
TTW_PAID_SET = ['Yes','No']
#SINGLE_PARENT_SET = ['Yes','No']

def render_report_csv(ofile, result, colnames=[], null='<NULL>', *args, **kwargs):
    delimiter = kwargs.get('delimiter', ',')
    quotechar = kwargs.get('quotechar', '"')
    quoting = kwargs.get('quoting', csv.QUOTE_MINIMAL)
    writer = csv.writer(ofile, delimiter=delimiter,
                        quotechar=quotechar, quoting=quoting)
    writer.writerow(colnames)
    
    for record in result:
        row = []
        for col in colnames:
            if '.' in col:
                (t, f) = col.split('.')
                row.append(record.get(t).get(f))
            else:
                row.append(record.get(col))
        writer.writerow(row)


#common utils
def create_time_list(min_hour, max_hour, minutes=15):
    #TODO implement configurable minutes divisions and different formats
    hour = min_hour
    arr = []
    while hour < max_hour:
        #need to have the zero in front for the calendar widget. alternatively, format in list.json
        shour = '0' if hour<10 else ''
        shour += str(hour)
        arr.append(shour + ':00')
        arr.append(shour + ':15')
        arr.append(shour + ':30')
        arr.append(shour + ':45')
        hour += 1
    arr.append(str(max_hour) + ':00')
    return arr


def parse_time(timestr):
    try:
        return datetime.strptime(timestr, TIME_FORMAT)
    except:
        return None

def parse_date(strdate, default=None, as_datetime=False):
     try:
         dt = datetime.strptime(strdate, DATE_FORMAT)
         return dt if as_datetime else dt.date()
         #return datetime.strptime(strdate, DATE_FORMAT).date()
     except:
         return default
     
def display_name(person):
    return person.first_name+' '+person.last_name+' ('+person.mobile+')'

def bool2yn(boolean):
    return 'Yes' if boolean else 'No'

def lower_or(input, default=''):
    return input.lower() if input else default

def subdict(d, keys):
    return dict((k, d[k]) for k in keys if k in d)
