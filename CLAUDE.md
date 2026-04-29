# jansen_dev_agent — Project Context

## What this is
Demo project for a Principal AI Engineer interview with Jedo (CTO) via Henry.
Three automated agents running on a DigitalOcean VPS, reviewed via GitHub PRs.

## VPS Access
```bash
ssh root@137.184.60.205
cd /root/jansen-dev-agent/jansen_dev_agent
```
Claude Code can SSH directly — no need to open a web console.

## Key Files
| File | Purpose |
|------|---------|
| `roteiro_ingles.html` | Interactive demo script — open in browser with `open roteiro_ingles.html` |
| `architecture.md` | System overview with pipeline diagram |
| `jansen_dev_agent/overnight_agent.py` | Runs at 02:00 — reviews files in `demo/code_auto_reviewed/`, opens PRs, archives to `processed/` |
| `jansen_dev_agent/morning_agent.py` | Runs at 07:00 — processes .md files in MEETINGS_DIR → Telegram |
| `jansen_dev_agent/bot_listener.py` | 24/7 Telegram bot (systemd service) — routes code/SQL/meeting/voice inputs |
| `jansen_dev_agent/groq_client.py` | LLM client: Anthropic Claude primary, Groq fallback (3-key rotation) |
| `jansen_dev_agent/reviewer.py` | Python code review via Anthropic Claude (Groq fallback) |
| `jansen_dev_agent/sql_reviewer.py` | SQL review via Anthropic Claude (Groq fallback, multi-dialect) |
| `jansen_dev_agent/code_fixer.py` | Auto-fixes code based on review report |
| `jansen_dev_agent/meeting_processor.py` | Extracts decisions, action items, blockers from meeting notes |
| `jansen_dev_agent/github_pr.py` | Opens review PRs on GitHub; auto-merges APPROVED ones |
| `jansen_dev_agent/metrics.py` | GitHub API → PDF report via /report command |
| `jansen_dev_agent/transcriber.py` | Transcribes voice notes (OpenAI Whisper primary, Groq fallback, up to 60s) |
| `jansen_dev_agent/greeter.py` | Conversational fallback for short/greeting messages |
| `jansen_dev_agent/file_processor.py` | File reading with size limit enforcement (FileTooLargeError) |
| `demo/order_manager.py` | Main code review target (live on VPS) |
| `demo/mocks/` | All mock files for the demo (Python, SQL, meeting notes) |
| `demo/mocks/meetings/` | Mock meeting notes scanned by morning agent during demo |

## Infrastructure
- **VPS:** DigitalOcean 137.184.60.205
- **LLM (code/text):** Anthropic claude-sonnet-4-6 (primary), Groq llama-3.3-70b-versatile (fallback, 3 API keys)
- **LLM (voice):** OpenAI whisper-1 (primary), Groq whisper-large-v3-turbo (fallback)
- **Scheduling:** crontab root (02:00 overnight, 07:00 morning)
- **Bot runtime:** systemd `jansen-bot.service`
- **GitHub:** github.com/ToniJansen/jansen-dev-agent
- **Telegram bot:** @jansen_dev_agent_bot (chat_id: 6492284230)
- **Dependencies:** anthropic, openai, groq, python-telegram-bot, requests, plotly, kaleido, playwright, pytest, python-dotenv

## Demo Mock Files (`demo/mocks/`)
Mock files for the live demo — copy to `demo/code_auto_reviewed/` or `demo/meetings/` to trigger agents.

| Mock File | Type | Use |
|-----------|------|-----|
| `order_manager.py`, `order_mock_1..3.py` | Python | Code review targets |
| `order_mock_review_1.py` | Python | Pre-reviewed version |
| `user_auth_clean.py`, `payment_utils_clean.py` | Python | Clean code samples |
| `file_storage_clean.py`, `notification_service_clean.py` | Python | Clean code samples |
| `q_test.sql`, `q_test_1..3.sql` | SQL | SQL review targets |
| `q_test_review_1.sql`, `queries.sql` | SQL | Pre-reviewed SQL |
| `meetings/ata-sprint-planning.md` | Meeting | Sprint planning notes |
| `meetings/sprint-planning-2026-04-29.md` | Meeting | Latest sprint planning |
| `meetings/contexto-projeto.md` | Meeting | Project context notes |

