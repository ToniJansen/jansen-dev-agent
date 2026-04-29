"""notification_service_clean.py — multi-channel notification dispatcher."""
from __future__ import annotations
import logging
import os
from typing import Literal

import requests

log = logging.getLogger(__name__)

_SLACK_URL   = os.environ.get("SLACK_WEBHOOK_URL", "")
_SMTP_HOST   = os.environ.get("SMTP_HOST", "smtp.gmail.com")
_SMTP_TOKEN  = os.environ.get("SMTP_API_TOKEN", "")
_TIMEOUT     = 10

Channel = Literal["slack", "email", "sms"]


def notify_slack(message: str) -> bool:
    if not _SLACK_URL:
        log.warning("SLACK_WEBHOOK_URL not configured")
        return False
    r = requests.post(_SLACK_URL, json={"text": message}, timeout=_TIMEOUT)
    if not r.ok:
        log.error("Slack notify failed: %d", r.status_code)
        return False
    log.info("Slack notification sent")
    return True


def notify_email(to: str, subject: str, body: str) -> bool:
    api_url = f"https://{_SMTP_HOST}/v1/send"
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
