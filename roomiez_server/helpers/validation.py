from re import search as _searchRegex
from roomiez_server.config import ErrorCode as _ErrorCode


def strip(value):
    return '' if value is None else str(value).strip()


def is_empty(value):
    return value is None or len(value) == 0


def _select_keys(keys, data, predicate):
    results = []
    for key in keys:
        if predicate(key, data):
            results.append(key)

    empty = len(results) == 0
    return empty, results if not empty else None


def basic_form(keys, postData, customValidators):
    def nonExistantKeys(key, data): return key not in data
    def emptyKeys(key, data):  # noqa:E306
        value = data[key]
        if value is None: return True  # noqa:E701
        if isinstance(value, str):
            return is_empty(value)
        return False

    empty, missingKeys = _select_keys(keys, postData, nonExistantKeys)
    if not empty: return _ErrorCode.MissingParameter, missingKeys  # noqa:E701

    for key in keys:
        val = postData[key]
        if isinstance(val, str):
            postData[key] = strip(postData[key])  # noqa:E701
    empty, missingKeys = _select_keys(keys, postData, emptyKeys)
    if not empty: return _ErrorCode.EmptyParameter, missingKeys  # noqa:E701

    if customValidators is not None:
        for validatorKey in customValidators:
            validator = customValidators[validatorKey]
            value = postData[validatorKey]
            valid, result, extras = validator(value)
            if not valid:
                errData = {'key': validatorKey}
                if extras is not None:
                    errData['data'] = extras
                return result, errData  # noqa:E701
            postData[validatorKey] = result

    return _ErrorCode.Success, list(postData[key] for key in keys)


def verify_decimal(value):
    return _searchRegex(r"^\d*(\.\d\d?)?$", value) is not None


def verify_email(email):
    return _searchRegex(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+$)", email) is not None


def verify_password_strength(password):
    """
    Verify the strength of 'password'
    Returns a tuple
        Value 0 is success flag
        Value 1 is dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """
    # TODO: Enhance this
    # Reject x amount of repeated characters, last 3 passwords, etc...

    # calculating the length
    lengthError = len(password) < 8

    # searching for digits
    digitError = _searchRegex(r"\d", password) is None

    # searching for uppercase
    uppercaseError = _searchRegex(r"[A-Z]", password) is None

    # searching for lowercase
    lowercaseError = _searchRegex(r"[a-z]", password) is None

    # searching for symbols
    symbolError = _searchRegex(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~<>"+r'"]', password) is None

    # overall result
    passwordOk = not (lengthError or digitError or uppercaseError or lowercaseError or symbolError)

    return (passwordOk, {
        'passwordOk': passwordOk,
        'lengthError': lengthError,
        'digitError': digitError,
        'uppercaseError': uppercaseError,
        'lowercaseError': lowercaseError,
        'symbolError': symbolError,
    })
