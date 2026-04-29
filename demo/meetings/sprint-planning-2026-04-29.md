# Sprint Planning — 2026-04-29

**Attendees:** Antonio (Tech Lead), Ana (Backend), Bruno (DevOps), Carla (Product)

---

## Agenda

1. Review last sprint velocity
2. Prioritize backlog for Sprint 12
3. Assign owners for API migration tasks
4. Discuss infrastructure blockers

---

## Decisions

- API gateway migration to Kong approved for Sprint 12
- Authentication will use OAuth2 with refresh tokens (dropped JWT-only approach)
- Rate limiting will be implemented at gateway level, not application level
- Deployment freeze scheduled for May 9th due to client go-live

---

## Action Items

- Antonio → finalize Kong configuration and document setup steps — deadline: 2026-05-03
- Ana → implement OAuth2 token refresh endpoint — deadline: 2026-05-05
- Bruno → provision staging environment with Kong installed — deadline: 2026-05-02
- Carla → write acceptance criteria for rate limiting feature — deadline: 2026-05-01
- Antonio → review and merge open PRs from overnight agent before sprint kickoff — deadline: 2026-04-30

---

## Blockers

- Database migration script from Sprint 11 still not reviewed — blocking Ana's auth work
- Bruno waiting on DevOps approval for new VPS firewall rules — no ETA from infra team

---

## Open Questions

- Which regions will be activated for Phase 2 rollout? (decision needed by May 6th)
- Should rate limiting apply to internal services or only external traffic?
- Is the client SLA 99.9% or 99.5%? Carla to confirm with account manager.

---

## Signals

- Two engineers expressed concern that scope is too broad for a 2-week sprint
- Bruno mentioned the infra team has been slow to respond — possible capacity issue
- Team agreed previous sprint suffered from unclear acceptance criteria — Carla taking ownership
