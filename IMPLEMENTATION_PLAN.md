# jansen_dev_agent — Implementation Plan

> **Status: COMPLETE** — All tasks implemented and committed to `github.com/ToniJansen/jansen-dev-agent`.
> VPS deployment (Oracle Cloud) in progress — see Task 11.

**Goal:** A Python project with two scheduled agents (overnight code review at 02:00, morning meeting-to-todos at 07:00), an interactive Telegram bot (`@jansen_dev_agent_bot`), automatic GitHub PR creation with LLM-generated code fixes, security regression tests before/after each fix, language-aware greeting/off-topic handling, and an on-demand metrics dashboard delivered as PDF via `/report`.

**Architecture:** Four entry points sharing five processors and three support modules. Scheduled scripts run via launchd (macOS) or systemd+cron (Linux/VPS). Interactive mode uses async long-polling (`python-telegram-bot`). Content-type auto-detection routes incoming messages to the correct processor. All LLM inputs pass through a pre-processing safety layer before reaching Groq.

**Tech Stack:** Python 3.9+, `groq` SDK (free tier, `llama-3.3-70b-versatile`), `python-telegram-bot>=20.0`, `requests`, `python-dotenv`, `pytest`, `playwright` (Chromium PDF rendering)

**Capabilities:**
| Input | Processor | Trigger |
|-------|-----------|---------|
| `.py` file or code snippet | `reviewer.py` + `code_fixer.py` + `github_pr.py` | `def`, `class`, `import` keywords |
| `.sql` file or SQL text | `sql_reviewer.py` | `SELECT`, `FROM`, `JOIN`, `CREATE` keywords |
| `.md` / meeting text | `meeting_processor.py` | `action item`, `decision`, `agenda`, `ata` keywords |
| Greeting / off-topic / unrecognized text | `greeter.py` | fallback — no strong content-type signal |

---

## File Map

```
ai_principal_interview_demo/
├── deploy.sh                        ← one-shot VPS setup (systemd + cron)
├── jansen_dev_agent/
│   ├── overnight_agent.py           ← entry point: git pull + code review at 02:00
│   ├── morning_agent.py             ← entry point: meeting todos at 07:00
│   ├── bot_listener.py              ← entry point: interactive Telegram long-polling
│   ├── reviewer.py                  ← Groq: Python security + quality review
│   ├── sql_reviewer.py              ← Groq: multi-dialect SQL review
│   ├── meeting_processor.py         ← Groq: meeting-to-actions (decisions/blockers/signals)
│   ├── code_fixer.py                ← Groq: LLM-generated code fix (Python + SQL)
│   ├── github_pr.py                 ← GitHub REST API: branch + commit + PR
│   ├── greeter.py                   ← Groq: language-aware intro / off-topic redirect
│   ├── metrics.py                   ← GitHub API: PR metrics + HTML dashboard + PDF via Playwright
│   ├── file_processor.py            ← pre-LLM safety: token budget + 7-vector injection defense
│   ├── telegram_sender.py           ← Telegram Bot API wrapper (text chunks + document upload)
│   ├── .env.example
│   └── .env                         ← gitignored
└── demo/
    ├── order_manager.py             ← primary code review target (planted issues)
    ├── code_auto_reviewed/          ← files scanned by overnight_agent; PRs opened per file
    │   └── queries.sql
    ├── tests/
    │   └── test_security.py         ← 10 pytest security tests (run before/after each fix)
    ├── meetings/
    │   ├── ata-sprint-planning.md   ← meeting demo file
    │   └── processed/               ← files archived here after processing
    └── mocks/                       ← 8 small test files for Telegram bot testing
        ├── order_mock.py
        ├── order_mock_1.py          ← JWT auth, hardcoded secret, plaintext password compare
        ├── order_mock_2.py          ← path traversal, pickle RCE, command injection
        ├── order_mock_3.py          ← hardcoded payment URL/secret, no timeout, PII in logs
        ├── q_test.sql
        ├── q_test_1.sql             ← GRANT ALL, UPDATE without WHERE, hardcoded password
        ├── q_test_2.sql             ← Cartesian join, no LIMIT, implicit cast, ORDER BY position
        └── q_test_3.sql             ← DROP without transaction, hardcoded prod key in INSERT
```

---

