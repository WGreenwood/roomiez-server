from datetime import datetime, timedelta as _timedelta, timezone
from roomiez_server.models import Bill, BillPayment, BillingCycle, BillType, User  # noqa:F401
from werkzeug.security import generate_password_hash

EMPTY_FIELDS = [
    None,
    '     ',
    '\n\n\n\n',
    '\r\r\r\r'
    '\n\n\n  \r\r \n \r\n'
]

EXISTING_USERS = [
    {'id': 6000, 'displayName': 'Alice', 'email': 'Alice@roomiez.ca', 'password': '~T5,@!q!',
     'role': 'admin', 'householdId': None, 'householdCreator': False},
    {'id': 6001, 'displayName': 'Bob', 'email': 'Bob@roomiez.ca', 'password': 'm+9PsjJ7',
     'role': 'user', 'householdId': None, 'householdCreator': False},
    {'id': 6002, 'displayName': 'Carla', 'email': 'Carla@roomiez.ca', 'password': '2N"D3#tf',
     'role': 'user', 'householdId': None, 'householdCreator': False},
    {'id': 6003, 'displayName': 'Jack', 'email': 'Jack@roomiez.ca', 'password': '$z7xN?CW',
     'role': 'user', 'householdId': None, 'householdCreator': False},
    {'id': 6004, 'displayName': 'Mark', 'email': 'Mark@roomiez.ca', 'password': '9Bq-5{b(',
     'role': 'user', 'householdId': None, 'householdCreator': False},
    {'id': 6005, 'displayName': 'Joan', 'email': 'Joan@roomiez.ca', 'password': '8g_P/{v,',
     'role': 'user', 'householdId': None, 'householdCreator': False},
]

VALID_NEW_USERS = [
    {'displayName': 'Jeremy', 'email': 'Jeremy@roomiez.ca', 'password': 'L3z<fyy['},
    {'displayName': 'Ted', 'email': 'Ted@roomiez.ca', 'password': 'k8c~THw$'},
    {'displayName': 'Grace', 'email': 'Grace@roomiez.ca', 'password': 'u]Uj6Dtx'},
    {'displayName': 'Edna', 'email': 'Edna@roomiez.ca', 'password': 'x33s!hGv'},
    {'displayName': 'Ron', 'email': 'Ron@roomiez.ca', 'password': 'wc6s[<P='},
    {'displayName': 'Kimmy', 'email': 'Kimmy@roomiez.ca', 'password': '*rQk$w7J'},
    {'displayName': 'Rick', 'email': 'Rick@roomiez.ca', 'password': '?}RzK3ks'},
]

VALID_PASSWORDS = [
    'L3z<fyy['
    'k8c~THw$',
    'u]Uj6Dtx',
    'x33s!hGv',
    'wc6s[<P=',
    '*rQk$w7J',
    '?}RzK3ks'
]

INVALID_PASSWORDS = [
    {'password': 'Asdfqwe', 'missingRequirements': ['lengthError', 'digitError', 'symbolError']},
    {'password': 'Asdfqwer', 'missingRequirements': ['digitError', 'symbolError']},
    {'password': 'Asdf44qAlafm44eoig', 'missingRequirements': ['symbolError']},
    {'password': 'Asd!qqa', 'missingRequirements': ['lengthError', 'digitError']},
    {'password': 'LKSJJKGF', 'missingRequirements': ['lowercaseError', 'digitError', 'symbolError']},
    {'password': '44444444', 'missingRequirements': ['lowercaseError', 'uppercaseError', 'symbolError']},
]

ONE_DAY = _timedelta(days=1)
def _utctoday():  # noqa:E302
    return datetime.utcnow().replace(tzinfo=timezone.utc).date()


EXISTING_BILLS = [
    {
        'id': 11, 'type': BillType.Monthly, 'name': 'Cellphone',
        'cost': 39.94, 'date': _utctoday().replace(day=9)
    },
    {
        'id': 12, 'type': BillType.Monthly, 'name': 'Rent',
        'cost': 1492.66, 'date': _utctoday().replace(day=1)
    },
    {
        'id': 13, 'type': BillType.Yearly, 'name': 'Domain Name',
        'cost': 15.00, 'date': _utctoday().replace(month=1, day=1)
    },
    {
        'id': 14, 'type': BillType.Monthly, 'name': 'Internet',
        'cost': 79.99, 'date': _utctoday().replace(day=25)
    },
    {
        'id': 15, 'type': BillType.OneTime, 'name': 'Grocery Shopping',
        'cost': 146.59, 'date': _utctoday().replace(year=2018, month=12, day=3)
    },
    {
        'id': 16, 'type': BillType.OneTime, 'name': 'Grocery Shopping',
        'cost': 146.59, 'date': _utctoday().replace(year=2018, month=12, day=3)
    },
    {
        'id': 17, 'type': BillType.OneTime, 'name': 'Grocery Shopping',
        'cost': 146.59, 'date': _utctoday().replace(month=1, day=2)
    },
    {
        'id': 18, 'type': BillType.OneTime, 'name': 'Grocery Shopping',
        'cost': 146.59, 'date': _utctoday().replace(month=1, day=2)
    },
    {
        'id': 19, 'type': BillType.OneTime, 'name': 'Grocery Shopping',
        'cost': 146.59, 'date': _utctoday().replace(month=1, day=15)
    },
    {
        'id': 20, 'type': BillType.OneTime, 'name': 'Grocery Shopping',
        'cost': 146.59, 'date': _utctoday().replace(month=2, day=26)
    },
    {
        'id': 21, 'type': BillType.OneTime, 'name': 'Grocery Shopping',
        'cost': 146.59, 'date': _utctoday().replace(month=2, day=10)
    },
]

LOGIN_FIELDS = ['email', 'password']
REGISTER_FIELDS = ['displayName'] + LOGIN_FIELDS


def insert_all(db):
    for userData in EXISTING_USERS:
        try:
            userData = dict(userData)
            userData['password'] = generate_password_hash(userData['password'])
            user = User(**userData)
            db.session.add(user)
        except Exception as e:
            print(e)
    # for billData in EXISTING_BILLS:
        # db.session.add(Bill(**billData))
    try:
        db.session.commit()
    except Exception as ex:
        print(ex)
    print()


def user_id_func(user):
    return user['email']


def func_field_id_func(data):
    if callable(data):
        if data.__name__ == 'register_request':
            return 'register'
        elif data.__name__ == 'login_request':
            return 'login'
    else:
        return ','.join(data)
