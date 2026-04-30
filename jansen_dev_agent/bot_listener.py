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
from meeting_processor import process_meeting, extract_action_items
from code_fixer import fix_file
from github_pr import open_review_pr, open_meeting_issues
from greeter import greet
from metrics import build_report
from file_processor import FileTooLargeError
from transcriber import transcribe, MAX_DURATION

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("bot_listener")

OWNER_ID         = int(os.environ.get("TELEGRAM_CHAT_ID", "0"))
MAINTENANCE_FLAG = Path(__file__).parent / ".maintenance"
LARGE_FILE_BYTES = 20_000

_CODE_KEYWORDS    = {"def ", "class ", "import ", "```python", "if __name__"}
_SQL_KEYWORDS     = {"select ", "insert ", "update ", "delete ", "create ", "drop ",
                     "from ", "join ", "where ", "group by", "with "}
_MEETING_KEYWORDS = {"action item", "decision", "agenda", "blocker", "standup",
                     "sprint", "retrospective", "attendee", "discussed", "agreed",
                     "action:", "owner:", "minutes", "pauta", "ata ",
                     "reunião", "decisão", "encaminhamento"}


def _detect_type(text: str) -> str:
    lower = text.lower()
    if any(kw in lower for kw in _CODE_KEYWORDS):
        return "code"
    if any(kw in lower for kw in _SQL_KEYWORDS):
        return "sql"
    if any(kw in lower for kw in _MEETING_KEYWORDS):
        return "meeting"
    return "greeting"


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
        "*@jansen\\_dev\\_agent\\_bot* — autonomous code review & meeting intelligence 🤖\n\n"
        "*What I can do:*\n"
        "🐍 `.py` file or Python snippet → security & quality review + auto-fix PR on GitHub\n"
        "🗄️ `.sql` file or SQL query → multi-dialect analysis (PostgreSQL, BigQuery, T-SQL…)\n"
        "📋 Meeting transcript (`.md` or text) → decisions, action items & blockers\n"
        "🎙️ Voice note or audio (up to 60s) → transcribed & routed automatically\n"
        "📊 /report → PDF metrics dashboard with live GitHub data\n\n"
        "*Running 24/7:*\n"
        "• 02:00 — overnight code review of pending files\n"
        "• 07:00 — morning processing of meeting notes",
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


async def report_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Not authorized.")
        return
    if _is_maintenance():
        await update.message.reply_text("🔧 Bot is under maintenance.")
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_document")
    await update.message.reply_text("📊 Generating metrics report, please wait...")
    try:
        pdf_path = await asyncio.to_thread(build_report)
        with open(pdf_path, "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename="jansen_dev_agent_metrics.pdf",
                caption="🤖 Agent metrics — live data from GitHub",
            )
    except Exception as e:
        log.error("report_cmd failed: %s", e)
        await update.message.reply_text(f"⚠️ Failed to generate report: {e}")


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
        # Rename temp file to original name so reviewers show the correct filename
        named_path = str(Path(tmp_path).parent / doc.file_name)
        Path(tmp_path).rename(named_path)
        tmp_path = named_path

        if doc.file_name.endswith(".py"):
            report = await asyncio.to_thread(review_file, tmp_path)
            await _reply(update, report)
            fixed = await asyncio.to_thread(fix_file, tmp_path, report)
            pr_url = await asyncio.to_thread(open_review_pr, doc.file_name, report, fixed)
            await update.message.reply_text(f"🔗 PR opened: {pr_url}")
        elif doc.file_name.endswith(".sql"):
            report = await asyncio.to_thread(review_sql, tmp_path)
            await _reply(update, report)
            fixed = await asyncio.to_thread(fix_file, tmp_path, report)
            pr_url = await asyncio.to_thread(open_review_pr, doc.file_name, report, fixed)
            await update.message.reply_text(f"🔗 PR opened: {pr_url}")
        else:
            report = await asyncio.to_thread(process_meeting, tmp_path)
            await _reply(update, report)
            items = await asyncio.to_thread(extract_action_items, tmp_path)
            if items:
                urls = await asyncio.to_thread(open_meeting_issues, items, doc.file_name)
                for url in urls:
                    await update.message.reply_text(f"📌 Issue opened: {url}")
    except FileTooLargeError as e:
        await update.message.reply_text(f"⚠️ {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


async def _process_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    content_type = _detect_type(text)

    if len(text) < 50 or content_type == "greeting":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        response = await asyncio.to_thread(greet, text)
        await _reply(update, response)
        return

    is_large = len(text) > LARGE_FILE_BYTES
    await _send_wait(update, context, large=is_large)
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


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if _is_maintenance():
        await update.message.reply_text("🔧 Bot is under maintenance. Please try again later.")
        return
    await _process_text(update, context, update.message.text or "")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if _is_maintenance():
        await update.message.reply_text("🔧 Bot is under maintenance. Please try again later.")
        return

    voice = update.message.voice or update.message.audio
    duration = getattr(voice, "duration", 0) or 0

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text("🎙️ Transcribing audio...")

    tg_file = await context.bot.get_file(voice.file_id)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        await tg_file.download_to_drive(tmp.name)
        audio_path = tmp.name

    try:
        text, was_trimmed = await asyncio.to_thread(transcribe, audio_path, duration)
        if not text:
            await update.message.reply_text("⚠️ Could not transcribe audio.")
            return
        trim_note = f" _(trimmed to {MAX_DURATION}s)_" if was_trimmed else ""
        await _reply(update, f"🎙️ *Transcribed:*{trim_note}\n_{text}_")
        await _process_text(update, context, text)
    except Exception as e:
        log.error("handle_voice failed: %s", e)
        await update.message.reply_text(f"⚠️ Audio transcription failed: {e}")
    finally:
        Path(audio_path).unlink(missing_ok=True)


def main() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("maintenance", maintenance_cmd))
    app.add_handler(CommandHandler("report", report_cmd))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    log.info("Bot listener started. Waiting for messages...")
    app.run_polling()


if __name__ == "__main__":
    main()