## Task 1 — Manual prerequisites ✅

- [x] **Step 1:** Create bot via @BotFather → `@jansen_dev_agent_bot`
- [x] **Step 2:** Create folder structure
- [x] **Step 3:** Copy demo files from `proj_eprompt_g5`

---

## Task 2 — Environment setup ✅

- [x] **Step 1:** Write `.env.example`

  ```
  GROQ_API_KEY=gsk_...
  GROQ_MODEL=llama-3.3-70b-versatile
  TELEGRAM_BOT_TOKEN=NNNNNNNNNN:AAA...
  TELEGRAM_CHAT_ID=your_chat_id_here
  CODE_TARGET_FILE=../demo/order_manager.py
  MEETINGS_DIR=../demo/meetings
  GITHUB_TOKEN=ghp_...
  GITHUB_REPO=owner/repo-name
  ```

- [x] **Step 2:** Create `.env` with real values
- [x] **Step 3:** Add `.env` to `.gitignore`

---

## Task 2b — `file_processor.py` ✅

Pre-LLM processing layer. Hard-rejects files >200KB. If content fits in 12,000 chars, returns as-is. If too large, returns a structural summary without LLM involvement.

**Three condensation strategies:**
- **Python** — `ast.walk()` to extract class/function signatures + first 5 body lines
- **SQL** — splits on `;`, fills budget statement-by-statement
- **Meeting/text** — splits on `##` headings, includes all titles + body up to budget

**7-vector injection sanitizer (`sanitize()`):**
1. Plaintext injection phrases
2. ROT13 variants
3. Base64 — decode candidates and re-check
4. Hex escape sequences (`\xNN`)
5. Unicode escapes (`\uNNNN`)
6. URL encoding (`%NN`)
7. HTML entities (`&#NNN;`)

**`wrap_for_llm(content, label)`** — sanitize + XML-tag + decode-ignore directive.

- [x] **Step 1:** Write `prepare()`, condensers, `sanitize()`, `wrap_for_llm()`

---

## Task 3 — `telegram_sender.py` ✅

Thin wrapper for the Telegram Bot API. Chunks messages at 4096 chars. Tries Markdown first; retries plain text on 400 BadRequest (LLM output with invalid Markdown escapes).

- [x] **Step 1:** Write the module

---

## Task 4 — `reviewer.py` ✅

Groq call for Python code review. Uses `prepare()` + `wrap_for_llm(content, label="code")`. Output format: severity header (🔴🟡🔵), per-finding lines with line number + one-line fix, final verdict.

- [x] **Step 1:** Write the module

---

## Task 5 — `meeting_processor.py` ✅

Groq call for meeting analysis. Uses `wrap_for_llm(content, label="meeting")`. Output: Decisions / Actions (Owner → action — deadline) / Blockers / Open / Signals.

- [x] **Step 1:** Write the module

---

## Task 5b — `sql_reviewer.py` ✅

Groq call for SQL review. Auto-detects dialect from syntax. Uses `wrap_for_llm(content, label="sql")`. Covers PostgreSQL, MySQL, SQLite, BigQuery, Spark SQL, T-SQL, ANSI SQL.

- [x] **Step 1:** Write the module

---

## Task 5c — `code_fixer.py` ✅

Groq call that takes a file + its review report and returns complete fixed source code (no markdown fences). Uses `max_tokens=4096` to fit full file. Detects `.py` vs `.sql` by extension and uses the appropriate system prompt.

- [x] **Step 1:** Write the module

---

## Task 5d — `github_pr.py` ✅

GitHub REST API integration (no extra dependency — uses `requests`).

Flow:
1. Create branch `agent/review-{YYYYMMDDHHMMSS}` (unique timestamp per run)
2. Commit fixed code to `demo/code_auto_reviewed/{filename}`
3. Commit review report to `reviews/{date}-{filename}.md`
4. Open PR with title `[Agent] Code review fixes — {filename} ({timestamp})`
5. Handles 422 on existing branch or existing PR gracefully

- [x] **Step 1:** Write the module

---

## Task 5f — Security test suite ✅

`demo/tests/test_security.py` — 10 pytest tests covering the most critical attack vectors.

