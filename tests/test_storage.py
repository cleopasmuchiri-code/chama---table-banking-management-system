from models.chama import Chama
from models.member import Member
from storage import save_chama, load_chama
from auth import secure_password
import datetime


def test_save_and_load(tmp_path):
    filepath = tmp_path / "chama.json"

    chama = Chama(
        name="Test",
        target_amount=100000,
        deadline=datetime.date(2026, 12, 31),
        frequency="monthly",
        interest_rate=0.05,
    )
    salt, hashed = secure_password("pass1234")
    member = Member(name="Wanjiru", role="member", salt=salt, password=hashed)
    member.contribute(5000)
    chama.add_member(member)

    save_chama(chama, filepath=str(filepath))
    reloaded = load_chama(filepath=str(filepath))

    assert reloaded.name == "Test"
    assert reloaded.members[0].savings_balance == 5000
