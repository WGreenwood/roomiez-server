from decimal import Decimal
from sqlalchemy import Column, Date, DECIMAL, Integer, ForeignKey
from sqlalchemy.orm import relationship

from roomiez_server import DB
from roomiez_server.helpers import dates
from .bill_payment import BillPayment


class BillingCycle(DB.Model):
    __tablename__ = 'billing_cycles'

    id = Column(Integer, primary_key=True)
    billId = Column(Integer, ForeignKey('bills.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    bill = relationship('Bill', uselist=False, single_parent=True, cascade="all, delete, delete-orphan")

    cost = Column(DECIMAL(10, 2, asdecimal=True), nullable=False)
    startDate = Column(Date, nullable=False)
    endDate = Column(Date)

    _paidAmount: Decimal = None

    def __init__(self, id=None, billId=None, cost=None, startDate=None, endDate=None):
        if id is not None:
            self.id = id
        self.billId = billId
        self.cost = cost
        self.startDate = startDate
        self.endDate = endDate
        self._paidAmount = None

    @property
    def remaining_cost(self):
        return self.cost - self.paid_amount

    @property
    def paid_amount(self):
        if self._paidAmount is None:
            paidAmount = DB.session.query(DB.func.sum(BillPayment.amount)).\
                    filter(BillPayment.billCycleId == self.id).first()[0]
            self._paidAmount = Decimal('0.00') if paidAmount is None else paidAmount
        return self._paidAmount

    @property
    def is_over(self):
        return self.endDate is not None and dates.utcnow().date() > self.endDate

    @property
    def is_paid(self):
        return self.paid_amount >= self.cost

    def get_api_dict(self):
        return {
            'id': self.id,
            'billId': self.billId,
            'cost': str(self.cost),
            'startDate': str(self.startDate),
            'endDate': str(self.endDate),
            'paidAmount': str(self.paid_amount),
            'remainingCost': str(self.remaining_cost),
            'isOver': self.is_over,
            'isPaid': self.is_paid
        }

    def __repr__(self):
        return '<BillingCycle: id={}, billId={}, cost={}, startDate={}, endDate={}>'.\
            format(self.id, self.billId, self.cost, self.startDate, self.endDate)
