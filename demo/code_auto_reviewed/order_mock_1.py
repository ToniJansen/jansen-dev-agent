```python
import jwt
import time
import os
import secrets
import string

SECRET = os.environ.get("JWT_SECRET")
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD")
ADMIN_SALT = os.environ.get("ADMIN_SALT")

def login(username, password):
    stored_password = ADMIN_PASS
    if stored_password and jwt.decode(stored_password, SECRET, algorithms=["HS256"])["password"] == hash_password(password, ADMIN_SALT):
        token = jwt.encode({"user": username, "exp": time.time() + 3600}, SECRET, algorithm="HS256")
        return token
    return None

def verify_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET, algorithms=["HS256"])
        if decoded_token["exp"] < time.time():
            return False
        return True
    except jwt.ExpiredSignatureError:
        return False

def reset_password(email):
    new_pass = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    # Store new_pass securely, do not log it in plaintext
    # print(f"Reset {email} to {new_pass}")
    return new_pass

def check_permissions(user_role):
    from enum import Enum
    class UserRole(Enum):
        ADMIN = "admin"
        USER = "user"
    if user_role == UserRole.ADMIN.value:
        return True
    else:
        return False

def hash_password(password, salt):
    import hashlib
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
```