## LLM Provider Strategy
- **Primary (code/text/SQL/meetings):** Anthropic claude-sonnet-4-6 via `ANTHROPIC_API_KEY`
- **Primary (voice/audio):** OpenAI whisper-1 via `OPENAI_API_KEY`
- **Fallback (code/text):** Groq llama-3.3-70b-versatile — 3 keys in `.env` (`GROQ_API_KEY`, `GROQ_API_KEY_2`, `GROQ_API_KEY_3`), tried in order on failure
- **Fallback (voice):** Groq whisper-large-v3-turbo

## Logs on VPS
```bash
tail -80 /tmp/jansen_overnight.log   # overnight agent
tail -40 /tmp/jansen_morning.log     # morning agent
```

## Run Agents Manually (from VPS)
```bash
python3 overnight_agent.py   # code review → Telegram + GitHub PR (archives to processed/)
python3 morning_agent.py     # meeting notes → Telegram
```

## Overnight Agent Flow
1. `git pull --rebase` to sync latest
2. Finds `.py` and `.sql` files in `demo/code_auto_reviewed/`
3. Reviews with Anthropic Claude (Python → `reviewer.py`, SQL → `sql_reviewer.py`; Groq fallback if unavailable)
4. Sends review report to Telegram
5. Runs pytest before/after fix (`demo/tests/`)
6. Calls `code_fixer.py` to auto-fix issues
7. Opens GitHub PR via `github_pr.py`
8. If `APPROVED ✅`: auto-merges PR, notifies Telegram
9. If issues found: leaves PR open, notifies Telegram for triage
10. Archives processed file to `demo/code_auto_reviewed/processed/`

## Bot Commands
| Command | Who | Purpose |
|---------|-----|---------|
| `/start` | anyone | Show capabilities |
| `/report` | owner only | Generate GitHub metrics PDF |
| `/maintenance on\|off` | owner only | Toggle maintenance mode |
| Send `.py` file | anyone | Code review + auto-fix PR |
| Send `.sql` file | anyone | SQL review + auto-fix PR |
| Send `.md` file | anyone | Meeting notes processing |
| Send voice (≤60s) | anyone | Transcribe + route automatically |
| Send text | anyone | Auto-detect: code / SQL / meeting / greeting |

## PR Status Groups (metrics.py)
- ❌ Needs Fixes — open PRs with "NEEDS FIXES" in body
- 🔄 Open — open PRs without verdict
- ✅ Fixes Applied — merged PRs

## Demo Script
`roteiro_ingles.html` has: stopwatch, per-step storytelling, inline GitHub links,
drip sound at 7:00 (1 min before limit), Demo Prep section with mock file prompt.

To open: `open roteiro_ingles.html`

## Environment Variables (`.env.example`)
| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Primary LLM key (Claude Sonnet — code, SQL, meetings) |
| `ANTHROPIC_MODEL` | Model name (default: claude-sonnet-4-6) |
| `OPENAI_API_KEY` | Primary speech-to-text key (whisper-1) |
| `GROQ_API_KEY` | Groq fallback key #1 |
| `GROQ_API_KEY_2` | Groq fallback key #2 |
| `GROQ_API_KEY_3` | Groq fallback key #3 |
| `GROQ_MODEL` | Groq fallback model (llama-3.3-70b-versatile) |
| `TELEGRAM_BOT_TOKEN` | Bot token |
| `TELEGRAM_CHAT_ID` | Owner chat ID (6492284230) |
| `CODE_TARGET_FILE` | Path to code review target |
| `MEETINGS_DIR` | Path to meetings directory |
| `GITHUB_REPO` | `ToniJansen/jansen-dev-agent` (used by github_pr.py) |

## Language
All code, docs, and comments in this project are in English (Jedo is US/Canada).
