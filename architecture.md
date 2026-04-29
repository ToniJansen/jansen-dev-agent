# jansen_dev_agent — Architecture Overview

## What This System Does

Three automated agents run continuously, turning code repositories and meeting notes into reviewed pull requests, action item lists, and live metrics — with zero human intervention on the implementation side.

---

## Agents in Production

### 1. Overnight Agent (02:00 daily)
**Trigger:** cron job on DigitalOcean VPS  
**Input:** Python source file (`order_manager.py`)  
**What it does:**
1. Reads the target file from disk
2. Sends it to Anthropic Claude (claude-sonnet-4-6) with a structured security review prompt; Groq llama-3.3-70b-versatile as fallback
3. Receives a classified findings report (CRITICAL / WARNING / INFO)
4. Applies fixes to the code
5. Runs the test suite before and after the fix
6. Opens a GitHub pull request with the full report + diff + test results
7. Labels the PR: `APPROVED ✅` (auto-merge) or `NEEDS FIXES ❌` (requires human triage)
8. Sends a Telegram notification with the review summary

**Output:** GitHub PR + Telegram message  
**Retry logic:** 3 attempts with 600s / 1800s backoff on rate limit (429)

---

### 2. Morning Agent (07:00 daily)
**Trigger:** cron job on DigitalOcean VPS  
**Input:** `.md` meeting files in `demo/meetings/`  
**What it does:**
1. Scans the meetings directory for unprocessed `.md` files
2. Sends each file to Anthropic Claude with a meeting intelligence prompt; Groq fallback if unavailable
3. Extracts: Decisions, Action Items (with owners + deadlines), Blockers, Open Questions, Signals
4. Sends the structured report to Telegram
5. Moves the processed file to `demo/meetings/processed/` so it is not re-processed

**Output:** Telegram message with action items table  
**Archive behavior:** processed files are moved, not deleted

---

### 3. Bot Listener (24/7, systemd service)
**Trigger:** on-demand via Telegram messages  
**Input:** file attachments (`.py`, `.sql`, `.md`) or pasted text  
**What it does:**
1. Receives a message from the Telegram user
2. Auto-detects content type: Python code, SQL query, or meeting transcript
3. Routes to the correct processor:
   - Python → `reviewer.py` (security + code quality)
   - SQL → `sql_reviewer.py` (injection, performance, dialect-aware)
   - Meeting text → `meeting_processor.py` (decisions, actions, signals)
4. Returns a structured report in the chat within ~10 seconds

**Output:** Telegram reply with classified findings  
**Special command:** `/report` → generates and sends a PDF metrics report (live GitHub API data)

---

## Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        SCHEDULED TRIGGERS                        │
│  cron 02:00 ──► overnight_agent.py                              │
│  cron 07:00 ──► morning_agent.py                                │
└─────────────────────────────────────────────────────────────────┘
          │                           │
          ▼                           ▼
   ┌─────────────┐           ┌─────────────────┐
   │ order_       │           │ demo/meetings/  │
   │ manager.py  │           │ *.md files      │
   └──────┬──────┘           └────────┬────────┘
          │                           │
          ▼                           ▼
   ┌─────────────────────────────────────────────┐
   │              file_processor.py              │
   │  • size check (200 KB hard limit)           │
   │  • condense large files (AST / sections)    │
   │  • sanitize prompt injection attempts       │
   │  • wrap in XML delimiters for LLM safety    │
   └──────────────────┬──────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
   ┌──────────┐ ┌──────────┐ ┌───────────────┐
   │reviewer  │ │sql_      │ │meeting_       │
   │.py       │ │reviewer  │ │processor.py   │
   │(Python)  │ │.py (SQL) │ │(meetings)     │
   └────┬─────┘ └────┬─────┘ └───────┬───────┘
        │            │               │
        └────────────┼───────────────┘
                     │
                     ▼
          ┌─────────────────────────────┐
          │  Anthropic API              │
          │  claude-sonnet-4-6          │
          │  (Groq llama-3.3-70b        │
          │   fallback on failure)      │
          └──────────┬──────────────────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
   ┌──────────┐ ┌─────────┐ ┌──────────────┐
   │ GitHub   │ │Telegram │ │ PDF report   │
   │ Pull     │ │message  │ │ (metrics)    │
   │ Request  │ │         │ │              │
   └──────────┘ └─────────┘ └──────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ON-DEMAND TRIGGER                           │
