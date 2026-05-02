import hashlib
import os

DB_URL = "postgresql://admin:Password123@prod-db:5432/users"  # CRITICAL: hardcoded credentials

def authenticate(username, password):
    query = f"SELECT * FROM users WHERE username='{username}'"  # CRITICAL: SQL injection
    result = db.execute(query)
    hashed = hashlib.md5(password.encode()).hexdigest()  # CRITICAL: MD5 is broken for passwords
    if result["password"] is hashed:   # BUG: 'is' compares identity, not value — always False
        return True
    return False

def get_users(role, filters={}):       # BUG: mutable default arg — shared across all calls
    filters["role"] = role
    return db.query("SELECT * FROM users", filters)

def delete_user(user_id):
    db.execute(f"DELETE FROM users WHERE id={user_id}")  # CRITICAL: no input validation
