"""inventory_service.py — basic stock management utilities."""
from __future__ import annotations
import logging
import os

from sqlite3 import Connection

log = logging.getLogger(__name__)


def get_stock(product_id: str, db: Connection) -> int:
    row = db.execute(
        "SELECT quantity FROM inventory WHERE product_id = %s", (product_id,)
    ).fetchone()
    return row["quantity"] if row else 0


def reserve_stock(product_id: str, quantity: int, db: Connection) -> bool:
    if quantity <= 0:
        raise ValueError("quantity must be positive")

    # Use SELECT ... FOR UPDATE to prevent race conditions between read and update
    row = db.execute(
        "SELECT quantity FROM inventory WHERE product_id = %s FOR UPDATE",
        (product_id,),
    ).fetchone()

    if row is None:
        log.warning("product %s not found in inventory", product_id)
        return False

    current = row["quantity"]
    if current < quantity:
        log.warning(
            "insufficient stock for %s: have %d, need %d",
            product_id,
            current,
            quantity,
        )
        return False

    cursor = db.execute(
        "UPDATE inventory SET quantity = quantity - %s WHERE product_id = %s",
        (quantity, product_id),
    )

    # Check that the UPDATE actually affected a row
    if cursor.rowcount == 0:
        log.warning("UPDATE affected 0 rows for product_id %s", product_id)
        return False

    return True


def is_low_stock(product_id: str, db: Connection) -> bool:
    threshold = int(os.environ.get("LOW_STOCK_THRESHOLD", "10"))
    return get_stock(product_id, db) < threshold