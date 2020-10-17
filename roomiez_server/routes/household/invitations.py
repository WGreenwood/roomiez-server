from flask import Blueprint, g

from roomiez_server import DB
from roomiez_server.config import ErrorCode
from roomiez_server.helpers import api, dates, forms, security, validation
from roomiez_server.models import HouseholdInvitation, User

blueprint = Blueprint('household_invitations', __name__, url_prefix='/household/invitations')


def map_invitation(invitation): return invitation.get_api_dict()


@blueprint.route('/mine', methods=['GET'])
@blueprint.route('/mine/page/<int:page>', methods=['GET'])
@security.protected_route
def get_my_invitations(page=1):
    query = HouseholdInvitation.query.filter(HouseholdInvitation.toUserId == g.user.id)
    return api.paginate(query, map_invitation, page)


@blueprint.route('/sent', methods=['GET'])
@blueprint.route('/sent/page/<int:page>', methods=['GET'])
@security.protected_route
@security.requires_household
def get_sent_invitations(page=1):
    query = HouseholdInvitation.query.filter(HouseholdInvitation.householdId == g.user.householdId)
    return api.paginate(query, map_invitation, page)


def _email_validator(email):  # noqa:E302
    if not validation.verify_email(email):
        return False, ErrorCode.InvalidEmail, None
    return True, email, None


_SEND_INVITATION_FIELDS = ['email', 'message']
_SEND_INVITATION_VALIDATORS = {
    'email': _email_validator,
}


@blueprint.route('/send', methods=['POST'])
@security.protected_route
@forms.requires_form_data(fields=_SEND_INVITATION_FIELDS, customValidators=_SEND_INVITATION_VALIDATORS)
@security.requires_household
def send_invitation(formData=None):
    email, message = formData
    if g.user.email.lower() == message.lower():
        return api.bad_request(ErrorCode.Self)
    toUser = User.query.filter(User.email == email).first()
    if toUser is None:
        return api.not_found()
    if toUser.householdId is not None:
        return api.bad_request(ErrorCode.AlreadyInHousehold)

    invitation = HouseholdInvitation(householdId=g.user.householdId,
                                     fromUserId=g.user.id, toUserId=toUser.id,
                                     sendTime=dates.utcnow(), message=message)
    DB.session.add(invitation)
    DB.session.commit()
    return api.success(invitation.get_api_dict())


@blueprint.route('/accept/<int:id>', methods=['POST'])
@security.protected_route
def accept_invitation(id):
    currentUser = g.user
    invitation = HouseholdInvitation.query.filter(HouseholdInvitation.id == id and HouseholdInvitation.toUserId == currentUser.id).first()
    if invitation is None:
        return api.not_found()

    currentUser = User.query.filter(User.id == currentUser.id).first()
    currentUser.householdId = invitation.householdId
    currentUser.householdCreator = False

    apiDict = invitation.household.get_api_dict()
    DB.session.add(currentUser)
    DB.session.query(HouseholdInvitation).filter(HouseholdInvitation.toUserId == currentUser.id).delete()
    DB.session.commit()

    return api.success(apiDict)


@blueprint.route('/<int:id>', methods=['DELETE'])
@security.protected_route
def reject_invitation(id):
    invitation = HouseholdInvitation.query\
                                    .filter(HouseholdInvitation.id == id)\
                                    .first()
    if invitation is None or (g.user.householdId != invitation.householdId and g.user.id != invitation.toUserId):
        return api.unauthorized()
    invitationId = invitation.id
    DB.session.delete(invitation)
    DB.session.commit()
    return api.success(invitationId)
