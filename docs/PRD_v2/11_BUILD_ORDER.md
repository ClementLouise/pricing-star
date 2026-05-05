# Build Order & Phased Roadmap

**Total estimated duration**: 6 months (24 weeks) for full V2.0 scope
**Team size assumed**: 2 backend, 2 frontend, 1 designer, 1 PM, 0.5 DevOps, 0.5 QA

---

## Phase overview

| Phase | Duration | Outcome |
|-------|----------|---------|
| **Phase 0**: Foundation | Weeks 1-2 | Repo setup, CI/CD, dev environments, auth scaffolding |
| **Phase 1**: Calc engine port | Weeks 3-5 | V1.7 calculation engine ported to backend, fully tested |
| **Phase 2**: Data layer + API | Weeks 6-8 | Postgres schema, REST API, multi-tenant isolation |
| **Phase 3**: MVP UI | Weeks 9-14 | Tabs 1-3 functional (Asset, Regulations, Cascade) |
| **Phase 4**: P1 features | Weeks 15-18 | Tabs 4-7 (Rebates, Levers, Optimizer, Compare) |
| **Phase 5**: V1.7 advanced | Weeks 19-21 | Tabs 8-9 (MFN Anchor, DE Cascade) + Audit JSON |
| **Phase 6**: V1.8 backlog | Weeks 22-24 | Monte Carlo UI, GR clawback, BR CMED, polish |

---

## Phase 0 — Foundation (Weeks 1-2)

### Goal
Get to "hello world" in production environment with auth.

### Tasks
- [ ] Repository setup (monorepo or split frontend/backend — team decides)
- [ ] CI/CD pipeline (build, test, deploy to staging on merge to main)
- [ ] Dev / staging / prod environments provisioned (cloud TBD)
- [ ] Database provisioned (Postgres recommended)
- [ ] OIDC/SAML auth scaffolding (Auth0, AWS Cognito, or self-hosted Keycloak)
- [ ] Multi-tenant data model bootstrap (`tenant_id` on every table)
- [ ] Trial mode scaffolding: `tenant.tier` field, sample asset seeding service stub (see `13_TRIAL_MODE.md`)
- [ ] Logging + monitoring (Sentry, Datadog, or equivalent)
- [ ] Secret management (AWS Secrets Manager, Vault, etc.)

### Definition of done
A user can sign in with SSO, see "Hello, [name]" with their tenant context, and the action is logged in audit trail. No business logic yet.

### Dependencies for next phase
- Auth context propagated to backend
- Tenant isolation tested with 2 dummy tenants

---

## Phase 1 — Calc engine port (Weeks 3-5)

### Goal
Backend implementation of all calculation functions from `PharmaPricingTool_V1.7.jsx`, validated against `10_TEST_FIXTURES.md`.

### Reference files
- `04_CALC_ENGINE_SPEC.md` — function-by-function specification
- `10_TEST_FIXTURES.md` — test inputs/expected outputs
- `PharmaPricingTool_V1.7.jsx` — reference implementation

### Tasks
- [ ] Reference data loaded as constants/config (PPP adjusters, IRP rules, US model baskets)
- [ ] Port `calculateGenerousPrice()` with tests
- [ ] Port `calculateGuardMethodI()` with tests
- [ ] Port `calculateGuardMethodII()` with tests
- [ ] Port `calculateGlobeMethodI()` and `calculateGlobeMethodII()` with tests
- [ ] Port `calculateGuardRebate()` and `calculateGlobeRebate()` with tests
- [ ] Port `applyCountryIRP()` with tests
- [ ] Port `runCascade()` with tests (43-market convergence)
- [ ] Port `projectVolume()` with tests
- [ ] Port `computeNPV()` with tests
- [ ] Port `analyzeMFNAnchor()` (V1.7 new module) with tests
- [ ] Port `simulateDECascade()` (V1.7 new module) with tests
- [ ] Port `monteCarloG2N()` with tests
- [ ] Port `generateAuditJSON()` with tests

### Validation gate
ALL test fixtures in `10_TEST_FIXTURES.md` must pass. NO function may produce a different output than the V1.7 prototype on the same inputs. Any deviation = engineering bug, not feature change.

### Definition of done
Backend exposes `POST /api/calculate` endpoint that runs the full simulation pipeline. Integration test passes with both VX-CFTR-NG and ONC-mAb-001 fixtures producing expected NPVs ($46.74B and $4.96B respectively under full MFN).

### Dependencies for next phase
- Engine ports complete
- Integration tests green in CI

---

## Phase 2 — Data layer + API (Weeks 6-8)

### Goal
Persistence layer, REST API contracts, multi-tenant data isolation.

### Reference files
- `03_DATA_MODEL.md` — entities, relations, schemas
- `05_API_CONTRACTS.md` — endpoints
- `08_AUTH_PERMISSIONS.md` — RBAC, multi-tenancy

### Tasks
- [ ] Database migrations for all entities (`tenant`, `user`, `asset`, `country_data`, `scenario`, `simulation_result`, `audit_log`)
- [ ] Repository layer with tenant filtering (every query auto-filters by `tenant_id`)
- [ ] REST API endpoints implemented per `05_API_CONTRACTS.md`
- [ ] OpenAPI/Swagger documentation generated
- [ ] Rate limiting (per-tenant)
- [ ] API key rotation support (for service accounts)
- [ ] Background job queue for long-running simulations (Monte Carlo with N=500)

### Validation gate
- Tenant A cannot access Tenant B's data via any endpoint (penetration test)
- API documented in OpenAPI; client SDK auto-generated
- All endpoints have unit tests + integration tests

