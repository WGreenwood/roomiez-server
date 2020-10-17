from flask import Blueprint, request, g

from roomiez_server.helpers import api, tokens, security, validation
from roomiez_server.helpers.forms import requires_form_data
from roomiez_server import models
from roomiez_server.config import ErrorCode

blueprint = Blueprint("authentication", __name__, url_prefix="/auth")

_LOGIN_FIELDS = ['email', 'password']
_REGISTER_FIELDS = ['displayName'] + _LOGIN_FIELDS

def _email_validator(email):  # noqa:E302
    if not validation.verify_email(email):
        return False, ErrorCode.InvalidEmail, None
    return True, email, None

def _password_validator(password):  # noqa:E302
    pwOk, errData = validation.verify_password_strength(password)
    if not pwOk: return False, ErrorCode.WeakPassword, errData  # noqa:E701
    return True, password, None

_FIELD_VALIDATORS = {  # noqa:E305
    'email': _email_validator,
    'password': _password_validator,
}


@blueprint.route('/register', methods=['POST'])
@requires_form_data(fields=_REGISTER_FIELDS, customValidators=_FIELD_VALIDATORS)
def register(formData=None):
    displayName, email, password = formData
    isOk, result = security.do_register(displayName, email, password)

    if isOk: result = api.success(result.get_api_dict(privacy=False))  # noqa:E701
    else: result = api.bad_request(result)  # noqa:E701

    return result


@blueprint.route('/login', methods=['POST'])
@requires_form_data(fields=_LOGIN_FIELDS, customValidators=_FIELD_VALIDATORS)
def login(formData=None):
    email, password = formData

    expirationInHours = 6

    user, jwt, expires = security.do_login(email, password, expirationInHours)
    if not user: return api.bad_request(ErrorCode.IncorrectLogin)  # noqa:E701

    return token_result(user, jwt, expires)


@blueprint.route('/profile', methods=['GET'])
@security.protected_route
def get_profile():
    return api.success(g.user.get_api_dict(privacy=False))


@blueprint.route('/renew', methods=['GET'])
@security.protected_route
def renew_token():
    expirationInHours = 6
    user = g.user
    jwt, expires = security.generate_token(user, expirationInHours)
    return token_result(user, jwt, expires)


def token_result(user, jwt, expires):
    return api.success({
        'user': user.get_api_dict(privacy=False),
        'jwt': jwt,
        'expires': str(expires)
    })


@blueprint.before_app_request
def _get_user_token():
    authToken = request.headers.get('Authorization')
    g.user = None
    if authToken is not None and authToken[0:7] == 'Bearer ':
        jwt = tokens.decode(authToken[7:])
        if jwt:
            user = jwt['user']
            g.user = models.User.query.filter(models.User.id == user['id']).one()
