from __future__ import annotations
import logging
import os
from groq import Groq

log = logging.getLogger(__name__)


def groq_complete(messages: list[dict], max_tokens: int = 1024) -> str:
    """Call Groq completions with automatic fallback to GROQ_API_KEY_2 on rate limit."""
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    keys = [k for k in [
        os.environ.get("GROQ_API_KEY"),
        os.environ.get("GROQ_API_KEY_2"),
    ] if k]

    last_exc: Exception | None = None
    for i, key in enumerate(keys, start=1):
        try:
            response = Groq(api_key=key).chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
            )
            if i > 1:
                log.info("groq_complete: succeeded with key %d", i)
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                log.warning("groq_complete: key %d rate-limited, trying next key", i)
                last_exc = e
                continue
            raise

    raise last_exc or RuntimeError("No Groq API keys configured")
