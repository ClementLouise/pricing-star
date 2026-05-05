# Pricing Star — Product Requirements Document

**Version**: 2.0 (build-ready)
**Date**: May 2026
**Status**: Approved for build
**Audience**: Engineering team (humans + Claude Code)

---

## What this is

This dossier specifies the production build of **Pricing Star**, a SaaS platform for mid-cap pharma pricing teams to model and respond to MFN regulations (Generous, Guard, Globe), IRP cascades across 43 markets, and confidential rebate strategies.

The build is **hybrid**: the calculation engine from the V1.7 prototype (`PharmaPricingTool_V1.7.jsx`, 2,612 lines) is treated as a **specification** — the engine's mathematical logic must be preserved. The UI, data layer, authentication, and persistence are to be built fresh, production-grade.

## How to use this PRD

### For humans (eng lead / PM / designer)
Start with `01_PRODUCT_VISION.md` for context, then `11_BUILD_ORDER.md` for the phased roadmap.

### For Claude Code agents
1. **Always read this file first** to understand structure
2. **Read `11_BUILD_ORDER.md`** to understand which phase you're in
3. **Read the relevant section file** for the current task (e.g., `07_TABS_SPEC/01_asset_markets.md`)
4. **Cross-reference** other files via the explicit links in each section
5. **Validate against `10_TEST_FIXTURES.md`** for any calculation work

### File loading order for first-time read

```
00_README.md (this file)
↓
01_PRODUCT_VISION.md       — what we're building and why
02_TECH_STACK.md            — language, framework, infra constraints
03_DATA_MODEL.md            — entities, relations, schemas
04_CALC_ENGINE_SPEC.md      — preserved from V1.7 prototype
05_API_CONTRACTS.md         — REST endpoints
06_UI_COMPONENTS.md         — design system + component library
07_TABS_SPEC/*.md           — one file per tab (9 files)
08_AUTH_PERMISSIONS.md      — SSO, RBAC, multi-tenancy
09_NON_FUNCTIONAL.md        — perf, security, a11y
10_TEST_FIXTURES.md         — input/output pairs for validation
11_BUILD_ORDER.md           — MVP/P1/P2/P3 phasing
12_EDGE_CASES.md            — known edge cases catalog
13_TRIAL_MODE.md            — trial mode architecture (GTM-critical)
```

## Reference materials (provided alongside this PRD)

| File | Purpose |
|------|---------|
| `PharmaPricingTool_V1.7.jsx` | **Reference implementation** of calculation engine. Functions to preserve verbatim are listed in `04_CALC_ENGINE_SPEC.md`. |
| `pharma_pricing_rules_reference.md` | Business rules for MFN regulations and IRP cascade across 43 markets |
| `mfn_asymmetry_framework.docx` | Strategic context — explains why each calculation matters |
| `test_results_v11.json` | Expected outputs for orphan premium asset profile |
| `test_v20_results.json` | Expected outputs for oncology biologic asset profile |
| `wireframes_*.png` | Design references for each tab (in `journeys_wireframes.docx`) |

## Build constraints (non-negotiable)

These are decisions that must NOT be questioned during implementation:

1. **Calculation engine logic preserved verbatim from V1.7**. The CMS multiply convention for PPP adjustment, the Method I/II algorithms, the cascade engine, and the NPV computation are all vetted against test fixtures. Changing these = changing the product.

2. **Multi-tenant SaaS, not single-tenant**. Mid-cap pharma will subscribe; tenant isolation is mandatory at data layer.

3. **No client-side state for sensitive data**. Asset prices, scenarios, audit JSONs are server-side only. Browser is a thin client.

4. **Auth is OIDC/SAML enterprise-grade from day 1**. Even MVP. No "we'll add SSO later".

5. **Audit trail is mandatory for every pricing decision**. SOX 404 is a market requirement for mid-cap pharma CFOs.

## Build constraints (negotiable)

These can be revised by the eng team based on their stack preferences:

- Backend language (Python/Node.js/Go acceptable; engine logic ports trivially)
- Database (Postgres preferred but MySQL acceptable)
- Frontend framework (React preferred — mirrors V1.7 — but Vue/Svelte acceptable)
- Cloud provider (AWS/GCP/Azure — no preference)
- CI/CD pipeline (team's choice)

## What this PRD does NOT specify

- **Sales pricing model** (per-seat vs per-tenant — see business team)
- **Customer onboarding workflow** (TBD with CSM team)
- **Marketing content** (separate brief)
- **Compliance certifications timeline** (SOC 2, ISO 27001 — handled by security team in parallel)
- **Customer support tooling** (Zendesk integration TBD)

## Definition of "done" for v2.0

The build is complete when ALL of the following are true:

- [ ] All 9 tabs from V1.7 reference implementation are functional in production UI
- [ ] All test fixtures in `10_TEST_FIXTURES.md` produce expected outputs (calculation engine validated)
- [ ] V1.8 backlog items (Monte Carlo UI, GR clawback toggle, BR CMED, scenario compare, Method I anchor visual, strategy compare panel) are integrated
- [ ] Multi-tenant SaaS deployment with at least 3 paying tenants live
- [ ] Auth (SSO + MFA), RBAC, audit JSON export functional
- [ ] All non-functional requirements in `09_NON_FUNCTIONAL.md` met
- [ ] All P0 and P1 edge cases from `12_EDGE_CASES.md` handled
- [ ] Performance benchmarks pass: cascade < 200ms, NPV calc < 500ms, page load < 2s
- [ ] Security audit passes (no critical findings)
- [ ] Documentation: API docs, admin guide, user guide

## Versioning

This PRD itself is versioned semantically:
- **2.0** — initial production build spec (May 2026)
- **2.1** — minor refinements (TBD)
- **3.0** — would imply major scope change (e.g., adding new regulatory regime beyond MFN)

Changes to this PRD must be committed alongside the relevant code change to maintain coherence.

## Glossary

Common terms used throughout:

| Term | Definition |
|------|------------|
| **MFN** | Most Favored Nation — US drug pricing models tying US prices to international benchmarks |
| **Generous** | CMS voluntary Medicaid MFN model (Nov 2025) |
| **Guard** | CMS mandatory Medicare Part D MFN model (Dec 2025) |
| **Globe** | CMS mandatory Medicare Part B MFN model (Dec 2025) |
| **Method I** | Default international benchmark = lowest GDP-PPP-adjusted ex-US price × 1.02 |
| **Method II** | Updated international benchmark = volume-weighted avg net price × 1.05 + phase-in |
| **PPP adjuster** | US GDP per capita PPP / Country GDP per capita PPP, with lower bound 1.000 |
| **IRP** | International Reference Pricing — country-level rules where one country's price references others |
| **Cascade** | Sequential application of IRP rules across the global basket until convergence |
| **G2N** | Gross-to-Net ratio — net revenue / gross revenue for a pharma asset |
| **OECD-19** | The 19 reference countries used in Guard/Globe baskets |
| **Anchor** | The country that determines the Method I benchmark (typically CH/IE/NO under multiply convention) |
| **Tenant** | A customer organization (mid-cap pharma) using the SaaS platform |

## Contacts (placeholder)

- Product owner: TBD
- Engineering lead: TBD
- Design lead: TBD
- Security lead: TBD

---

*Next: read `01_PRODUCT_VISION.md`*
