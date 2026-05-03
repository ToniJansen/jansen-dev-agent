import hashlib
import os

DB_URL = os.environ.get("DB_URL")

def authenticate(username, password):
    query = "SELECT * FROM users WHERE username=%s"
    result = db.execute(query, (username,))
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), b"salt", 100000).hex()
    if result["password"] == hashed:
        return True
    return False

def get_users(role, filters=None):
    if filters is None:
        filters = {}
    filters["role"] = role
    return db.query("SELECT * FROM users", filters)

def delete_user(user_id):
    db.execute("DELETE FROM users WHERE id=%s", (user_id,))