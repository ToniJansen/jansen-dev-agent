from __future__ import annotations
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from reviewer import review_file
from code_fixer import fix_file
from github_pr import open_review_pr
from telegram_sender import send

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("overnight_agent")


def main() -> None:
    target = os.environ.get("CODE_TARGET_FILE", "../demo/order_manager.py")
    target_path = (Path(__file__).parent / target).resolve()

    if not target_path.exists():
        log.error("Target file not found: %s", target_path)
        sys.exit(1)

    log.info("Starting overnight code review: %s", target_path.name)
    report = review_file(str(target_path))
    send(report)
    log.info("Code review report delivered.")

    log.info("Generating fixes...")
    fixed_code = fix_file(str(target_path), report)

    log.info("Opening GitHub PR...")
    pr_url = open_review_pr(target_path.name, report, fixed_code)
    send(f"🔗 PR opened: {pr_url}")
    log.info("PR opened: %s", pr_url)
    print(report)


if __name__ == "__main__":
    main()