**Tests (parametrized where applicable):**
- `test_no_hardcoded_secrets` × 4 patterns (password, secret/key, Stripe key, webhook secret)
- `test_no_sql_fstring` — f-string in SQL query
- `test_no_sql_percent_format` — % formatting in SQL
- `test_no_os_system` — command injection via `os.system()`
- `test_no_pickle_load` — unsafe deserialization
- `test_no_path_concatenation` — path traversal via string concat
- `test_requests_have_timeout` — all HTTP calls have explicit timeout

`TEST_TARGET` env var points to the file under test — overnight_agent writes content to a temp file and sets `TEST_TARGET` before running pytest.

**Verified result on `order_manager.py`:** 2 failed (hardcoded key + SQL f-string), 8 passed.

- [x] **Step 1:** Write `demo/tests/test_security.py`
- [x] **Step 2:** Update `overnight_agent.py` — `_run_tests(content, suffix)` before/after fix
- [x] **Step 3:** Update `github_pr.py` — `test_before`/`test_after` section in PR body

---

## Task 5g — `metrics.py` + `/report` command ✅

`metrics.py` — GitHub API → metrics computation → HTML dashboard → PDF via Playwright.

**Pipeline:**
1. Fetch all `[Agent]` PRs from GitHub API (open + closed)
2. Compute: total PRs, by file type, CRITICAL/WARNING/INFO counts, approved vs. needs-fixes
3. Build self-contained HTML with Chart.js timeline + before/after cards + PR table
4. `generate_pdf()` — Playwright headless Chromium renders the HTML (JS + charts) → A4 PDF
5. `build_report()` — orchestrates steps 1–4, returns PDF path

**`/report` Telegram command (owner-only):**
- `asyncio.to_thread(build_report)` — non-blocking PDF generation
- Bot sends PDF as document via `send_document()` in `telegram_sender.py`
- Live data: every `/report` pulls fresh data from GitHub API

**`telegram_sender.py`** updated with `send_document(file_path, caption)` using `sendDocument` endpoint.

- [x] **Step 1:** Write `metrics.py` with `build_report()` and `generate_pdf()`
- [x] **Step 2:** Add `send_document()` to `telegram_sender.py`
- [x] **Step 3:** Add `/report` command to `bot_listener.py`
- [x] **Step 4:** Update `deploy.sh` — `pip install playwright` + `playwright install chromium --with-deps`

---

## Task 5h — Auto-merge + mock historical PRs ✅

**Auto-merge logic (`overnight_agent.py` + `github_pr.py`):**
- `_is_approved(report)` — checks `"APPROVED ✅"` in LLM report (0 CRITICALs)
- `_extract_pr_number(pr_url)` — parses PR number from URL
- `merge_pr(repo, pr_number)` in `github_pr.py` — GitHub squash merge via `PUT /repos/{repo}/pulls/{n}/merge`
- `open_review_pr()` updated — `test_before`/`test_after` optional params, Test Results section in PR body
- Flow: APPROVED ✅ → auto-merge → Telegram "auto-merged" · NEEDS FIXES ❌ → leave open for triage

**Mock historical PRs (`demo/mock_prs.json`):**
- 20 PRs spread April 1–27, 2026 (before GitHub repo existed)
- ~13 NEEDS FIXES ❌ (realistic majority), ~7 APPROVED ✅
- `compute(include_mock=True)` merges mock + real PRs, deduped by `html_url`
- Enriches timeline chart from flat line to 27-day activity chart

**Demo file (`demo/code_auto_reviewed/payment_utils_clean.py`):**
- All credentials from `os.environ`, all requests have `timeout=10`, no unsafe ops
- Passes all 10 security tests → triggers APPROVED ✅ path → demonstrates auto-merge

**Dashboard cards updated:**
- OLD: Total PRs | Python | SQL | Critical | Warnings | Auto-approved
- NEW: Total PRs | Auto-merged ✅ (green) | Needs triage 🔴 (red) | Critical | Warnings | Python files

- [x] **Step 1:** Add `merge_pr()` to `github_pr.py`
- [x] **Step 2:** Add auto-merge logic to `overnight_agent.py`
- [x] **Step 3:** Create `demo/mock_prs.json` with 20 historical PRs
- [x] **Step 4:** Update `metrics.py` — `_load_mock_prs()`, `compute(include_mock=True)`, new card layout
- [x] **Step 5:** Create `demo/code_auto_reviewed/payment_utils_clean.py` (clean demo file)

