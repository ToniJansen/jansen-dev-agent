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
| `jansen_dev_agent/overnight_agent.py` | Runs at 02:00 — code review → GitHub PR |
| `jansen_dev_agent/morning_agent.py` | Runs at 07:00 — meeting notes → Telegram |
| `jansen_dev_agent/bot_listener.py` | 24/7 Telegram bot (systemd service) |
| `jansen_dev_agent/groq_client.py` | Groq API with 3-key fallback (KEY, KEY_2, KEY_3) |
| `jansen_dev_agent/metrics.py` | GitHub API → PDF report via /report command |
| `demo/order_manager.py` | Main code review target |
| `demo/meetings/` | Morning agent scans here for .md files |

## Infrastructure
- **VPS:** DigitalOcean 137.184.60.205
- **LLM:** Groq llama-3.3-70b-versatile (3 API keys for rate limit fallback)
- **Scheduling:** crontab root (02:00 overnight, 07:00 morning)
- **Bot runtime:** systemd `jansen-bot.service`
- **GitHub:** github.com/ToniJansen/jansen-dev-agent
- **Telegram bot:** @jansen_dev_agent_bot (chat_id: 6492284230)

## Groq Rate Limit Fallback
3 keys in `.env`: `GROQ_API_KEY`, `GROQ_API_KEY_2`, `GROQ_API_KEY_3`
`groq_client.py` tries them in order on 429. 300K tokens/day total.

## Logs on VPS
```bash
tail -80 /tmp/jansen_overnight.log   # overnight agent
tail -40 /tmp/jansen_morning.log     # morning agent
```

## Run Agents Manually (from VPS)
```bash
python3 overnight_agent.py   # code review → Telegram + GitHub PR
python3 morning_agent.py     # meeting notes → Telegram
```

## PR Status Groups (metrics.py)
- ❌ Needs Fixes — open PRs with "NEEDS FIXES" in body
- 🔄 Open — open PRs without verdict
- ✅ Fixes Applied — merged PRs

## Demo Script
`roteiro_ingles.html` has: stopwatch, per-step storytelling, inline GitHub links,
drip sound at 7:00 (1 min before limit), Demo Prep section with mock file prompt.

## Language
All code, docs, and comments in this project are in English (Jedo is US/Canada).
