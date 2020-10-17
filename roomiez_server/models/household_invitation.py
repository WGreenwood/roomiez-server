from flask import g
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from roomiez_server import DB
from roomiez_server.helpers import dates


class HouseholdInvitation(DB.Model):
    __tablename__ = 'household_invitations'
    id = Column(Integer, primary_key=True)
    householdId = Column(Integer, ForeignKey('households.id', onupdate='CASCADE', ondelete='CASCADE'), index=True)
    fromUserId = Column(Integer, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), index=True)
    toUserId = Column(Integer, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), index=True)
    sendTime = Column(DateTime, nullable=False, default=dates.utcnow())

    message = Column(String(50), nullable=True)

    household = relationship('Household', single_parent=True, foreign_keys=[householdId])
    fromUser = relationship('User', single_parent=True, foreign_keys=[fromUserId])
    toUser = relationship('User', single_parent=True, foreign_keys=[toUserId])

    def __init__(self, id=None, householdId=None, fromUserId=None, toUserId=None, sendTime=None, message=None):
        self.id = id
        self.householdId = householdId
        self.fromUserId = fromUserId
        self.toUserId = toUserId
        self.sendTime = sendTime
        self.message = message

    def get_api_dict(self):
        userId = g.user.id
        fromUserPrivacy = userId != self.fromUserId
        toUserPrivacy = userId != self.toUserId
        return {
            'id': self.id,
            'household': self.household.get_api_dict(),
            'fromUser': self.fromUser.get_api_dict(privacy=fromUserPrivacy),
            'toUser': self.toUser.get_api_dict(privacy=toUserPrivacy),
            'sendTime': str(self.sendTime),
            'message': self.message,
        }
