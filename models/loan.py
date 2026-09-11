# models


class Loan:
    def __init__(self, member, amount, interest_rate):
        self.member = member
        self.amount = amount
        self.interest_rate = interest_rate
        self.balance = amount * (1 + interest_rate)
        self.active = True

    # method to calculate the total amount to be repaid including interest
    def loan_balance(self):
        return self.balance

    # method to apply a repayment and reduce what's still owed
    def repay(self, amount):
        self.balance -= amount
        # once fully paid off remove the loan
        if self.balance <= 0:
            self.balance = 0
            self.active = False

    # method to check if loan is active
    def is_loan_active(self):
        return self.active

    # loan.py — add these two methods
    def to_dict(self):
        return {
            "amount": self.amount,
            "interest_rate": self.interest_rate,
            "balance": self.balance,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, member, data):
        loan = cls(
            member=member, amount=data["amount"], interest_rate=data["interest_rate"]
        )
        loan.balance = data["balance"]
        loan.active = data["active"]
        return loan