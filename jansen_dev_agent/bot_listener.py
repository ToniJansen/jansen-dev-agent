from __future__ import annotations
import asyncio
import logging
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from reviewer import review_file
from sql_reviewer import review_sql
from meeting_processor import process_meeting
from file_processor import FileTooLargeError

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("bot_listener")

OWNER_ID         = int(os.environ.get("TELEGRAM_CHAT_ID", "0"))
MAINTENANCE_FLAG = Path(__file__).parent / ".maintenance"
LARGE_FILE_BYTES = 20_000

_CODE_KEYWORDS = {"def ", "class ", "import ", "```python", "if __name__"}
_SQL_KEYWORDS  = {"select ", "insert ", "update ", "delete ", "create ", "drop ",
                  "from ", "join ", "where ", "group by", "with "}


def _detect_type(text: str) -> str:
    lower = text.lower()
    if any(kw in lower for kw in _CODE_KEYWORDS):
        return "code"
    if any(kw in lower for kw in _SQL_KEYWORDS):
        return "sql"
    return "meeting"


def _is_maintenance() -> bool:
    return MAINTENANCE_FLAG.exists()


async def _reply(update: Update, text: str) -> None:
    """Send reply with Markdown, fallback to plain text on parse error."""
    try:
        await update.message.reply_text(text, parse_mode="Markdown")
    except BadRequest:
        await update.message.reply_text(text)


async def _send_wait(update: Update, context: ContextTypes.DEFAULT_TYPE, large: bool = False) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    msg = (
        "⏳ Large file detected — condensing structure before analysis. Please wait..."
        if large else
        "⏳ Analyzing... please wait."
    )
    await update.message.reply_text(msg)


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    if _is_maintenance():
        await update.message.reply_text("🔧 Bot is under maintenance. Please try again later.")
        return
    await update.message.reply_text(
        "*@jansen\\_dev\\_agent\\_bot* ready 🤖\n\n"
        "Send me:\n"
        "• A `.py` file or code snippet → Python code review\n"
        "• A `.sql` file or SQL query → Multi-dialect SQL review\n"
        "• A meeting transcript (`.md` or text) → Action items & decisions\n\n"
        "_Scheduled: code review at 02:00 · meeting todos at 07:00_",
        parse_mode="Markdown",
    )


async def maintenance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Not authorized.")
        return
    args = context.args or []
    if args and args[0] == "on":
        MAINTENANCE_FLAG.touch()
        await update.message.reply_text("🔧 Maintenance mode ON.")
    elif args and args[0] == "off":
        MAINTENANCE_FLAG.unlink(missing_ok=True)
        await update.message.reply_text("✅ Maintenance mode OFF. Bot is live.")
    else:
        status = "ON 🔧" if _is_maintenance() else "OFF ✅"
        await update.message.reply_text(f"Maintenance is currently {status}.\nUsage: /maintenance on|off")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if _is_maintenance():
        await update.message.reply_text("🔧 Bot is under maintenance. Please try again later.")
        return

    doc = update.message.document
    file = await context.bot.get_file(doc.file_id)

    with tempfile.NamedTemporaryFile(suffix=Path(doc.file_name).suffix, delete=False) as tmp:
        await file.download_to_drive(tmp.name)
        tmp_path = tmp.name

    is_large = Path(tmp_path).stat().st_size > LARGE_FILE_BYTES
    await _send_wait(update, context, large=is_large)

    try:
        if doc.file_name.endswith(".py"):
            report = await asyncio.to_thread(review_file, tmp_path)
        elif doc.file_name.endswith(".sql"):
            report = await asyncio.to_thread(review_sql, tmp_path)
        else:
            report = await asyncio.to_thread(process_meeting, tmp_path)
        await _reply(update, report)
    except FileTooLargeError as e:
        await update.message.reply_text(f"⚠️ {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if _is_maintenance():
        await update.message.reply_text("🔧 Bot is under maintenance. Please try again later.")
        return

    text = update.message.text or ""
    if len(text) < 50:
        await update.message.reply_text(
            "Send a Python snippet, SQL query, or meeting transcript (min 50 chars)."
        )
        return

    is_large = len(text) > LARGE_FILE_BYTES
    await _send_wait(update, context, large=is_large)
    content_type = _detect_type(text)
    suffix = {"code": ".py", "sql": ".sql", "meeting": ".md"}[content_type]

    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as tmp:
        tmp.write(text)
        tmp_path = tmp.name

    try:
        if content_type == "sql":
            report = await asyncio.to_thread(review_sql, tmp_path)
        elif content_type == "code":
            report = await asyncio.to_thread(review_file, tmp_path)
        else:
            report = await asyncio.to_thread(process_meeting, tmp_path)
        await _reply(update, report)
    except FileTooLargeError as e:
        await update.message.reply_text(f"⚠️ {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def main() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("maintenance", maintenance_cmd))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    log.info("Bot listener started. Waiting for messages...")
    app.run_polling()


if __name__ == "__main__":
    main()
