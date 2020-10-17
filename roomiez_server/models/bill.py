from dateutil.relativedelta import relativedelta

from sqlalchemy import Column, DateTime, DECIMAL, Enum, ForeignKey, Integer, String
from roomiez_server.helpers import dates

from roomiez_server import DB

from .bill_type import BillType
from .billing_cycle import BillingCycle


class Bill(DB.Model):
    __tablename__ = 'bills'
    id = Column(Integer, primary_key=True)
    type = Column(Enum(BillType), nullable=False, default=BillType.OneTime)
    householdId = Column(Integer,
                         ForeignKey('households.id', onupdate="CASCADE", ondelete="CASCADE"),
                         index=True, nullable=False)
    name = Column(String(25), nullable=False)
    cost = Column(DECIMAL(10, 2, asdecimal=True), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, default=dates.utcnow())

    def __init__(self, id=None, type=None, householdId=None, name=None, cost=None, date=None):
        if id is not None:
            self.id = id
        self.type = BillType(type)
        self.householdId = householdId
        self.name = name
        self.cost = cost
        self.date = date

    def _current_start_date(self, utcNow, billSpan):
        lastCycle = self.get_billing_cycle(utcNow - billSpan)
        if lastCycle is None:
            return self.date
        else:
            return lastCycle.endDate + relativedelta(days=1)

    def is_repeating(self):
        return self.type is not BillType.OneTime

    def create_current_billing_cycle(self):
        utcNow = dates.utcnow()
        billSpan = self.type.to_relativetime()
        startDate = self._current_start_date(utcNow, billSpan)
        endDate = startDate + billSpan - relativedelta(days=1)
        currentCycle = BillingCycle(billId=self.id, cost=self.cost, startDate=startDate, endDate=endDate)
        DB.session.add(currentCycle)
        DB.session.commit()
        return currentCycle

    def get_current_billing_cycle(self):
        if not self.is_repeating(): return None  # noqa:E701

        cycle = self.get_billing_cycle(dates.utcnow())
        if cycle is not None: return cycle  # noqa:E701

        return self.create_current_billing_cycle()

    def get_billing_cycle(self, dateFor):
        return BillingCycle.query.filter(BillingCycle.billId == self.id,
                                         BillingCycle.startDate <= dateFor,
                                         BillingCycle.endDate > dateFor).first()

    def get_api_dict(self):
        result = {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'householdId': self.householdId,
            'cost': str(self.cost),
            'date': str(self.date),
        }
        if self.is_repeating():
            result['cycle'] = self.get_current_billing_cycle().get_api_dict()
        return result

    def __repr__(self):
        return '<Bill: id={}, name={}, type={}, householdId={}, cost={}, date={}>'.\
            format(self.id, self.name, self.type.value, self.householdId, self.cost, self.date)
