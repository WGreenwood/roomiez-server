from base64 import b64decode as _b64decode
from dateutil.relativedelta import relativedelta as _relativedelta
from roomiez_server.helpers import dates
from jwt import decode as _decodeJwt, encode as _encodeJwt
from jwt.exceptions import InvalidTokenError as _InvalidTokenError

from flask import current_app as _current_app


def getSecret():
    return _b64decode(_current_app.config.get('SECRET_KEY'))


def encode(data, expirationInHours):
    secret = getSecret()
    exp = dates.utcnow() + _relativedelta(hours=expirationInHours)
    jwtData = {
        'data': data,
        'exp': exp
    }
    return _encodeJwt(jwtData, secret, algorithm='HS512'), exp


def decode(token):
    secret = getSecret()
    try:
        jwt = _decodeJwt(token, secret, algorithms=['HS512'])
        return jwt['data']
        # InvalidTokenError is the base error of any error thrown when decoding the jwt
    except _InvalidTokenError:
        return None
