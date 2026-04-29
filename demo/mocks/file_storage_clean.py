"""file_storage_clean.py — secure file upload and retrieval."""
from __future__ import annotations
import hashlib
import logging
import os
from pathlib import Path
from typing import Optional

import requests

log = logging.getLogger(__name__)

_UPLOAD_DIR  = Path(os.environ.get("UPLOAD_DIR", "/tmp/uploads"))
_STORAGE_URL = os.environ.get("STORAGE_SERVICE_URL", "https://storage.internal.corp/v1")
_API_KEY     = os.environ.get("STORAGE_API_KEY", "")
_TIMEOUT     = 10
_MAX_BYTES   = 10 * 1024 * 1024  # 10 MB


def save_upload(filename: str, data: bytes) -> Optional[Path]:
    safe_name = Path(filename).name
    if not safe_name:
        log.error("Invalid filename")
        return None
    if len(data) > _MAX_BYTES:
        log.error("File too large: %d bytes", len(data))
        return None

    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = _UPLOAD_DIR / safe_name
    dest.write_bytes(data)
    log.info("Saved upload: %s (%d bytes)", safe_name, len(data))
    return dest


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def upload_to_storage(path: Path) -> Optional[str]:
    with open(path, "rb") as f:
        r = requests.post(
            f"{_STORAGE_URL}/upload",
            headers={"X-API-Key": _API_KEY},
            files={"file": (path.name, f)},
            timeout=_TIMEOUT,
        )
    if not r.ok:
        log.error("Storage upload failed: %d", r.status_code)
        return None
    url = r.json().get("url")
    log.info("Uploaded %s → %s", path.name, url)
    return url


def delete_local(path: Path) -> None:
    path.unlink(missing_ok=True)
    log.info("Deleted local file: %s", path.name)
