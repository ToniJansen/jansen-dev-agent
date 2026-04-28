from __future__ import annotations
import logging
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from meeting_processor import process_meeting
from telegram_sender import send

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("morning_agent")


def main() -> None:
    meetings_dir = Path(os.environ.get("MEETINGS_DIR", "../demo/meetings")).resolve()
    processed_dir = meetings_dir / "processed"
    processed_dir.mkdir(exist_ok=True)

    files = list(meetings_dir.glob("*.md"))
    if not files:
        log.info("No new meeting files found in %s", meetings_dir)
        return

    for meeting_file in files:
        log.info("Processing: %s", meeting_file.name)
        report = process_meeting(str(meeting_file))
        send(report)
        shutil.move(str(meeting_file), str(processed_dir / meeting_file.name))
        log.info("Processed and archived: %s", meeting_file.name)

    log.info("Morning agent complete. %d meeting(s) processed.", len(files))


if __name__ == "__main__":
    main()
