from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey

from roomiez_server import DB
from roomiez_server.helpers import dates


class User(DB.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    displayName = Column(String(50), nullable=False)
    email = Column(String(60), nullable=False, unique=True)
    password = Column(String(254), nullable=False)
    registered = Column(DateTime(timezone=True), nullable=False, default=dates.utcnow())
    role = Column(String(10), nullable=False, default='user')
    householdId = Column(Integer, ForeignKey('households.id', onupdate="CASCADE", ondelete="SET NULL"), index=True)
    householdCreator = Column(Boolean, nullable=False, default=False)

    def __init__(self, id=None, displayName=None, email=None, password=None,
                 registered=None, role=None, householdId=None, householdCreator=None):
        if id is not None:
            self.id = id
        self.displayName = displayName
        self.email = email
        self.password = password
        self.registered = registered
        if isinstance(registered, str):
            self.registered = dates.parse_iso(registered)
        else:
            self.registered = registered
        self.role = role
        self.householdId = householdId
        self.householdCreator = householdCreator

    def get_api_dict(self, privacy=True):
        result = {
            'id': self.id,
            'displayName': self.displayName,
            'registered': str(self.registered),
        }
        if not privacy:
            result['role'] = self.role
            result['email'] = self.email
            result['householdId'] = self.householdId
            result['householdCreator'] = self.householdCreator
        return result
