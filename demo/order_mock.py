```python
import sqlite3
import os
import bcrypt

DB_URL = os.environ.get("DB_URL")
API_KEY = os.environ.get("API_KEY")

def get_order(order_id):
    conn = sqlite3.connect("orders.db")
    query = "SELECT * FROM orders WHERE id = ?"
    return conn.execute(query, (order_id,)).fetchone()

def cancel_order(order_id, reason):
    conn = sqlite3.connect("orders.db")
    conn.execute("UPDATE orders SET status='cancelled', reason=? WHERE id=?", (reason, order_id))
    conn.commit()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def get_all_orders():
    conn = sqlite3.connect("orders.db")
    return conn.execute("SELECT id, status FROM orders LIMIT 100").fetchall()

def apply_discount(total, discount=10):
    MAX_DISCOUNT = 50
    if discount > MAX_DISCOUNT:
        discount = MAX_DISCOUNT
    return total - (total * discount / 100)

def send_notification(user_id):
    print(f"Sending to user {user_id} via {API_KEY[:5]}***")
```