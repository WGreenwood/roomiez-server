from functools import wraps as _wraps

from flask import g as _g
from werkzeug.security import check_password_hash as _check_password_hash, generate_password_hash as _generate_password_hash
from roomiez_server.config import ErrorCode as _ErrorCode
from roomiez_server.models import User as _User

from . import api as _api
from . import tokens as _tokens


def user_logged_in():
    return _g.user is not None
def user_is_admin():  # noqa:E302
    return user_logged_in() and _g.user.role == 'admin'


def protected_route(view, requiredRole='user'):
    @_wraps(view)
    def wrapped_protected_route(**kwargs):
        if not user_logged_in(): return _api.unauthorized()  # noqa:E701

        if requiredRole == 'admin' and not user_is_admin():
            return _api.unauthorized()

        return view(**kwargs)
    return wrapped_protected_route


def requires_household(view):
    @_wraps(view)
    def wrapped_requires_household(**kwargs):
        if _g.user.householdId is None:
            return _api.not_found()
        return view(**kwargs)
    return wrapped_requires_household


def user_has_household_access(user, householdId):
    if user.role == 'admin':
        return True
    return user.householdId == householdId


def do_register(displayName, email, password, role='user'):
    password = _generate_password_hash(password, salt_length=16)
    user = _User(displayName=displayName, email=email, password=password, role=role)

    from roomiez_server import DB
    from sqlalchemy.exc import IntegrityError, OperationalError

    try:
        DB.session.add(user)
        DB.session.commit()
        return True, user
    except IntegrityError:
        return False, _ErrorCode.EmailAlreadyRegistered
    except OperationalError as ex:
        print("Unexpected database error: {}".format(vars(ex)))
        return False, _ErrorCode.UnknownError


def do_login(email, password, expirationInHours=60):
    user = _User.query.filter(_User.email == email).first()
    if not user or not _check_password_hash(user.password, password):
        return None, None, None

    jwt, exp = generate_token(user, expirationInHours)
    return user, jwt, exp


def generate_token(user, expirationInHours=60):
    jwt, exp = _tokens.encode({
        'user': user.get_api_dict(privacy=False)
    }, expirationInHours)
    return jwt, exp
