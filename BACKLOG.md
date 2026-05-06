# Pricing Star — Backlog

> Suivi des tâches reportées et améliorations futures. Lu à chaque session
> par Claude Code (cf. CLAUDE.md). Mis à jour à chaque fin de session.

---

## P1 — (vide)

Tous les P1 du PRD v2.0 sont résolus. Voir section Done.

---

## P2 — Polish post-launch (priorisé selon feedback)

### UX improvements
- (À compléter selon feedback utilisateurs réels)

### Performance
- Profile `/simulate` endpoint sous charge réaliste (100+ concurrent simulations)
- Cache reference data (PPP adjusters, IRP rules) au startup avec hot-reload
- Investiguer vectorisation de la boucle `compute_npv` avec numpy
- Benchmark : Method II par année (×14) vs cache invalidation (gain perf marginal vu actuellement < 1ms)

### Documentation
- Génération OpenAPI Swagger UI publique
- Admin runbook pour onboarding tenants
- User guide standalone markdown
- Architecture Decision Records (ADRs) pour les choix majeurs (PPP convention,
  optimistic concurrency, G2N temporel)

### Testing infrastructure
- Pattern test commit cross-session (ref EC-UI-02) à documenter dans
  CLAUDE.md ou dans backend/tests/README.md pour les futurs tests qui
  vérifient des audit logs
- Tests frontend (Playwright) pour les flows critiques

### Operational
- Setup Sentry pour error tracking
- Configurer dashboards de logging structuré (Datadog ou équivalent)
- Database backup automation + restore drill trimestriel
- Synthetic monitoring sur /health et /v1/auth/me

### Future features (v2.1+)
- Multi-asset portfolio view (aggregation cross-assets)
- Custom IRP rule editor pour admins
- Direct integration IQVIA / Eversana / GlobalData APIs
- Markov demand modeling
- EU drug pricing regulations expansion

---

## Done — Resolved items (most recent first)

- ✅ **EC-TRIAL-01** — Real data heuristic detection in trial — commit `5f01143`
- ✅ **EC-UI-02** — Optimistic concurrency control (4 commits)
  - `a7be28a` migration updated_at on CountryData
  - `e222305` backend OCC on PATCH endpoints
  - `d43568b` OCC integration tests
  - `e1baf35` frontend ConflictModal
- ✅ **EC-TRIAL-08** — Duplicate trial signup detection — commit `f7f2347`
- ✅ **EC-TRIAL-05** — Block API key creation in trial — commit `f998809`
- ✅ **EC-COMP-03** — Audit JSON export endpoint — commit `51dd192`
- ✅ **EC-CALC-13** — G2N year vs lifecycle validation — commit `51c420c`
- ✅ **EC-CALC-17** — Method II per-year with G2N time-variant — commit `a02a88d`
- ✅ **EC-AUTH-03** — DELETE /api-keys/{id} revocation — commit `c44c161`
- ✅ **EC-CALC-06** — Strict gt=0 on price fields — commit `888082c`
- ✅ **EC-CALC-01** — 422 on cascade non-convergence — commit `418f074`

---

## Hors scope v2.0 (deferred to v3.0)

- Custom IRP rule editor (admins write Python; UI editor later)
- Multi-asset portfolio aggregation view
- Forecasting beyond 15-year NPV (Markov, demand modeling)
- Direct integration IQVIA / Eversana / GlobalData APIs
- Mobile app (web responsive only)
- Customer-facing public API tier

---

## How to use this file

**For maintainers**: Update at end of each session. Add P2 items as they
emerge from user feedback or operational learnings. Move resolved items
to Done section with the resolving commit hash.

**For Claude Code**: This file is mandatory reading at session start (see
CLAUDE.md). Suggest tackling P2 items when context permits and the user
has bandwidth.
