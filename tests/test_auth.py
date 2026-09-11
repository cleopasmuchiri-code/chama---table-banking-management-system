# auth tests
import pytest
from models.member import Member
from auth import secure_password, verify_password


class TestAuth:
    def test_correct_password_verifies(self):
        salt, hashed = secure_password("pass1234")
        assert verify_password("pass1234", salt, hashed) is True

    def test_wrong_password_fails(self):
        salt, hashed = secure_password("pass1234")
        assert verify_password("wrongpass", salt, hashed) is False
