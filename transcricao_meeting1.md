# Technical Interview Analysis — Antônio Arruda x Henry

> **Date:** 2026-04-28
> **Type:** Technical screening call (Principal AI Engineer)
> **Participants:** Henry (Executive Recruiter, Miami) | Antônio Arruda (Candidate, Florianópolis)
> **Purpose:** Strategic alignment and technical screening for Principal AI (Artificial Intelligence) Engineer position focused on autonomous coding agents
> **Confidence:** 0.90 — transcript is well-structured with clear speaker attribution and explicit decisions

---

## Executive Summary

Henry, an executive recruiter with decades of global tech experience, conducted a strategic screening for a Principal AI Engineer role requiring deep, hands-on expertise with autonomous coding agents. The hiring decision sits with Jedo (CTO/Founder), who has already rejected two previous candidates — one for cultural misalignment and one for failing a technical demo. Antônio demonstrated a credible production-grade profile, distinguished himself by framing his work as "Software Engineering with AI" (not "vibe coding"), and was given a clear, high-stakes next step: record a screen demo of his agent pipeline and orchestrator before submission to Jedo.

---

## Decisions Made

| # | Decision | Context |
|---|----------|---------|
| D1 | Henry will send Antônio a detailed script via WhatsApp of what Jedo wants to validate | Decided at end of call; script specifies exact scope and framing expected in the demo |
| D2 | Antônio must submit a recorded screen demo (not a live session) | Format chosen to allow Jedo to review asynchronously; Jedo's feedback expected within 1 business day after submission |
| D3 | Demo must cover architecture and internal logic ("under the hood"), not just functionality | Explicitly stated by Henry as Jedo's requirement — previous candidate failed by showing only surface-level behavior |

---

## Action Items

| # | Action | Owner | Deadline | Priority |
|---|--------|-------|----------|----------|
| A1 | Send detailed script of what Jedo wants validated in the demo (via WhatsApp) | Henry | ASAP (post-call) | High |
| A2 | Wait for and review Henry's WhatsApp script before recording anything | Antônio | Upon receipt of A1 | High |
| A3 | Record screen demo: agent pipeline and orchestrator in full operation | Antônio | TBD — after receiving script | High |
| A4 | Demo must verbally explain logic, architecture, and "under the hood" mechanics | Antônio | Same as A3 | High |
| A5 | Submit demo to Henry for forwarding to Jedo | Antônio | TBD — after A3 | High |
| A6 | Practice and reinforce daily English in preparation for a fully English-speaking work environment | Antônio | Ongoing | Medium |
| A7 | Identify the strongest production agent project to feature as the centerpiece of the demo (FNDE pipeline vs. editorial automation) | Antônio | Before recording | Medium |

---

## Open Questions

| # | Question | Blocker? | Follow-up |
|---|----------|----------|-----------|
| Q1 | What is the exact format and duration Jedo expects for the demo video? | Yes — cannot record without this | Resolved by Henry's WhatsApp script (A1) |
| Q2 | Does the role require relocation or is it fully remote? | Potential blocker for Antônio | Not explicitly discussed; clarify with Henry |
| Q3 | What is the compensation range and equity structure? | Not a blocker yet | Standard next-round topic |
| Q4 | What is the company/product domain where the orchestrator will be deployed? | Medium — affects which demo project is most relevant | Ask Henry when reviewing the script |
| Q5 | Will Jedo conduct a live technical interview after the demo, or is the demo the final technical gate? | Medium — affects depth of preparation | Clarify with Henry |
| Q6 | What does Jedo define as "cultural alignment"? (Previous candidate was rejected on this basis) | Medium — risk mitigation | Ask Henry proactively |

---

## Key Insights

- **The bar is explicitly high and the failure pattern is known.** Two candidates already failed — one on culture, one on technical demo. This is not a standard screening; Jedo has a very specific mental model of what "hands-on with coding agents" means. Antônio must preempt that mental model in the demo, not just demonstrate competence.

- **"Software Engineering with AI" framing is a strategic differentiator.** Antônio's explicit rejection of "vibe coding" directly addresses what Jedo appears to be screening against (theorists vs. practitioners). This framing should be verbalized early in the demo narration.

- **The orchestrator concept is load-bearing.** Jedo's requirements (centralized coordination of multiple agents, full workflow from code generation through PR, tests, and error triage) map precisely to Antônio's FNDE monorepo and editorial multi-agent pipeline. The demo should name the pattern explicitly.

