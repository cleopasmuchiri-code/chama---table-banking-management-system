import json
from models.chama import Chama
from models.member import Member


def save_chama(chama, filepath="data/chama.json"):
    with open(filepath, "w") as f:
        json.dump(chama.to_dict(), f, indent=2)


def load_chama(filepath="data/chama.json"):
    with open(filepath, "r") as f:
        data = json.load(f)
    return Chama.from_dict(data, Member)
