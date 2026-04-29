"""transcriber.py — audio transcription via Groq Whisper."""
from __future__ import annotations
import os
import subprocess
import tempfile
from pathlib import Path

from groq import Groq

MAX_DURATION = 60  # seconds — longer audio is trimmed before sending


def _trim_audio(input_path: str) -> str:
    trimmed = input_path + "_trim.ogg"
    subprocess.run(
        ["ffmpeg", "-i", input_path, "-t", str(MAX_DURATION), "-c", "copy", "-y", trimmed],
        check=True, timeout=30, capture_output=True,
    )
    return trimmed


def transcribe(file_path: str, duration: float = 0) -> tuple[str, bool]:
    """Return (transcribed_text, was_trimmed). Language auto-detected by Whisper."""
    trimmed = duration > MAX_DURATION
    path_to_use = file_path
    trimmed_path: str | None = None

    try:
        if trimmed:
            trimmed_path = _trim_audio(file_path)
            path_to_use = trimmed_path

        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        with open(path_to_use, "rb") as f:
            result = client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3-turbo",
                response_format="text",
            )
        return str(result).strip(), trimmed
    finally:
        if trimmed_path:
            Path(trimmed_path).unlink(missing_ok=True)
