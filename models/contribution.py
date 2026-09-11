# contribution
import datetime


class Contribution:
    def __init__(self, member, amount, date=None):
        self.member = member
        self.amount = amount
        self.date = date if date is not None else datetime.date.today()