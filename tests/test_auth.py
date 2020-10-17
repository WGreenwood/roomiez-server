import pytest  # noqa: F401

from testhelper import json_request, get_combinations, get_combinations_double
import testdata

from roomiez_server.config import ErrorCode
from roomiez_server.models import User


def register_request(client, data={}, headers={}):
    return json_request(client, '/auth/register', data=data, headers=headers)
def login_request(client, data={}, headers={}):  # noqa:E302
    return json_request(client, '/auth/login', data=data, headers=headers)


@pytest.mark.parametrize('user', testdata.EXISTING_USERS[0:4], ids=testdata.user_id_func)
def test_login(app, client, user):
    data = {
        'email': user['email'],
        'password': user['password'],
    }
    code, success, result, statusCode = login_request(client, data=data)
    assert_success(code, success, statusCode)

    assert 'jwt' in result, 'No JWT was returned for successful login'
    assert 'user' in result, 'No user was returned for successful login'
    validate_user_dict(app, user, result['user'])

@pytest.mark.parametrize('user', testdata.VALID_NEW_USERS[0:4], ids=testdata.user_id_func)  # noqa:E302
def test_register_new(app, client, user):
    code, success, result, statusCode = register_request(client, data=user)
    assert_success(code, success, statusCode)

    assert result is not None, 'No user was returned'
    validate_user_dict(app, user, result)


@pytest.mark.parametrize('user', testdata.VALID_NEW_USERS[0:2], ids=testdata.user_id_func)  # noqa:E302
@pytest.mark.parametrize('password', testdata.VALID_PASSWORDS)
def test_invalid_login(client, user, password):
    data = {
        'email': user['email'],
        'password': password,
    }
    code, success, result, statusCode = login_request(client, data=data)
    assert_failure(code, success)
    assert_code(ErrorCode.IncorrectLogin, code)


@pytest.mark.parametrize('user', testdata.EXISTING_USERS[0:4], ids=testdata.user_id_func)  # noqa:E302
def test_register_existing_user(client, user):
    data = {
        'displayName': user['displayName'],
        'email': user['email'],
        'password': testdata.VALID_PASSWORDS[0],
    }
    code, success, result, statusCode = register_request(client, data=data)
    assert_failure(code, success)
    assert_code(ErrorCode.EmailAlreadyRegistered, code)


@pytest.mark.parametrize('user', testdata.VALID_NEW_USERS[0:4], ids=testdata.user_id_func)
@pytest.mark.parametrize('invalidPasswordData', testdata.INVALID_PASSWORDS)
def test_register_weak_password(client, user, invalidPasswordData):
    data = {
        'displayName': user['displayName'],
        'email': user['email'],
        'password': invalidPasswordData['password'],
    }
    code, success, result, statusCode = register_request(client, data=data)
    assert_failure(code, success)
    assert_code(ErrorCode.WeakPassword, code)

    requirements = result['data']
    realMissingRequirements = invalidPasswordData['missingRequirements']
    for requirement in requirements:
        value = requirements[requirement]
        correctValue = requirement in realMissingRequirements
        assert value == correctValue


MISSING_PARAMETER_TESTS = [
    (login_request, list(fields)) for fields in get_combinations(testdata.LOGIN_FIELDS)
] + [(register_request, list(fields)) for fields in get_combinations(testdata.REGISTER_FIELDS)]
@pytest.mark.parametrize('method,keys', MISSING_PARAMETER_TESTS, ids=testdata.func_field_id_func)
def test_missing_parameters(client, method, keys):
    data = dict(testdata.VALID_NEW_USERS[1])
    for key in keys:
        del data[key]

    code, success, result, statusCode = method(client, data=data)
    validate_bad_request(code, success, statusCode)

    assert_code(ErrorCode.MissingParameter, code)
    assert result == keys


EMPTY_PARAMETER_TESTS = get_combinations_double(
                            login_request, testdata.LOGIN_FIELDS, testdata.EMPTY_FIELDS)
EMPTY_PARAMETER_TESTS += get_combinations_double(
                            register_request, testdata.REGISTER_FIELDS, testdata.EMPTY_FIELDS)
@pytest.mark.parametrize('method,fieldVals', EMPTY_PARAMETER_TESTS)  # noqa:E302
def test_empty_parameters(client, method, fieldVals):
    data = dict(testdata.VALID_NEW_USERS[2])
    for key in fieldVals.keys():
        data[key] = fieldVals[key]

    code, success, result, statusCode = method(client, data=data)
    validate_bad_request(code, success, statusCode)

    assert_code(ErrorCode.EmptyParameter, code)
    assert result == list(fieldVals.keys())


def assert_success(code, success, statusCode):
    assert statusCode == 200, 'Server returned an incorrect status code'
    assert success and code is ErrorCode.Success, 'Server returned an invalid failure'
def assert_failure(code, success):  # noqa:E302
    assert not success and code is not ErrorCode.Success
def assert_code(expectedCode, receivedCode):  # noqa:E302
    assert receivedCode is expectedCode, 'The server returned an invalid code'


def validate_user_dict(app, userData, returnedUserData):
    with app.app_context():
        returnedUser = User(**returnedUserData)
        assert returnedUser.registered is not None
        assert returnedUser.displayName == userData['displayName']
        assert returnedUser.email == userData['email']
        assert returnedUser.role == userData['role'] if 'role' in userData else 'user'

        if 'id' in userData:
            assert returnedUser.id == userData['id']
        else:
            assert returnedUser.id is not None

        dbUser = User.query.filter(User.id == returnedUser.id).first()
        assert dbUser is not None, 'Insert failed'
        assert dbUser.email == returnedUser.email


def validate_bad_request(code, success, statusCode):
    assert statusCode == 400, 'Server returned an incorrect status code'
    assert_failure(code, success)