- **Spec Driven Development (SDD) methodology, introduced by mentor Luan, is a concrete differentiator.** The overnight-conversion-of-meeting-transcriptions-into-technical-requirements workflow is exactly the kind of production-grade, unsupervised agent behavior Jedo is looking for. It should be demonstrated or at minimum narrated in the demo.

- **English proficiency is a real but manageable risk.** Antônio is technically fluent but lacks daily immersion in an all-English environment. His self-awareness on this point is an asset, not a liability — but the demo video must be recorded in confident, clear English. Consider scripting the narration before recording.

- **Henry's own network depth is an asset.** His 30–35 years of Florianópolis visits and global recruiter experience suggests this is a warm, relationship-driven placement — not a cold pipeline. Antônio should treat this as a long-term professional relationship regardless of this specific outcome.

- **WSL (Windows Subsystem for Linux) workaround for FNDE agents signals real-world problem-solving.** Using WSL to run agents in a native Linux environment to overcome OS limitations is the kind of "I've faced real production friction" story Jedo explicitly values. Include it in the demo narrative.

---

## Transcricao Original

### Section 1 – Context & Market Trends

Henry has visited Florianópolis for 30–35 years, watching it evolve into a tech hub. They discussed cost-of-living as an economic indicator — Henry uses "coffee price at coworking spaces" as an inflation proxy (moved from WeWork to Spaces; coffee in Miami/Brickell now exceeds NYC/Penn Station prices). Discussion on return-to-office trend led by Nubank and JP Morgan. Antônio confirms NYC center revitalization from a recent trip, but maintains high-performance remote routine.

### Section 2 – Role Definition & Strategic Requirements

Selection process conducted by CTO/Founder "Jedo" is extremely rigorous. Two previous candidates failed: one for cultural misalignment, another failed the coding agents technical demo.

**Critical requirements defined by Jedo:**
- Autonomous coding agents (operating without direct human supervision)
- Full workflow automation: code generation → PR opening → test execution → error triage
- Orchestrator: centralized system coordinating multiple agents simultaneously
- Hands-on experience: Jedo wants practitioners who have faced real production challenges with coding agents, not theorists

### Section 3 – Technical Profile & AI Software Engineering

Antônio defines his practice as "Software Engineering with AI" (not "vibe code"). His production agents focus on the business layer; he uses coding-layer agents in his private daily workflow.

**Tech stack:**
- Claude 3 Opus (Max Plan) — primary tool for complex tasks
- Anti Gravity (Claude Code / Cursor-type IDE) — main IDE for agent development
- ChatGPT and Codex as technical redundancy

**Mentors:**
- Sandeco (UFG) — Generative AI reference, Campus Party Brasil founder
- Luan (Pifia, Canadian company) — introduced Antônio to Spec Driven Development; methodology: agents run overnight converting meeting transcriptions into technical requirements ready for human review next morning

**Projects:**
- FNDE data investigation: Databricks agents on a Monorepo; uses WSL to ensure agents run in native Linux environment, overcoming OS limitations
- Editorial automation: multi-agent pipeline (spell-check, content review, formatting) for writing a 120-page LaTeX book

### Section 4 – Professional & Academic Background

- Currently at FNDE (federal autarchy), acting as informal AI solutions leader
- Past startup experience: fintech Jon
- MBA from PUC-RS in Machine Learning applied to business
- Postgrad in Emotional Intelligence (to mitigate communication gaps)
- Daily routine: exercise + meditation for sustained high-performance workload

### Section 5 – English Proficiency Assessment

- Demonstrates technical fluency and communicative confidence
- No daily experience in fully English-speaking companies yet
- Observation: practicing English in NYC was more productive due to nationality diversity; in Florida, strong Latin community frequently shifted conversation back to Spanish
- Quote: "As a Brazilian, I try to speak a lot, but it's very hard for me because I don't have the daily experience. It's only going to change when you start to work for a US or Canadian company." — Antônio Arruda

### Section 6 – Closing & Next Steps

- Henry will send via WhatsApp a detailed script of exactly what Jedo wants to validate
- Antônio must record a screen demo showing his agent pipeline and orchestrator in action
- Video must explain the logic, architecture, and what's happening "under the hood" — not just functional demo
- Jedo's feedback expected within 1 business day after submission
