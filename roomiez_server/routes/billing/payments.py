from decimal import Decimal
from flask import Blueprint, g
from sqlalchemy import desc

from roomiez_server import DB
from roomiez_server.config import ErrorCode
from roomiez_server.helpers import api, security, validation
from roomiez_server.helpers.forms import requires_form_data
from roomiez_server.models import Bill, BillPayment

cycle_payments_blueprint = Blueprint('bill_cycle_payments', __name__,
    url_prefix='/bills/<int:billId>/cycles/<int:cycleId>/payments')  # noqa:E128
bill_payments_blueprint = Blueprint('bill_payments', __name__,
    url_prefix='/bills/<int:billId>/payments')  # noqa:E128


@cycle_payments_blueprint.url_defaults
def _default_cycle_data(endpoint, values):
    values.setdefault('billId', -1)
    values.setdefault('cycleId', -1)


@cycle_payments_blueprint.url_value_preprocessor
def _process_cycle_data(endpoint, values):
    g.billId = values.pop('billId')
    g.cycleId = values.pop('cycleId')


@bill_payments_blueprint.url_defaults
def _default_bill_data(endpoint, values):
    values.setdefault('billId', -1)


@bill_payments_blueprint.url_value_preprocessor
def _process_bill_data(endpoint, values):
    g.billId = values.pop('billId')


def _check_params(useCycleId):
    missingParams = []
    if g.billId == -1:
        missingParams.append('billId')
    if useCycleId and g.cycleId == -1:
        missingParams.append('cycleId')
    if len(missingParams) != 0:
        return False, api.bad_request(ErrorCode.MissingParameter, missingParams)
    return True, None


def map_payment_dict(payment):
    return payment.get_api_dict()


@cycle_payments_blueprint.route('/', methods=['GET'])
@cycle_payments_blueprint.route('/page/<int:page>', methods=['GET'])
@security.protected_route
def read_cycle_payments(page=1):
    isOk, err = _check_params(True)
    if not isOk:
        return err

    query = BillPayment.query.filter(BillPayment.billId == g.billId)\
                             .filter(BillPayment.billCycleId == g.cycleId)\
                             .order_by(desc(BillPayment.timestamp))
    return api.paginate(query, map_payment_dict, page)


@bill_payments_blueprint.route('/', methods=['GET'])
@bill_payments_blueprint.route('/page/<int:page>', methods=['GET'])
def read_bill_payments(page=1):
    isOk, err = _check_params(False)
    if not isOk:
        return err

    query = BillPayment.query.filter(BillPayment.billId == g.billId).order_by(desc(BillPayment.timestamp))
    return api.paginate(query, map_payment_dict, page)


def _validate_decimal(cost):
    if not validation.verify_decimal(cost):
        return False, ErrorCode.InvalidCost, None
    return True, Decimal(cost), None


_MAKE_PAYMENT_FIELDS = ['amount']
_MAKE_PAYMENT_FIELD_VALIDATORS = {
    'amount': _validate_decimal
}


@bill_payments_blueprint.route('/', methods=['POST'])
@requires_form_data(fields=_MAKE_PAYMENT_FIELDS, customValidators=_MAKE_PAYMENT_FIELD_VALIDATORS)
def make_bill_payment(formData=None):
    cost = formData[0]  # Unpack single value tuple
    userId = g.user.id
    bill = Bill.query.filter(Bill.id == g.billId).first()
    if bill is None: return api.not_found()  # noqa:E701

    currentCycle = bill.get_current_billing_cycle()
    payment = BillPayment(billId=bill.id, billCycleId=currentCycle.id, amount=cost, userId=userId)
    payment.timestamp = validation.utcnow()
    DB.session.add(payment)
    DB.session.commit()

    result = {
        'payment': payment.get_api_dict(),
        'bill': bill.get_api_dict()
    }
    return api.success(result)
