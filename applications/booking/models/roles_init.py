
is_admin = auth.user.type==PERSON_TYPE_ADMIN if auth.user else False
is_agency = auth.user.type==PERSON_TYPE_AGENCY if auth.user else False
is_employee = auth.user.type==PERSON_TYPE_EMPLOYEE if auth.user else False
is_client = auth.user.type==PERSON_TYPE_CLIENT if auth.user else False
is_volunteer = auth.user.type==PERSON_TYPE_VOLUNTEER if auth.user else False
