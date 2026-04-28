from __future__ import annotations
import logging
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from reviewer import review_file
from sql_reviewer import review_sql
from code_fixer import fix_file
from github_pr import open_review_pr
from telegram_sender import send

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("overnight_agent")

PROJECT_ROOT = Path(__file__).parent.parent
REVIEW_DIR   = PROJECT_ROOT / "demo" / "code_auto_reviewed"


def _pull() -> None:
    result = subprocess.run(
        ["git", "pull", "--rebase"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    log.info("git pull: %s", result.stdout.strip() or result.stderr.strip())


def _process(target: Path) -> None:
    log.info("Reviewing: %s", target.name)

    if target.suffix == ".py":
        report = review_file(str(target))
    else:
        report = review_sql(str(target))

    send(report)
    log.info("Review delivered: %s", target.name)

    fixed = fix_file(str(target), report)
    pr_url = open_review_pr(target.name, report, fixed)
    send(f"🔗 PR: {pr_url}")
    log.info("PR opened: %s", pr_url)


def main() -> None:
    log.info("Overnight agent started.")
    _pull()

    targets = sorted(REVIEW_DIR.glob("*.py")) + sorted(REVIEW_DIR.glob("*.sql"))
    if not targets:
        log.warning("No files found in %s", REVIEW_DIR)
        send("⚠️ overnight_agent: no files found in code_auto_reviewed/")
        return

    log.info("Found %d file(s) to review.", len(targets))
    for target in targets:
        _process(target)

    log.info("Overnight agent complete.")


if __name__ == "__main__":
    main()
