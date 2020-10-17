from flask import Blueprint, g

from roomiez_server import DB
from roomiez_server.config import ErrorCode
from roomiez_server.helpers import api, security, validation
from roomiez_server.helpers.forms import requires_form_data
from roomiez_server.models import Household, User

blueprint = Blueprint('household_base', __name__, url_prefix='/household')
_NEW_HOUSEHOLD_FIELDS = ['name']


@blueprint.route('/mine', methods=['GET'])
@security.protected_route
@security.requires_household
def my_household():
    household = Household.query.filter(Household.id == g.user.householdId).first()
    if household is None:
        return api.not_found()
    else:
        return api.success(household.get_api_dict())


@blueprint.route('/', methods=['POST'])
@security.protected_route
@requires_form_data(fields=_NEW_HOUSEHOLD_FIELDS)
def new_household(formData=None):
    name = formData[0]
    user = User.query.filter(User.id == g.user.id).first()

    if user.householdId is not None:
        return api.bad_request(ErrorCode.AlreadyInHousehold)

    household = Household(name=name, created=validation.utcnow())
    try:
        DB.session.add(household)
        DB.session.commit()

        user.householdId = household.id
        user.householdCreator = True
        DB.session.add(household)
        DB.session.commit()
        return api.success(household.get_api_dict())
    except Exception as ex:
        print("Unexpected exception on household insert: {}".format(ex))
        return api.server_error()


@blueprint.route('/people', methods=['GET'])
@security.protected_route
@security.requires_household
def get_household_users():
    if g.user.householdId is None:
        return api.not_found()

    users = User.query.filter(User.householdId == g.user.householdId and User.id != g.user.id).all()
    return api.success({'users': [user.get_api_dict() for user in users]})


@blueprint.route('/<int:householdId>', methods=['POST'])
@security.protected_route
@security.requires_household
@requires_form_data(fields=_NEW_HOUSEHOLD_FIELDS)
def update_household(householdId, formData=None):
    name = formData[0]
    user = g.user

    if householdId != user.householdId:
        return api.unauthorized()

    household = Household.query.filter(Household.id == householdId).first()
    household.name = name

    try:
        DB.session.add(household)
        DB.session.commit()
        return api.success(household.get_api_dict())
    except Exception as ex:
        print("Error updaing household {}: {}".format(householdId, ex))
        return api.server_error()


@blueprint.route('/leave', methods=['POST'])
@security.protected_route
@security.requires_household
def leave_household():
    try:
        user = User.query.filter(User.id == g.user.id).first()
        if user.householdId is None:
            return api.not_found()

        if user.householdCreator:
            pass  # Some kind of extra check to make sure household is empty or something

        user.householdId = None
        user.householdCreator = False
        DB.session.add(user)
        DB.session.commit()
    except Exception as ex:
        print("Error leaving household {}: {}".format(g.user.householdId, ex))
        return api.server_error()


@blueprint.route('/remove/<int:userId>', methods=['DELETE'])
@security.protected_route
@security.requires_household
def remove_from_household(userId):
    try:
        currentUser = g.user
        if not currentUser.householdCreator:
            return api.unauthorized()
        user = User.query.filter(User.id == userId and User.householdId == currentUser.householdId).first()
        if user is None:
            return api.not_found()
    except Exception as ex:
        print("Error removing user {} from household {}: {}".format(userId, g.user.householdId, ex))
        return api.server_error()
