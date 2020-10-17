import enum
from dateutil.relativedelta import relativedelta


class BillType(enum.IntEnum):
    OneTime = 1
    Weekly = 2
    BiWeekly = 3
    Monthly = 4
    Quarterly = 5
    SemiAnually = 6
    Yearly = 7

    @classmethod
    def has_value(cls, val):
        return any(val == item.value for item in cls)

    def to_relativetime(self):
        if self is BillType.Weekly:
            return relativedelta(weeks=1)
        elif self is BillType.BiWeekly:
            return relativedelta(weeks=2)
        elif self is BillType.Monthly:
            return relativedelta(months=1)
        elif self is BillType.Quarterly:
            return relativedelta(months=4)
        elif self is BillType.SemiAnually:
            return relativedelta(months=6)
        elif self is BillType.Yearly:
            return relativedelta(years=1)
        return None
