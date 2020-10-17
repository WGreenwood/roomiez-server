from datetime import timezone
import dateutil.parser
from decimal import Decimal

from flask import Blueprint, g
from sqlalchemy import desc

from roomiez_server import DB
from roomiez_server.config import ErrorCode
from roomiez_server.models import Bill, BillType

from roomiez_server.helpers import api, security, validation
from roomiez_server.helpers.forms import requires_form_data

blueprint = Blueprint("bills", __name__, url_prefix="/bills")
_UPDATE_BILL_FIELDS = ['name', 'cost']
_DEFAULT_BILL_FIELDS = ['billType'] + _UPDATE_BILL_FIELDS + ['date']

def _bill_type_validator(billType):  # noqa:E302
    if not BillType.has_value(billType):
        return False, ErrorCode.InvalidBillType, None
    return True, BillType(billType), None

def _cost_validator(cost):  # noqa:E302
    if not isinstance(cost, str):
        return False, ErrorCode.InvalidCost, None
    if not validation.verify_decimal(cost):
        return False, ErrorCode.InvalidCost, None
    return True, Decimal(cost), None

def _date_validator(date):  # noqa:E302
    try:
        date = dateutil.parser.parse(date)
        if date.tzinfo is None:
            return False, ErrorCode.NoTimezoneInfo, None
        if date.tzname() != 'UTC':
            date = date.astimezone(timezone.utc)
        utcNow = validation.utcnow()
        if date > utcNow:
            return False, ErrorCode.DateInFuture, None
        return True, date, None
    except ValueError:
        return False, ErrorCode.InvalidDate, None

def _bill_id_group_validator(billIds):  # noqa:E302
    if not isinstance(billIds, list):
        return False, ErrorCode.InvalidBillIdList, None
    success = all(isinstance(billId, int) for billId in billIds)
    return success, billIds, None


def _date_validator_round2(date, billType):
    billSpan = billType.to_relativetime()
    if billSpan is not None:
        utcNow = validation.utcnow()
        nextSpan = date + billSpan
        if nextSpan < utcNow:
            return False, ErrorCode.DateNotCurrentCycle
    return True, ErrorCode.Success


_BILLID_LIST_VALIDATOR = {
    'billIds': _bill_id_group_validator,
}
_UPDATE_BILL_FIELD_VALIDATORS = {
    'cost': _cost_validator,
}
_DEFAULT_FIELD_VALIDATORS = {
    'billType': _bill_type_validator,
    'date': _date_validator,
    **_UPDATE_BILL_FIELD_VALIDATORS
}


def _get_bill(billId):
    return Bill.query.filter(Bill.id == billId).first()
def _delete_bill(billId):  # noqa:E302
    bill = _get_bill(billId)
    if bill is None or bill.householdId != g.user.householdId:
        return False
    DB.session.delete(bill)
    return True


@blueprint.route('/', methods=['GET'])
@blueprint.route('/page/<int:page>', methods=['GET'])
@security.protected_route
def read_bills(page=1):
    def billMap(bill): return bill.get_api_dict()
    return api.paginate(Bill.query.filter(Bill.householdId == g.user.householdId).order_by(desc(Bill.date)), billMap, page)


@blueprint.route('/', methods=['POST'])
@security.protected_route
@requires_form_data(fields=_DEFAULT_BILL_FIELDS, customValidators=_DEFAULT_FIELD_VALIDATORS)
def create_bill(formData=None):
    billType, name, cost, date = formData

    isOk, code = _date_validator_round2(date, billType)
    if not isOk: return api.bad_request(code)  # noqa:E701

    try:
        bill = Bill(type=billType, name=name, householdId=g.user.householdId, cost=cost, date=date)
        DB.session.add(bill)
        DB.session.commit()  # Commit so the new bill id is retrieved

        cycle = bill.create_current_billing_cycle()
        DB.session.add(cycle)
        DB.session.commit()
        return api.success(bill.get_api_dict())
    except Exception as ex:
        print("Exception on bill insert: {}".format(ex))
        return api.server_error()


@blueprint.route('/', methods=['DELETE'])
@security.protected_route
@requires_form_data(fields=['billIds'], customValidators=_BILLID_LIST_VALIDATOR)
def delete_bills(formData=None):
    billIds = formData[0]
    deletedBills = {}
    try:
        for billId in billIds:
            if _delete_bill(billId):
                deletedBills[billId] = True
            else:
                deletedBills[billId] = False
        DB.session.commit()
        return api.success({'deleted': deletedBills})
    except Exception as ex:
        print("Unexpected exception deleting bills: {}".format(ex))
        return api.server_error()


@blueprint.route('/<int:billId>', methods=['GET'])
@security.protected_route
def read_bill(billId):
    bill = _get_bill(billId)
    if bill is None: return api.not_found()  # noqa:E701
    return api.success(bill.get_api_dict())


@blueprint.route('/<int:billId>', methods=['POST'])
@security.protected_route
@requires_form_data(fields=_UPDATE_BILL_FIELDS, customValidators=_UPDATE_BILL_FIELD_VALIDATORS)
def update_bill(billId, formData=None):
    name, cost = formData
    bill = _get_bill(billId)
    if bill is None: return api.not_found()  # noqa:E701
    bill.name = name
    bill.cost = cost
    try:
        DB.session.add(bill)
        DB.session.commit()
        return api.success(bill.get_api_dict())
    except Exception as ex:
        print("Unexpected exception updating bill {}: {}".format(billId, ex))
        return api.server_error()


@blueprint.route('/<int:billId>', methods=['DELETE'])
@security.protected_route
def delete_bill(billId):
    try:
        if not _delete_bill(billId): return api.not_found()  # noqa:E701
        DB.session.commit()
        return api.success({'deleted': True})
    except Exception as ex:
        print("Unexpected exception deleting bill {}: {}".format(billId, ex))
        return api.success({'deleted': False})
