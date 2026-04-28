import jwt
import time

SECRET = "mysecretkey123"          # CRITICAL: hardcoded JWT secret
ADMIN_PASS = "admin123"            # CRITICAL: hardcoded password

def login(username, password):
    if password == ADMIN_PASS:     # CRITICAL: plaintext password compare
        token = jwt.encode({"user": username, "exp": time.time() + 99999999}, SECRET)
        return token
    return None

def verify_token(token):
    return jwt.decode(token, SECRET, algorithms=["HS256"])  # WARNING: no expiry check

def reset_password(email):
    new_pass = "reset123"          # WARNING: predictable reset password
    print(f"Reset {email} to {new_pass}")  # WARNING: logs password in plaintext

def check_permissions(user_role):
    if user_role == "admin":       # WARNING: magic string, use enum/const
        return True
    return False                   # INFO: missing else for non-admin roles
