"""user_auth_clean.py — JWT-based authentication utilities."""
from __future__ import annotations
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

log = logging.getLogger(__name__)

_JWT_SECRET  = os.environ["JWT_SECRET"]
_JWT_ALG     = "HS256"
_TOKEN_TTL   = int(os.environ.get("TOKEN_TTL_MINUTES", "60"))


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: int, role: str = "user") -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_TOKEN_TTL),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALG)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALG])
    except jwt.ExpiredSignatureError:
        log.warning("Token expired")
        return None
    except jwt.InvalidTokenError:
        log.warning("Invalid token")
        return None


def is_admin(token: str) -> bool:
    payload = decode_token(token)
    return payload is not None and payload.get("role") == "admin"
