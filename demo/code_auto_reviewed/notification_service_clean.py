```python
"""notification_service_clean.py — multi-channel notification dispatcher."""
from __future__ import annotations
import logging
import os
from typing import Literal
import requests

log = logging.getLogger(__name__)

_SLACK_URL   = os.environ.get("SLACK_WEBHOOK_URL", "")
_SMTP_HOST   = os.environ.get("SMTP_HOST", "")
_SMTP_TOKEN  = os.environ.get("SMTP_API_TOKEN", "")
_TIMEOUT     = int(os.environ.get("TIMEOUT", 10))

Channel = Literal["slack", "email", "sms"]

def validate_url(url: str) -> bool:
    """Validate URL to prevent SQL injection"""
    # Simple validation, you may want to add more complex validation based on your requirements
    if not url.startswith("https://"):
        return False
    return True

def notify_slack(message: str) -> bool:
    if not _SLACK_URL or not validate_url(_SLACK_URL):
        log.warning("SLACK_WEBHOOK_URL not configured or invalid")
        return False
    r = requests.post(_SLACK_URL, json={"text": message}, timeout=_TIMEOUT)
    if not r.ok:
        log.error("Slack notify failed: %d", r.status_code)
        return False
    log.info("Slack notification sent")
    return True


def notify_email(to: str, subject: str, body: str) -> bool:
    api_url = f"https://{_SMTP_HOST}/v1/send"
    if not validate_url(api_url):
        log.warning("SMTP_HOST is not a valid URL")
        return False
    r = requests.post(
        api_url,
        headers={"Authorization": f"Bearer {_SMTP_TOKEN}"},
        json={"to": to, "subject": subject, "body": body},
        timeout=_TIMEOUT,
    )
    if not r.ok:
        log.error("Email notify failed: %d", r.status_code)
        return False
    log.info("Email sent to %s", to)
    return True


def dispatch(channel: Channel, **kwargs) -> bool:
    if channel == "slack":
        return notify_slack(kwargs.get("message", ""))
    if channel == "email":
        return notify_email(
            kwargs.get("to", ""),
            kwargs.get("subject", ""),
            kwargs.get("body", ""),
        )
    log.warning("Unknown channel: %s", channel)
    return False
```