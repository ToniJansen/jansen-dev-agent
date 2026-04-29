"""Security regression tests — run by overnight_agent before/after code fix.

Set TEST_TARGET env var to the Python file under test.
"""
from __future__ import annotations
import os
import re
from pathlib import Path

import pytest

_TARGET = Path(os.environ.get(
    "TEST_TARGET",
    str(Path(__file__).parent.parent / "code_auto_reviewed" / "order_manager.py"),
))


def _src() -> str:
    return _TARGET.read_text(encoding="utf-8")


# ── Hardcoded credentials ──────────────────────────────────────────────────

_SECRET_PATTERNS = [
    (r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]{4,}['\"]", "hardcoded password"),
    (r"(?i)(secret|api_key|apikey)\s*=\s*['\"][^'\"]{6,}['\"]", "hardcoded secret/key"),
    (r"sk_(live|prod|test)_[A-Za-z0-9]+", "Stripe-style live key"),
    (r"whsec_[A-Za-z0-9]+", "webhook secret"),
]


@pytest.mark.parametrize("pattern,label", _SECRET_PATTERNS)
def test_no_hardcoded_secrets(pattern, label):
    """No credentials hardcoded in source."""
    match = re.search(pattern, _src())
    assert match is None, f"{label} detected: {match.group()!r}"


# ── SQL injection ─────────────────────────────────────────────────────────

def test_no_sql_fstring():
    """SQL queries must not use f-strings."""
    matches = re.findall(
        r'f["\'].*?(?:SELECT|INSERT|UPDATE|DELETE|DROP).*?["\']',
        _src(), re.IGNORECASE,
    )
    assert not matches, f"SQL injection risk — f-string in query: {matches}"


def test_no_sql_percent_format():
    """SQL queries must not use % string formatting."""
    src = _src()
    assert '"%s"' not in src and "% (" not in src, \
        "SQL injection risk — % formatting in SQL query"


# ── Command injection ─────────────────────────────────────────────────────

def test_no_os_system():
    """os.system() must not be used — use subprocess.run() with a list."""
    assert "os.system(" not in _src(), \
        "Command injection risk — os.system() found"


# ── Unsafe deserialization ────────────────────────────────────────────────

def test_no_pickle_load():
    """pickle.load() allows arbitrary code execution and must not be used."""
    assert "pickle.load(" not in _src(), \
        "Unsafe deserialization — pickle.load() found"


# ── Path traversal ────────────────────────────────────────────────────────

def test_no_path_concatenation():
    """File paths must not be built by concatenating a constant + user input."""
    assert not re.search(r'[A-Z_]{3,}\s*\+\s*["\'/]', _src()), \
        "Path traversal risk — directory constant concatenated with string"


# ── Network safety ────────────────────────────────────────────────────────

def test_requests_have_timeout():
    """Every requests call must specify a timeout."""
    src = _src()
    calls = re.findall(r'requests\.(get|post|put|patch|delete)\(', src)
    timeouts = re.findall(r'timeout\s*=', src)
    assert len(timeouts) >= len(calls), (
        f"Missing timeout — {len(calls)} request call(s), "
        f"only {len(timeouts)} timeout(s) found"
    )
