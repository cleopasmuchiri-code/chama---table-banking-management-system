from models.loan import Loan
from models.contribution import Contribution


class Member:
    def __init__(self, name, role, salt, password, contributions=None):
        self.name = name
        self.role = role
        self.salt = salt
        self.password = password
        self.savings_balance = 0
        self.loan_balance = 0
        self.contributions = contributions if contributions is not None else []
        self.loan = None

        # only for the auto generated account
        self.must_reset_password = True

    def contribute(self, amount):
        if amount <= 0:
            raise ValueError("Contribution amount must be positive")
        self.savings_balance += amount
        self.contributions.append(Contribution(member=self, amount=amount))

    def request_loan(self, amount, interest_rate):
        loan_limit = self.savings_balance * 3
        if amount > loan_limit:
            raise ValueError(
                f"Requested amount {amount} exceeds loan limit of {loan_limit}"
            )
        self.loan = Loan(member=self, amount=amount, interest_rate=interest_rate)
        self.loan_balance = self.loan.loan_balance()

    def repay_loan(self, amount):
        if self.loan is not None and self.is_loan_active():
            self.loan.repay(amount)
            self.loan_balance = self.loan.loan_balance()

    def is_loan_active(self):
        if self.loan is None:
            return False
        return self.loan.is_loan_active()

    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "salt": self.salt,
            "password": self.password,
            "savings_balance": self.savings_balance,
            "loan_balance": self.loan_balance,
            "loan": self.loan.to_dict() if self.loan is not None else None,
            "must_reset_password": self.must_reset_password,
        }

    @classmethod
    def from_dict(cls, data):
        member = cls(
            name=data["name"],
            role=data["role"],
            salt=data["salt"],
            password=data["password"],
        )
        member.savings_balance = data["savings_balance"]
        member.loan_balance = data["loan_balance"]
        if data.get("loan") is not None:
            member.loan = Loan.from_dict(member, data["loan"])
        member.must_reset_password = data["must_reset_password"]
        return member
