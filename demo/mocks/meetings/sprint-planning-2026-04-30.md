# Sprint Planning — 2026-04-30

**Attendees:** Antonio (Tech Lead), Ana (Backend), Bruno (DevOps), Carla (Product)

---

## Decisions

- Kong API gateway approved for Sprint 12 — replaces NGINX routing layer
- OAuth2 with refresh tokens selected over JWT-only approach
- Deployment freeze confirmed for May 9th — client go-live

---

## Action Items

- Ana → implement OAuth2 token refresh endpoint — deadline: 2026-05-05
- Bruno → provision staging environment with Kong installed — deadline: 2026-05-02

---

## Blockers

- DB migration script from Sprint 11 not reviewed — blocking Ana's auth work
- DevOps approval for new firewall rules still pending — no ETA

---

## Open Questions

- Will rate limiting apply to internal services or external traffic only?
