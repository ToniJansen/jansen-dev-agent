from __future__ import annotations
import logging
import os
import anthropic
from groq import Groq

log = logging.getLogger(__name__)

_anthropic_client: anthropic.Anthropic | None = None


def _get_anthropic() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _anthropic_client


def _call_anthropic(messages: list[dict], max_tokens: int) -> str:
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    system: str | None = None
    chat: list[dict] = []
    for msg in messages:
        if msg["role"] == "system":
            system = msg["content"]
        else:
            chat.append({"role": msg["role"], "content": msg["content"]})
    kwargs: dict = {"model": model, "max_tokens": max_tokens, "messages": chat}
    if system:
        kwargs["system"] = system
    response = _get_anthropic().messages.create(**kwargs)
    return response.content[0].text


def _call_groq(messages: list[dict], max_tokens: int) -> str:
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    keys = [k for k in [
        os.environ.get("GROQ_API_KEY"),
        os.environ.get("GROQ_API_KEY_2"),
        os.environ.get("GROQ_API_KEY_3"),
    ] if k]
    last_exc: Exception | None = None
    for i, key in enumerate(keys, start=1):
        try:
            response = Groq(api_key=key).chat.completions.create(
                model=model, max_tokens=max_tokens, messages=messages,
            )
            if i > 1:
                log.info("groq fallback: succeeded with key %d", i)
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                log.warning("groq fallback: key %d rate-limited, trying next", i)
                last_exc = e
                continue
            raise
    raise last_exc or RuntimeError("No Groq API keys available")


def groq_complete(messages: list[dict], max_tokens: int = 1024) -> str:
    """Call Anthropic Claude; fall back to Groq if credits are exhausted."""
    try:
        return _call_anthropic(messages, max_tokens)
    except Exception as e:
        log.warning("Anthropic failed (%s), falling back to Groq", e)
        return _call_groq(messages, max_tokens)
