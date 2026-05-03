import hashlib
import os
import bcrypt

DB_URL = os.environ.get("DB_URL")

def authenticate(username, password):
    query = "SELECT * FROM users WHERE username=%s"
    result = db.execute(query, (username,))
    if bcrypt.checkpw(password.encode(), result["password"]):
        return True
    return False

def get_users(role, filters=None):
    if filters is None:
        filters = {}
    filters["role"] = role
    return db.query("SELECT * FROM users", filters)

def delete_user(user_id):
    db.execute("DELETE FROM users WHERE id=%s", (user_id,))