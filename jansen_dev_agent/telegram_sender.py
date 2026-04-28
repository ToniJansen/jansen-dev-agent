from __future__ import annotations
import os
import requests

_API = "https://api.telegram.org/bot{token}/sendMessage"
_MAX = 4096


def send(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    for chunk in [text[i : i + _MAX] for i in range(0, len(text), _MAX)]:
        r = requests.post(
            _API.format(token=token),
            json={"chat_id": chat_id, "text": chunk, "parse_mode": "Markdown"},
            timeout=10,
        )
        if r.status_code == 400:
            # Retry without parse_mode — LLM output may contain invalid Markdown
            requests.post(
                _API.format(token=token),
                json={"chat_id": chat_id, "text": chunk},
                timeout=10,
            ).raise_for_status()
        else:
            r.raise_for_status()
