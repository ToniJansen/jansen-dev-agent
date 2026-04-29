import requests
import os

PAYMENT_URL = os.environ.get("PAYMENT_URL")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

def charge_card(amount, card_token):
    response = requests.post(
        PAYMENT_URL,
        json={"amount": amount, "token": card_token, "key": WEBHOOK_SECRET},
        timeout=10,
    )
    print(f"Charge status: {response.status_code}")
    return response.json()

def refund(transaction_id, amount):
    r = requests.post(f"{PAYMENT_URL}/refund",
                      json={"id": transaction_id, "amount": amount},
                      timeout=10)
    if r.status_code != 200:
        print(f"Refund failed: status {r.status_code}")
    return r.status_code

def get_balance():
    r = requests.get(PAYMENT_URL + "/balance",
                     headers={"X-API-Key": WEBHOOK_SECRET})
    return r.json().get("balance")

def ping():
    result = requests.get(PAYMENT_URL + "/health", timeout=5)
    return result.status_code