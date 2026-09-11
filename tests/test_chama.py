import datetime
import math
import pytest

from models.chama import Chama
from models.member import Member
from auth import secure_password


class TestChama:

    @pytest.fixture
    def chama(
        self,
    ):
        return Chama(
            name="Test Chama",
            target_amount=2000000,
            deadline=datetime.date.today() + datetime.timedelta(days=30),
            frequency="weekly",
            interest_rate=0.05,
        )

    @pytest.fixture
    def members(
        self,
    ):
        salt, hashed = secure_password("pass1234")
        salt, hashed2 = secure_password("pass1234")
        return [
            Member(name="Wanjiru", role="member", salt=salt, password=hashed),
            Member(name="John", role="admin", salt=salt, password=hashed2),
        ]

    def test_chama_initialization(self, chama):
        assert chama.name == "Test Chama"
        assert chama.target_amount == 2000000
        assert chama.frequency == "weekly"
        assert chama.interest_rate == 0.05

    def test_add_member_appends_to_list(self, chama):
        salt, hashed = secure_password("pass1234")
        member = Member(name="Wanjiru", role="member", salt=salt, password=hashed)
        chama.add_member(member)

        assert member in chama.members
        assert len(chama.members) == 1

    def test_expected_contribution_per_member_calculation(self, chama, members):
        chama.members = members
        expected_contribution = chama.expected_contribution_per_member()

        assert expected_contribution == 1000000  # 2000000 / 2 members

    def test_total_saved_calculation(self, chama, members):
        chama.members = members
        total_saved = chama.total_saved()

        assert total_saved == 0  # No contributions made yet

    def test_progress_percentage_calculation(self, chama, members):
        chama.members = members

        progress_percentage = chama.progress_percentage()

        assert progress_percentage == 0  # No contributions made yet

    def test_number_of_periods(self, chama):
        days_remaining = (chama.deadline - datetime.date.today()).days
        assert days_remaining == 30

    def test_expected_amount_per_period(self, chama, members):
        chama.members = members

        expected = chama.expected_amount_per_period()

        assert expected == math.ceil(
            chama.expected_contribution_per_member() / chama.number_of_periods()
        )
