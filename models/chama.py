import math
import datetime


class Chama:
    def __init__(
        self, name, target_amount, deadline, frequency, interest_rate, members=None
    ):
        self.name = name
        self.target_amount = target_amount
        self.deadline = deadline
        self.frequency = frequency
        self.interest_rate = interest_rate
        self.members = members if members is not None else []

    def add_member(self, member):
        self.members.append(member)

    def expected_contribution_per_member(self):
        return self.target_amount / len(self.members) if self.members else 0

    def total_saved(self):
        return sum(member.savings_balance for member in self.members)

    def progress_percentage(self):
        return (self.total_saved() / self.target_amount) * 100

    def number_of_periods(self):
        days_remaining = (self.deadline - datetime.date.today()).days
        if self.frequency == "daily":
            periods = days_remaining
        elif self.frequency == "weekly":
            periods = days_remaining // 7
        elif self.frequency == "monthly":
            periods = days_remaining // 30
        else:
            raise ValueError(f"Unknown frequency: {self.frequency}")
        return max(periods, 1)

    def expected_amount_per_period(self):
        return math.ceil(
            self.expected_contribution_per_member() / self.number_of_periods()
        )

    def to_dict(self):
        return {
            "name": self.name,
            "target_amount": self.target_amount,
            "deadline": self.deadline.isoformat(),
            "frequency": self.frequency,
            "interest_rate": self.interest_rate,
            "members": [member.to_dict() for member in self.members],
        }

    @classmethod
    def from_dict(cls, data, member_class):
        chama = cls(
            name=data["name"],
            target_amount=data["target_amount"],
            deadline=datetime.date.fromisoformat(data["deadline"]),
            frequency=data["frequency"],
            interest_rate=data["interest_rate"],
        )
        chama.members = [member_class.from_dict(m) for m in data["members"]]
        return chama