---

## Task 5e — `greeter.py` ✅

Groq call for language-aware greetings and off-topic handling.

**Two-type classification:**
- **TYPE A** (greeting / intro request) — intro in detected language: what the bot is + 3 capabilities + one example
- **TYPE B** (off-topic) — polite 2-line decline + suggestion, in detected language

Full injection protection via `wrap_for_llm(text, label="message")`. `temperature=0.4`, `max_tokens=350`.

- [x] **Step 1:** Write the module

---

## Task 6 — `overnight_agent.py` ✅

Runs at 02:00. Pulls latest from GitHub (`git pull --rebase`) before scanning. Scans `demo/code_auto_reviewed/` for `*.py` and `*.sql` files. For each file: review → send Telegram → fix → open PR → send PR URL.

- [x] **Step 1:** Write the script (git pull + multi-file scan + PR flow)

---

## Task 7 — `morning_agent.py` ✅

Runs at 07:00. Scans `MEETINGS_DIR` for unprocessed `*.md` files. Processes each, sends Telegram report, moves file to `processed/`.

- [x] **Step 1:** Write the script

---

## Task 8 — `bot_listener.py` ✅

Interactive async long-polling bot. Key design decisions:

- **Content detection priority:** Python keywords → SQL keywords → meeting keywords → greeting (fallback). Python checked before SQL to prevent Python files containing SQL from misrouting.
- **`_MEETING_KEYWORDS`** separates real meeting transcripts from general text.
- **`asyncio.to_thread()`** wraps all synchronous Groq calls to prevent blocking the event loop.
- **`_reply()` helper** — sends with `parse_mode="Markdown"`, retries plain on `BadRequest`.
- **Temp file rename** — renames to `doc.file_name` before processing so review shows correct filename.
- **`.py` upload flow:** review → send → fix → PR → send PR URL.
- **Maintenance mode:** owner-only `/maintenance on|off` writes a `.maintenance` flag file.

- [x] **Step 1:** Install `python-telegram-bot>=20.0`
- [x] **Step 2:** Write the bot with all handlers and safety patterns

---

## Task 9 — End-to-end tests ✅

- [x] **Step 1:** Install all dependencies
  ```bash
  pip3 install groq requests python-dotenv "python-telegram-bot>=20.0"
  ```
- [x] **Step 2:** `python3 overnight_agent.py` → Telegram report + PR URL
- [x] **Step 3:** `python3 morning_agent.py` → Telegram report, file archived to `processed/`
- [x] **Step 4:** `python3 bot_listener.py` → `/start`, file upload, text snippet, greeter

---

## Task 10 — Scheduling (macOS launchd) ✅

- [x] **Step 1:** Create `~/Library/LaunchAgents/com.jansen.overnight.plist` (02:00)
- [x] **Step 2:** Create `~/Library/LaunchAgents/com.jansen.morning.plist` (07:00)
- [x] **Step 3:** `launchctl load` both plists
- [x] **Step 4:** `python3 bot_listener.py &` — running continuously (PID confirmed)

---

## Task 11 — VPS Deployment (Oracle Cloud) 🔄 IN PROGRESS

> **⚠️ Telegram long-polling constraint:** Only one `bot_listener.py` process can run per bot token at a time. Running it on both Mac and VPS simultaneously causes the second instance to forcibly disconnect the first. **Rule: bot_listener runs on VPS only (production).** The scheduled agents (`overnight_agent.py` and `morning_agent.py`) can run on both machines without conflict — duplicate Telegram messages are harmless. The Mac is for development and testing only.

One-shot deploy script at `deploy.sh` in repo root. Sets up Ubuntu 22.04 on Oracle Cloud Always Free tier.

**VM spec:** `VM.Standard.A1.Flex` — 1 OCPU, 6GB RAM, Always Free (no expiry).

**What `deploy.sh` does:**
1. `apt-get install python3 python3-pip git`
2. `git clone` the repo (or `git pull` if already cloned)
3. `pip3 install` all dependencies
4. Pauses for user to fill in `.env`
5. Creates and enables `/etc/systemd/system/jansen-bot.service` (auto-restart on crash)
6. Writes cron entries for overnight (02:00) and morning (07:00) agents

