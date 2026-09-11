import os
import hashlib


def secure_password(password):
    salt = os.urandom(32)
    hashed_password = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 100000
    )
    return salt.hex(), hashed_password.hex()


def verify_password(entered_password, salt_hex, stored_hash_hex):
    salt = bytes.fromhex(salt_hex)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", entered_password.encode("utf-8"), salt, 100000
    )
    return hashed.hex() == stored_hash_hex
