from flask import Blueprint, g
from sqlalchemy import desc

from roomiez_server.config import ErrorCode
from roomiez_server.helpers import api, security
from roomiez_server.models import BillingCycle


blueprint = Blueprint('billing cycles', __name__, url_prefix='/bills/<int:billId>/cycles')


@blueprint.url_defaults
def _default_url_data(endpoint, values):
    values.setdefault('billId', -1)


@blueprint.url_value_preprocessor
def _process_url_data(endpoint, values):
    g.billId = values.pop('billId')


def _check_params():
    if g.billId is None:
        return False, api.bad_request(ErrorCode.MissingParameter, ['billId'])
    return True, None


@blueprint.route('/', methods=['GET'])
@blueprint.route('/page/<int:page>', methods=['GET'])
@security.protected_route
def read_cycles(page=1):
    isOk, err = _check_params()
    if not isOk:
        return err

    def billCycleMap(billCycle): return billCycle.get_api_dict()
    query = BillingCycle.query.filter(BillingCycle.billId == g.billId).order_by(desc(BillingCycle.startDate))
    return api.paginate(query, billCycleMap, page)


@blueprint.route('/<int:cycleId>', methods=['GET'])
@security.protected_route
def read_cycle(cycleId):
    isOk, err = _check_params()
    if not isOk:
        return err

    billCycle = BillingCycle.query.filter(BillingCycle.id == cycleId).first()
    if billCycle is None: return api.not_found()  # noqa:E701
    return api.success(billCycle.get_api_dict())