│  Telegram message ──► bot_listener.py (systemd, always on)     │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
   Auto-detection: code keywords → reviewer.py
                   SQL keywords  → sql_reviewer.py
                   otherwise     → meeting_processor.py
          │
          ▼ (same Anthropic/Groq → Telegram path as above)
```

---

## Infrastructure

| Component | Technology | Where |
|-----------|-----------|-------|
| VPS | DigitalOcean Droplet | 137.184.60.205 |
| Scheduling | crontab (root) | VPS |
| Bot runtime | systemd service (`jansen-bot.service`) | VPS |
| LLM API (primary) | Anthropic | Cloud |
| LLM model (primary) | claude-sonnet-4-6 | Anthropic |
| LLM API (fallback) | Groq | Cloud |
| LLM model (fallback) | llama-3.3-70b-versatile | Groq |
| Speech-to-text (primary) | OpenAI whisper-1 | Cloud |
| Speech-to-text (fallback) | Groq whisper-large-v3-turbo | Cloud |
| Version control | GitHub | `ToniJansen/jansen-dev-agent` |
| Notifications | Telegram Bot API | `@jansen_dev_agent_bot` |
| Report format | PDF (Plotly + ReportLab) | Generated on demand |

---

## Key Design Decisions

**Why Anthropic Claude as primary LLM?**  
Claude Sonnet delivers stronger code reasoning and structured output consistency than open-weight models. Groq (llama-3.3-70b) is retained as a fallback so the system keeps running if Anthropic credits are exhausted.

**Why OpenAI Whisper for voice transcription?**  
OpenAI's hosted whisper-1 has better language detection and lower error rates for mixed-language audio (PT/EN). Groq's whisper-large-v3-turbo serves as fallback.

**Why open a GitHub PR instead of patching in place?**  
PRs preserve the human-in-the-loop gate. The agent cannot merge its own work — only the reviewer can. This is the architectural guarantee that keeps quality in human hands.

**Why launchd/cron instead of Airflow or Prefect?**  
Zero infrastructure overhead. Two cron lines are the simplest possible scheduler for two jobs. The demo does not need orchestration complexity.

**Why a systemd service for the bot?**  
The bot must survive SSH session closes and VPS reboots. Systemd handles restarts automatically. `nohup` is not reliable for long-running processes.

**Why file_processor.py as a pre-LLM layer?**  
LLM context windows are finite. Large files get condensed structurally (AST for Python, section headers for Markdown) without losing the parts the reviewer actually needs to see.

---

## PR Triage Flow

```
Agent opens PR
      │
      ├── body contains "APPROVED ✅" ──► auto-merged, no action needed
      │
      └── body contains "NEEDS FIXES ❌" ──► enters human triage queue
                │
                ▼
          Tech Lead reviews:
          • Are the findings valid?
          • Does the diff actually fix the problem?
          • Do tests pass before AND after?
                │
                ├── Yes → approve + merge
                └── No  → comment, request new agent run
```

---

## Codebase Structure

```
ai_principal_interview_demo/
├── jansen_dev_agent/
│   ├── overnight_agent.py     ← entry point: code review at 02:00
│   ├── morning_agent.py       ← entry point: meeting todos at 07:00
│   ├── bot_listener.py        ← entry point: Telegram long-polling (systemd)
│   ├── reviewer.py            ← Anthropic Claude: Python security + quality review
│   ├── sql_reviewer.py        ← Anthropic Claude: multi-dialect SQL review
│   ├── meeting_processor.py   ← Anthropic Claude: meeting → actions + decisions
│   ├── file_processor.py      ← pre-LLM: condense + sanitize input
│   ├── telegram_sender.py     ← thin POST wrapper for Telegram Bot API
│   ├── metrics.py             ← GitHub API → PDF report (/report command)
│   └── .env                   ← secrets (gitignored)
└── demo/
    ├── order_manager.py       ← code review target (10 planted issues)
    └── meetings/
        ├── *.md               ← unprocessed meeting files
        └── processed/         ← archived after morning agent runs
```