- [x] **Step 1:** Write `deploy.sh` and commit to repo
- [ ] **Step 2: Create Oracle Cloud account**
  - cloud.oracle.com → Sign Up → verify credit card (no charge)
- [ ] **Step 3: Create VM instance**
  - Compute → Instances → Create Instance
  - Image: Ubuntu 22.04
  - Shape: `VM.Standard.A1.Flex` (Always Free)
  - Generate SSH key pair → download `.key` file
  - Note the public IP
- [ ] **Step 4: SSH and run deploy script**
  ```bash
  chmod 400 ~/Downloads/ssh-key.key
  ssh -i ~/Downloads/ssh-key.key ubuntu@<VM_IP>
  curl -sL https://raw.githubusercontent.com/ToniJansen/jansen-dev-agent/main/deploy.sh | bash
  ```
- [ ] **Step 5: Verify**
  ```bash
  sudo systemctl status jansen-bot
  sudo journalctl -u jansen-bot -f
  ```

---

## Pre-recording Checklist

- [x] `python3 overnight_agent.py` → Telegram report with CRITICAL issues + PR URL
- [x] `python3 morning_agent.py` → Telegram report with decisions + action items
- [x] `python3 bot_listener.py` running → `/start`, file upload, text, greeter all work
- [x] Mock files in `demo/mocks/` — 4 Python + 4 SQL with planted issues
- [x] Security tests in `demo/tests/` — 2 failures on original, 0 on fixed
- [x] `/report` command → PDF delivered via Telegram (193 KB, Chart.js rendered)
- [x] Auto-merge: APPROVED ✅ PRs squash-merged automatically; NEEDS FIXES left for triage
- [x] Mock historical PRs: 20 PRs (Apr 1-27) enrich metrics chart to 27-day timeline
- [x] `.env` not tracked by git
- [x] Both scheduled jobs active in launchd
- [ ] VPS running on Oracle Cloud with systemd service active

---

## Commit History

| Hash | Description |
|------|-------------|
| `4012514` | feat: auto-merge approved PRs + mock historical data + updated metrics dashboard |
| `aa806fa` | feat: /report command — PDF from live GitHub data via Playwright, sent via Telegram |
| `ec4fe62` | feat: add metrics dashboard (GitHub API + HTML report + Chart.js) |
| `bae1659` | feat: security test suite + before/after test results in PRs |
| `9e62087` | docs: add Oracle Cloud step-by-step deploy guide |
| `e3f631e` | docs: update implementation plan to reflect completed state |
| `eaf9942` | feat: add one-shot deploy script for Oracle Cloud Ubuntu 22.04 |
| `868e79a` | feat: greeter handles off-topic messages with polite redirect |
| `2c7d2e1` | feat: add LLM greeter — auto-detects language, injection protection |
| `067819a` | feat: add 6 mock files for Telegram testing (order_mock_1-3.py, q_test_1-3.sql) |
| `0f8b830` | feat: code_auto_reviewed/ folder, overnight agent scans folder + git pull |
| `5c8101f` | fix: unique branch per run (timestamp), correct filename in review, PR on upload |

---

## Estimated Time (Actual)

| Task | Estimated | Status |
|------|-----------|--------|
| Task 1 — Manual prerequisites | 10 min | ✅ Done |
| Task 2 — Environment setup | 5 min | ✅ Done |
| Task 2b — file_processor.py | 15 min | ✅ Done |
| Tasks 3–5b — Core modules | 30 min | ✅ Done |
| Task 5c — code_fixer.py | 10 min | ✅ Done |
| Task 5d — github_pr.py | 15 min | ✅ Done |
| Task 5e — greeter.py | 10 min | ✅ Done |
| Task 5f — Security tests | 15 min | ✅ Done |
| Task 5g — metrics.py + /report | 20 min | ✅ Done |
| Task 5h — Auto-merge + mock PRs | 15 min | ✅ Done |
| Tasks 6–7 — Scheduled agents | 15 min | ✅ Done |
| Task 8 — Interactive bot | 20 min | ✅ Done |
| Task 9 — Testing | 20 min | ✅ Done |
| Task 10 — Scheduling (launchd) | 10 min | ✅ Done |
| Task 11 — VPS (Oracle Cloud) | 20 min | 🔄 In progress |
| **Total** | **~185 min** | |
