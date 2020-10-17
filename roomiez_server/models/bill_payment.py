from sqlalchemy import Column, DECIMAL, Integer, ForeignKey, DateTime
from roomiez_server import DB
from roomiez_server.helpers import dates


class BillPayment(DB.Model):
    __tablename__ = 'bill_payments'
    id = Column(Integer, primary_key=True)
    billId = Column(Integer, ForeignKey('bills.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    billCycleId = Column(Integer, ForeignKey('billing_cycles.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    userId = Column(Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="SET NULL"))

    amount = Column(DECIMAL(10, 2, asdecimal=True), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=dates.utcnow())

    def __init__(self, id=None, billId=None, billCycleId=None, userId=None, amount=None):
        if id is not None:
            self.id = id
        self.billId = billId
        self.billCycleId = billCycleId
        self.userId = userId
        self.amount = amount
        self.timestamp = None

    def get_api_dict(self):
        return {
            'id': self.id,
            'billId': self.billId,
            'billCycleId': self.billCycleId,
            'userId': self.userId,
            'amount': str(self.amount),
            'timestamp': self.timestamp
        }

    def __repr__(self):
        return '<BillPayment: id={}, billId={}, billCycleId={}, userId={}, amount={}, timestamp={}>'.\
            format(self.id, self.billId, self.billCycleId, self.userId, self.amount, self.timestamp)
