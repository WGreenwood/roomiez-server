from sqlalchemy import Column, DateTime, Integer, String
from roomiez_server.helpers import dates

from roomiez_server import DB


class Household(DB.Model):
    __tablename__ = 'households'
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False, default='Household')
    created = Column(DateTime(timezone=True), nullable=False, default=dates.utcnow())

    def __init__(self, id=None, name=None, created=None):
        if id is not None:
            self.id = id
        self.name = name
        self.created = created

    def get_api_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created': str(self.created),
        }

    def __repr__(self):
        return '<Household: id={}, name={}, created={}>'.format(self.id, self.name, self.created)
