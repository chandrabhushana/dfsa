execfile('applications/booking/controllers/people.py', globals())

@auth.requires(has_auth)
def index():
    return people_index(PERSON_TYPE_VOLUNTEER)

@auth.requires(has_auth)
def create():
    return people_create(PERSON_TYPE_VOLUNTEER, required_email=True)

@auth.requires(has_auth)
def update():
    return people_update(PERSON_TYPE_VOLUNTEER)

@auth.requires(has_auth)
def view():
    return people_view(PERSON_TYPE_VOLUNTEER)

@auth.requires(has_auth)
def disable_login():
    return people_login_set(enable=False)

@auth.requires(has_auth)
def enable_login():
    return people_login_set(enable=True)
