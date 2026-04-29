```python
"""payment_utils_clean.py — refactored payment service utilities.

All credentials loaded from environment. No hardcoded secrets.
All HTTP calls have explicit timeouts. No unsafe operations.
"""
from __future__ import annotations
import logging
import os
from typing import Optional

import requests

log = logging.getLogger(__name__)

_PAYMENT_URL = os.environ.get("PAYMENT_SERVICE_URL", "https://pay.internal.corp/v1")
_API_KEY     = os.environ.get("PAYMENT_API_KEY", "")
TIMEOUT_SECONDS = 10  # define a named constant


def charge_card(amount: float, card_token: str) -> dict:
    """
    Charge a card with the given amount.
    
    Args:
    amount (float): The amount to charge.
    card_token (str): The token of the card to charge.
    
    Returns:
    dict: The response from the payment service.
    """
    response = requests.post(
        f"{_PAYMENT_URL}/charge",
        json={"amount": amount, "token": card_token},
        headers={"X-API-Key": _API_KEY},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    log.info("Charge completed for amount=%.2f", amount)
    return response.json()


def refund(transaction_id: str, amount: float) -> bool:
    """
    Refund a transaction with the given amount.
    
    Args:
    transaction_id (str): The ID of the transaction to refund.
    amount (float): The amount to refund.
    
    Returns:
    bool: True if the refund was successful, False otherwise.
    """
    response = requests.post(
        f"{_PAYMENT_URL}/refund",
        json={"id": transaction_id, "amount": amount},
        headers={"X-API-Key": _API_KEY},
        timeout=TIMEOUT_SECONDS,
    )
    if not response.ok:
        log.error("Refund failed: status=%d", response.status_code)
        return False
    return True


def get_balance() -> Optional[float]:
    response = requests.get(
        f"{_PAYMENT_URL}/balance",
        headers={"X-API-Key": _API_KEY},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json().get("balance")


def ping() -> bool:
    try:
        response = requests.get(f"{_PAYMENT_URL}/health", timeout=5)
        return response.ok
    except requests.RequestException:
        return False
```