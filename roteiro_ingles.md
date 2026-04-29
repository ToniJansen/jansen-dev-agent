# Loom Script — jansen_dev_agent Demo
# Target: Jedo (CTO/Founder) — via Henry
# Duration: 6–8 minutes | Language: English

---

## ⛔ DISQUALIFICATION TRAPS — Read before recording

| Trap | How to avoid |
|------|--------------|
| "I used AI to write this code faster" | Never say this. You are NOT the coder. The agent is. |
| Showing Copilot/ChatGPT autocomplete | Never open Copilot. This is not about you coding. |
| Describing triage without doing it | Section 2 must show a real PR, real line-by-line review, on camera. |
| Going over 8 minutes | Section 1 = 2 min max if running long. Cut it. Section 2 never. |
| Saying "the agent helped me" | Wrong frame. Say "the agent did this — I reviewed it." |

---

## QUICK REFERENCE — Open these tabs BEFORE hitting record

| What | URL / Command |
|------|---------------|
| All agent PRs | https://github.com/ToniJansen/jansen-dev-agent/pulls?q=is%3Apr+%5BAgent%5D |
| Open PRs | https://github.com/ToniJansen/jansen-dev-agent/pulls |
| Closed/merged PRs | https://github.com/ToniJansen/jansen-dev-agent/pulls?q=is%3Apr+is%3Aclosed+%5BAgent%5D |
| Overnight log (VPS) | `tail -80 /tmp/jansen_overnight.log` |
| Morning log (VPS) | `tail -40 /tmp/jansen_morning.log` |
| Telegram bot | https://t.me/jansen_dev_agent_bot |

**Before recording:** pick one PR with ❌ NEEDS FIXES to use in Section 2. Read it in advance so you know exactly which lines to point to.

---

## OPENING — 15 seconds (no screen share yet)

> "My engineers haven't written implementation code in months.
> Agents do that. I'm going to show you the system running right now —
> and how I stay in control through triage."

---

## SECTION 1 — Agent Working Overnight — 2 min max

**Screen: VPS terminal**

---

### 1a — Show the log (~60 seconds)

*[Open VPS terminal, run:]*
```
tail -80 /tmp/jansen_overnight.log
```

> "This is last night's run. Every day at 2 AM, this agent starts automatically."

*[Point to each line as you read it:]*

> "— It pulled the latest code from GitHub.
> — It reviewed this file for security issues.
> — It ran the test suite on the original code.
> — It applied the fixes.
> — It ran tests again on the fixed version.
> — It opened a pull request on GitHub.
> All of this happened while I was asleep. Zero human intervention."

---

### 1b — Show GitHub PRs (~60 seconds)

*[Open https://github.com/ToniJansen/jansen-dev-agent/pulls?q=is%3Apr+%5BAgent%5D ]*

> "Here's the result. Every single one of these pull requests was opened by the agent.
> I did not write a single line of this code."

*[Click on one PR — ideally one that was auto-merged (✅ APPROVED)]*

> "This one was clean — the agent found no critical issues, tests passed,
> it merged automatically. No one reviewed it. That's the point."

> "This one here was flagged. Let me show you what triage looks like."

*[Navigate to a PR with ❌ NEEDS FIXES — this is your bridge into Section 2]*

---

## SECTION 2 — Triage Live — 3–4 min — DO NOT CUT THIS

**Screen: GitHub PR with NEEDS FIXES — stay here the whole section**

*[You should already have this PR open from the end of Section 1]*

---

### 2a — Set the frame (~20 seconds)

> "Now I do triage. The agent opened this PR and flagged it as needing fixes.
> My job is to verify: did it find the right problems, and did it fix them correctly?"

---

### 2b — Review the findings (~90 seconds)

*[Scroll to the 🔴/🟡/🔵 findings block in the PR body]*

> "The agent found [N] critical issues."

*[Point to the first finding — read the line number and title]*

> "Line [X] — [issue name]. The agent is right.
> [One sentence explaining WHY this is dangerous in plain English.]
> This is a real security vulnerability, not a style suggestion."

*[Point to the second finding]*

> "Line [Y] — [issue name]. [One sentence on why it matters.]
> The agent caught this without me asking."

*[If there's a third finding, do the same. Skip warnings — focus on criticals.]*

---

### 2c — Show the fix (~60 seconds)

*[Click the "Files changed" tab at the top of the PR]*

> "Now the fix. The agent didn't just report the problem — it rewrote the code."

*[Scroll to the diff — green lines are the fix]*

> "Here's what I'm checking: does this fix actually solve the vulnerability,
> or did the agent produce something that looks right but isn't?
> This is where human judgment matters."

*[Pause — actually read it on camera]*

> "This is correct. The agent solved it properly."

---

### 2d — Show test results (~30 seconds)

*[Go back to the PR description — scroll to the pytest output block]*

> "One last thing — the agent ran a security test suite before and after the fix.
> Before: [N] tests failing — exactly the issues it found.
> After: all passing. The fix isn't assumed. It's verified."

---

## SECTION 3 — Impact and Metrics — 1–2 min

**Screen: Telegram → /report → PDF**

---

### 3a — Generate live (~30 seconds)

*[Open https://t.me/jansen_dev_agent_bot → type /report → wait ~15s]*

> "I have a live metrics dashboard. I'll generate it right now —
> straight from the GitHub API, no manual data."

---

### 3b — Walk through the PDF (~60 seconds)

*[Open the PDF — Before vs. After section first]*

> "Before this system: zero automated reviews per week.
> After: all of these pull requests — opened automatically, zero human effort."

*[Point to the chart — PRs over time]*

> "The agent has been running every night. This is the PR volume over time."

*[Point to the status tables]*

> "Organized by status — what needs my attention, what's still open, what's already merged.
> This is my triage queue. I don't chase files. The agent surfaces what matters."

---

## CLOSING — 10 seconds

> "Live system. Real PRs. Real tests. Agents implement — I own the quality.
> Happy to go deeper in a call."

---

## TIMING CHECK

| Section | Target | Cut point if running long |
|---------|--------|--------------------------|
| Opening | 15 sec | — |
| Section 1 | 2 min | Cut 1b to just the PR list, skip the approved PR |
| Section 2 | 3–4 min | Never cut — this is the whole demo |
| Section 3 | 1–2 min | Skip the chart, go straight to before/after |
| Closing | 10 sec | — |
| **Total** | **6:25–8:15** | Stay under 8 min |

---

## MANDATORY PHRASES CHECKLIST

- [ ] "Agents do that. I'm going to show you the system running right now."
- [ ] "All of this happened while I was asleep. Zero human intervention."
- [ ] "I did not write a single line of this code."
- [ ] "Now I do triage."
- [ ] "The agent didn't just report the problem — it rewrote the code."
- [ ] "This is where human judgment matters."
- [ ] "Agents implement — I own the quality."

---

## SEND TO HENRY — not directly to Jedo
