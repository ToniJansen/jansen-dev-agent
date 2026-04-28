import sqlite3
import hashlib

DB_URL = "postgresql://admin:s3cr3t@prod-db:5432/orders"  # CRITICAL: hardcoded credential
API_KEY = "live_key_abc123xyz"                             # CRITICAL: hardcoded API key

def get_order(order_id):
    conn = sqlite3.connect("orders.db")
    query = f"SELECT * FROM orders WHERE id = {order_id}"  # CRITICAL: SQL injection
    return conn.execute(query).fetchone()

def cancel_order(order_id, reason):
    conn = sqlite3.connect("orders.db")
    conn.execute(f"UPDATE orders SET status='cancelled', reason='{reason}' WHERE id={order_id}")  # CRITICAL: SQL injection
    conn.commit()

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()  # WARNING: weak hash (use bcrypt)

def get_all_orders():
    conn = sqlite3.connect("orders.db")
    return conn.execute("SELECT * FROM orders").fetchall()  # WARNING: SELECT * + no LIMIT

def apply_discount(total, discount=10):
    return total - (total * discount / 100)  # WARNING: magic number, no validation

def send_notification(user_id):
    print(f"Sending to user {user_id} via {API_KEY}")  # INFO: leaks API key in log