### Definition of done
- Frontend developer can spin up local backend, see API docs, and make authenticated requests against test data
- Cross-tenant access is impossible (verified via security test)

### Dependencies for next phase
- API contracts stable (no breaking changes after this point)

---

## Phase 3 — MVP UI (Weeks 9-14)

### Goal
First three tabs functional in production UI: enough to demo the platform, not yet enough to sell it.

### Reference files
- `06_UI_COMPONENTS.md` — design system + components
- `07_TABS_SPEC/01_asset_markets.md`
- `07_TABS_SPEC/02_regulations.md`
- `07_TABS_SPEC/03_cascade.md`

### Tasks
- [ ] Design system implementation (colors, typography, spacing tokens)
- [ ] Component library: Button, Input, Select, Toggle, Tabs, Modal, Toast
- [ ] Layout shell (top nav, KPI bar, footer)
- [ ] Tab 1: Asset & Markets — country grid, price/volume input, save/load
- [ ] Tab 2: Regulations — scenario toggles for Generous/Guard/Globe
- [ ] Tab 3: IRP Cascade — visualization + cascade execution

### Validation gate
- Internal user (PM, designer, eng lead) can complete a full workflow: launch asset → set regulations → see cascade output
- Lighthouse score ≥ 85 on all 3 tabs

### Definition of done
3 tabs in production with full functionality. Backend round-trip works. Save/load scenario persists across sessions.

---

## Phase 4 — P1 features (Weeks 15-18)

### Goal
Tabs 4-7 functional. Platform is now feature-complete for V1.6 parity.

### Reference files
- `07_TABS_SPEC/04_rebates.md`
- `07_TABS_SPEC/05_levers.md`
- `07_TABS_SPEC/06_optimizer.md`
- `07_TABS_SPEC/07_compare.md`

### Tasks
- [ ] Tab 4: Rebates & G2N — confidential rebate inputs, G2N display
- [ ] Tab 5: Strategic Levers — withdrawal toggles, price floor commitments
- [ ] Tab 6: NPV Optimizer — heuristic recommendations, audit JSON export button
- [ ] Tab 7: Compare — side-by-side scenario comparison with delta highlighting

### Definition of done
V1.6 feature parity reached. Mid-cap pricing lead can do their full job within the platform.

---

## Phase 5 — V1.7 advanced (Weeks 19-21)

### Goal
Differentiating features that no competing tool has.

### Reference files
- `07_TABS_SPEC/08_mfn_anchor.md`
- `07_TABS_SPEC/09_de_cascade.md`

### Tasks
- [ ] Tab 8: MFN Anchor Analysis — auto-identification of Method I anchor
- [ ] Tab 9: DE Cascade Trap Simulator — interactive opt-in modeling
- [ ] Audit JSON Export integrated in Optimizer tab

### Definition of done
V1.7 reference implementation parity reached. Demo-ready for prospect engagements.

---

## Phase 6 — V1.8 backlog (Weeks 22-24)

### Goal
Polish + advanced features that close the loop on enterprise readiness.

### Tasks
- [ ] Monte Carlo G2N UI exposure (sliders + confidence intervals visualization)
- [ ] GR clawback worst-case toggle (55% net floor stress test)
- [ ] BR CMED 3/2025 live/dormant flag
- [ ] Scenario comparison view enhanced (more than 2 side-by-side)
- [ ] Method I anchor visual chart (Recharts integration in Tab 8)
- [ ] Strategy comparison panel (mitigation strategies with NPV deltas)
- [ ] Performance optimization pass (cascade < 100ms, NPV < 250ms)
- [ ] Security audit + remediation
- [ ] Documentation (API docs, user guide, admin guide)
- [ ] First 3 tenants onboarded

### Definition of done
Production launch-ready. Defined in `00_README.md` "Definition of done for v2.0".

---

## Critical path dependencies

```
Phase 0 ─→ Phase 1 ─→ Phase 2 ─→ Phase 3 ─→ Phase 4 ─→ Phase 5 ─→ Phase 6
                          │
                          └─ (parallel) → Auth deepening, security hardening
```

Phase 1 (calc engine) is the **highest-risk** phase. If the engine doesn't pass test fixtures, nothing else matters. Allocate the strongest backend engineer here. Get this right before moving on.

Phase 3 (MVP UI) is the **demo-ready** milestone. After Phase 3, internal demos are possible. After Phase 5, customer demos are possible.

## Risks & mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Calc engine port introduces math errors | Medium | All test fixtures must pass before Phase 1 closes; pair-program complex functions |
| Multi-tenancy bugs leak data | Low but high impact | Penetration test in Phase 2; mandatory code review for any query |
| Performance issues with large baskets | Medium | Benchmark in Phase 2; optimize in Phase 6 |
| CMS rule changes mid-build | High | Build with rule tables as config (not hardcoded); design for hot-swappable rules |
| Scope creep from sales/customer requests | High | Treat this PRD as the contract; new requests = v2.1+ |

## Out-of-scope for v2.0 (deferred to v3.0)

- Custom IRP rule editor (admins write Python scripts; UI rule editor is v3.0)
- Multi-asset portfolio view (v2.0 is per-asset; portfolio view requires separate aggregation layer)
- Forecasting beyond 15-year NPV (no Markov modeling, no demand modeling)
- Direct integration with IQVIA / Eversana / GlobalData APIs (manual upload in v2.0)
- Mobile app (web responsive only)
- Customer-facing API (internal only, no public API tier in v2.0)

---

*Next: read `01_PRODUCT_VISION.md`*
