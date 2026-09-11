import pytest
from models.member import Member
from models.loan import Loan
from models.contribution import Contribution
from auth import secure_password

interest_rate = 0.05  # 5% interest rate
loan_amount = 100000


class TestMember:
    @pytest.fixture
    def member(self):
        salt, hashed = secure_password("pass1234")
        return Member(
            name="Wanjiru",
            role="member",
            salt=salt,
            password=hashed,
        )

    @pytest.fixture
    def loan(self, member):
        return Loan(
            member=member,
            amount=loan_amount,
            interest_rate=interest_rate,
        )

    @pytest.fixture
    def contribution(self, member):
        return Contribution(member=member, amount=0, date=None)

    # test member initialization
    def test_member_initialization(self, member):
        assert member.name == "Wanjiru"
        assert member.role == "member"

    # test contribute method
    def test_contribute_method(self, member):
        member.contribute(5000)
        assert member.savings_balance == 5000

    # test contribution of a negative amount
    def test_contribute_negative_raises_error(self, member):
        with pytest.raises(ValueError):
            member.contribute(-100)

    # test request_loan method
    def test_request_loan_method(self, member):
        member.contribute(500000)
        member.request_loan(10000, interest_rate)
        assert member.loan_balance == (10000 * (1 + interest_rate))

    # test request_loan method with amount exceeding limit
    def test_request_loan_exceeding_limit(self, member):
        member.contribute(5000)

        with pytest.raises(ValueError):
            member.request_loan(100000, interest_rate)
        assert member.loan_balance == 0  # loan should not be granted

    def test_repay_loan_method(self, member):
        member.contribute(500000)
        member.request_loan(10000, interest_rate)
        member.repay_loan(5000)
        assert member.loan_balance == (10000 * (1 + interest_rate)) - 5000
