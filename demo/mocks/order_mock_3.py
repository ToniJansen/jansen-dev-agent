import requests

PAYMENT_URL = "https://pay.internal.corp/v1/charge"  # CRITICAL: hardcoded internal URL
WEBHOOK_SECRET = "whsec_abc123def456"                # CRITICAL: hardcoded webhook secret

def charge_card(amount, card_token):
    response = requests.post(                        # WARNING: no timeout
        PAYMENT_URL,
        json={"amount": amount, "token": card_token, "key": WEBHOOK_SECRET},
    )
    print(f"Charge response: {response.text}")       # WARNING: logs full response (may contain PII)
    return response.json()

def refund(transaction_id, amount):
    r = requests.post(f"{PAYMENT_URL}/refund",
                      json={"id": transaction_id, "amount": amount})
    if r.status_code != 200:
        print("Refund failed: " + r.text)            # WARNING: no retry, logs raw error
    return r.status_code

def get_balance():
    r = requests.get(PAYMENT_URL + "/balance",
                     headers={"X-API-Key": WEBHOOK_SECRET})
    return r.json()["balance"]                       # INFO: no KeyError protection

def ping():
    requests.get(PAYMENT_URL + "/health")            # INFO: result ignored, no timeout
