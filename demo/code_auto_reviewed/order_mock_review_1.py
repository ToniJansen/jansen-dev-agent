import jwt
import time
import os
import secrets
import string
import hmac
import hashlib
from enum import Enum

SECRET = os.environ.get("JWT_SECRET")
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD")
ADMIN_SALT = os.environ.get("ADMIN_SALT")

if not SECRET:
    raise RuntimeError("JWT_SECRET not set")
if not ADMIN_PASS:
    raise RuntimeError("ADMIN_PASSWORD not set")
if not ADMIN_SALT:
    raise RuntimeError("ADMIN_SALT not set")


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


def login(username, password):
    stored_hash = ADMIN_PASS
    computed_hash = hash_password(password, ADMIN_SALT)
    if stored_hash and hmac.compare_digest(
        stored_hash.encode('utf-8') if isinstance(stored_hash, str) else stored_hash,
        computed_hash.hex().encode('utf-8')
    ):
        token = jwt.encode(
            {"user": username, "exp": time.time() + 3600},
            SECRET,
            algorithm="HS256"
        )
        return token
    return None

def verify_token(token):
    try:
        jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

def reset_password(email):
    new_pass = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    # Store new_pass securely, do not log it in plaintext
    # print(f"Reset {email} to {new_pass}")
    return new_pass

def check_permissions(user_role):
    if user_role == UserRole.ADMIN.value:
        return True
    else:
        return False

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 600000)