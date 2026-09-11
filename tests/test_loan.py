# test loans
from models.loan import Loan
from models.member import Member
from models.contribution import Contribution
from auth import secure_password
import pytest

interest_rate = 0.05  # 5% interest rate


class TestLoan:
    @pytest.fixture
    def member(
        self,
    ):
        salt, hashed = secure_password("pass1234")
        return Member(name="Wanjiru", role="member", salt=salt, password=hashed)

    @pytest.fixture
    def loan(self, member):
        return Loan(
            member=member,
            amount=0.0,
            interest_rate=interest_rate,
        )

    @pytest.fixture
    def contribution(self, member):
        return Contribution(member=member, amount=0, date=None)

    def test_loan_balance(
        self,
        member,
    ):
        member.contribute(10000)
        member.request_loan(10000, interest_rate)
        assert member.loan_balance == (10000 * (1 + interest_rate))

    def test_loan_repayment(
        self,
        member,
    ):
        member.contribute(10000)
        member.request_loan(10000, interest_rate)
        assert member.loan_balance == (10000 * (1 + interest_rate))
        member.repay_loan(5000)
        assert member.loan_balance == (10000 * (1 + interest_rate)) - 5000

    def test_loan_is_active(
        self,
        member,
    ):
        member.contribute(10000)
        member.request_loan(10000, interest_rate)
        assert member.is_loan_active() is True
        member.repay_loan(5000)
        assert member.is_loan_active() is True
        member.repay_loan(5500)
        assert member.is_loan_active() is False
