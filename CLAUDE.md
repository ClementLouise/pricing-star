# CLAUDE.md

This file is read automatically by Claude Code at the start of each session. It defines how Claude Code should behave in this repository.

---

## What this project is

**Pricing Star** — a multi-tenant SaaS platform for mid-cap pharma pricing teams to model and respond to MFN regulations (Generous, Guard, Globe), IRP cascades across 43 markets, and confidential rebate strategies.

**Build status**: Pre-Phase 0. The reference implementation (`reference/PharmaPricingTool_V1.7.jsx`) is a 2,612-line React prototype that defines the calculation engine's expected behavior. The production build is documented in `docs/PRD_v2/`.

**Audience for this codebase**: Mid-cap pharma pricing leads (Sarah Chen persona), CFOs (Marcus Reyes), and Regulatory Affairs (Elena Volkov). The product makes consequential business decisions; rigor and audit-grade defensibility matter more than velocity.

---

## Where to start

Before writing any code, read these files in order:

1. **`docs/PRD_v2/00_README.md`** — entry point and navigation
2. **`docs/PRD_v2/11_BUILD_ORDER.md`** — current phase and dependencies
3. **`docs/PRD_v2/01_PRODUCT_VISION.md`** — why this product exists

Then read the file relevant to the current task. The PRD is structured as 21 markdown files; each is < 500 lines and self-contained with cross-references.

**If a question seems answerable from training data alone (e.g., "should I use React or Vue?"), check the PRD first.** Most architectural questions are explicitly decided in `docs/PRD_v2/02_TECH_STACK.md`.

---

## Non-negotiable rules

These constraints come from `docs/PRD_v2/00_README.md` and must NOT be questioned:

1. **The calculation engine logic is preserved verbatim from V1.7.** Every math function in `reference/PharmaPricingTool_V1.7.jsx` is treated as specification, not as inspiration. Any deviation from V1.7 outputs (validated against `docs/PRD_v2/10_TEST_FIXTURES.md`) is a bug.

2. **Multi-tenant isolation is mandatory at the application layer.** Every database query that touches a domain entity must filter by `tenant_id`. There are NO exceptions, including admin tools.

3. **Auth is OIDC/SAML enterprise-grade from day 1.** No "we'll add SSO later" patterns. Even MVP supports SSO.

4. **Audit logs are append-only.** No UPDATE or DELETE operations on `audit_log` table at any layer. SOX 404 compliance depends on this.

5. **No PII in logs.** Drug pricing data is sensitive but acceptable in logs. User emails should be masked except in dedicated auth events.

6. **Test fixtures must pass before deployment.** The two reference scenarios must produce expected NPVs (VX-CFTR-NG: $46.74B, ONC-mAb-001: $4.96B) within ±0.1% tolerance.

---

## Code conventions

### Language & framework choices

Per `docs/PRD_v2/02_TECH_STACK.md`:

- **Backend**: Python 3.11+ with FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Frontend**: React 18 + TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand
- **Database**: PostgreSQL 15+, Redis 7+ for cache/queue
- **Tests**: pytest (backend), Vitest + React Testing Library (frontend), Playwright (E2E)

If a different choice would be better in a specific context, raise it explicitly — don't silently substitute.

### Style

**Python**:
- Black formatter, line length 100
- Ruff linter with strict mode
- Type hints required on all function signatures
- Docstrings required on public functions and classes
- No `print()` in production code; use structured logging

**TypeScript**:
- Prettier formatter
- ESLint with `@typescript-eslint/strict`
- Strict mode enabled in `tsconfig.json`
- No `any` types except when documented why
- Functional components only; no class components

**General**:
- Files < 400 lines; split if larger
- Functions < 50 lines; refactor if larger
- Variable names descriptive (no `x`, `tmp`, `data2`)
- Comments explain *why*, not *what*

### File organization

```
.
├── frontend/             # React app
│   ├── src/
│   │   ├── components/   # Shared components
│   │   ├── tabs/         # 9 tab implementations
│   │   ├── hooks/        # Custom React hooks
│   │   ├── lib/          # Utilities, API client
│   │   └── types/        # TypeScript types
│   └── tests/
├── backend/              # FastAPI service
│   ├── app/
│   │   ├── api/          # Routers
│   │   ├── engine/       # Calculation engine (PRD §04)
│   │   ├── models/       # SQLAlchemy models (PRD §03)
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── repos/        # Repository pattern (tenant filtering)
│   └── tests/
│       └── fixtures/     # PRD §10 fixtures (must pass)
├── shared/               # Shared types/schemas
├── infrastructure/       # Terraform / IaC
├── docs/
│   ├── PRD_v2/           # Product requirements
│   └── reference/        # V1.7 prototype + materials
└── CLAUDE.md             # This file
```

---

## Workflow expectations

### Starting a new task

1. **Always read the relevant PRD section first.** Do not infer requirements; the PRD is the source of truth.
2. **Check `11_BUILD_ORDER.md` to confirm prerequisites are met.** Don't start Phase 3 work if Phase 1 is incomplete.
3. **Look for existing patterns in the codebase** before creating new ones. Consistency matters.
4. **Write the test first** when implementing a new function. Use fixtures from `10_TEST_FIXTURES.md` where applicable.

### Making changes

1. **Small, focused commits.** One logical change per commit.
2. **Branch naming**: `phase-X/feature-name` (e.g., `phase-1/calc-engine-method-i`)
3. **Commit message format**: Conventional Commits

   ```
   feat(engine): port calculate_guard_method_i from V1.7
   fix(api): tenant filtering missing on assets list endpoint
   test(engine): add fixture for VX-CFTR-NG full MFN scenario
   docs(prd): clarify Method II tolerance in 10_TEST_FIXTURES.md
   ```

4. **PR descriptions** must include:
   - Link to PRD section being implemented
   - Test coverage notes
   - Any deviations from PRD (with justification)

### Asking questions

When a requirement is unclear:

1. **Re-read the PRD section.** Most ambiguity is explained in adjacent paragraphs.
2. **Check `12_EDGE_CASES.md`** — many edge cases are pre-documented.
3. **If genuinely ambiguous**, surface the question with options. Don't guess.

Example of good clarification:

> "PRD §05 specifies `POST /scenarios/{id}/simulate` returns 200 with results. PRD §12 EC-CALC-01 says cascade non-convergence returns 422. What about partial success — cascade converges but Monte Carlo fails? Options: (a) 200 with warning in result body, (b) 422 with error and partial result, (c) 207 multi-status. Recommendation: (a) because Monte Carlo is async and shouldn't block sync simulation. Confirm?"

### Avoiding scope creep

The PRD is the contract. New features = new PRD version (v2.1+), not silent additions during build.

If a customer / sales / ops request comes in mid-build:

- Document it in a `BACKLOG.md` file at repo root
- Continue the current sprint
- Discuss in next planning cycle

---

## Specific guidance per phase

### Phase 0 — Foundation (Weeks 1-2)

Focus: Infrastructure, auth scaffolding, CI/CD. **No business logic yet.**

Read: `docs/PRD_v2/02_TECH_STACK.md` + `docs/PRD_v2/08_AUTH_PERMISSIONS.md` + `docs/PRD_v2/11_BUILD_ORDER.md`

Definition of done: User can SSO-login, see "Hello, [name]" with tenant context, action audit-logged.

### Phase 1 — Calc engine port (Weeks 3-5)

Focus: Mathematical correctness above all else.

Read: `docs/PRD_v2/04_CALC_ENGINE_SPEC.md` + `docs/PRD_v2/10_TEST_FIXTURES.md` + `reference/PharmaPricingTool_V1.7.jsx`

**The reference V1.7 jsx is the source of truth for math.** Don't optimize. Don't refactor. Port verbatim, then verify against fixtures.

Definition of done: All 14 functions ported, all fixtures pass, integration tests green for both VX-CFTR-NG and ONC-mAb-001 scenarios.

### Phase 2 — Data layer + API (Weeks 6-8)

Focus: Persistence, multi-tenancy isolation, API contracts.

Read: `docs/PRD_v2/03_DATA_MODEL.md` + `docs/PRD_v2/05_API_CONTRACTS.md` + `docs/PRD_v2/08_AUTH_PERMISSIONS.md`

**Critical**: Cross-tenant access tests must be added in this phase and run on every PR thereafter. Failure blocks merge.

### Phase 3 — MVP UI (Weeks 9-14)

Focus: First 3 tabs production-grade.

Read: `docs/PRD_v2/06_UI_COMPONENTS.md` + `docs/PRD_v2/07_TABS_SPEC/01-03_*.md`

Build the design system FIRST, then implement tabs against it. Don't proliferate one-off styles.

### Phase 4-6 — Feature expansion

Read the corresponding tab spec files in `docs/PRD_v2/07_TABS_SPEC/`. Each tab has its own user stories, acceptance criteria, and edge cases.

---

## What NOT to do

- ❌ **Don't change calculation engine math** without fixture re-baselining and explicit sign-off
- ❌ **Don't add new dependencies** without justification (open a discussion first)
- ❌ **Don't skip tests** "to move faster" — Phase 1 fixtures are non-negotiable
- ❌ **Don't store secrets in code** or env files; use AWS Secrets Manager / Vault
- ❌ **Don't disable RLS or tenant filters** "temporarily for debugging" — use proper test data
- ❌ **Don't use `any` in TypeScript** without a comment explaining why
- ❌ **Don't add `console.log` to production code** — use the logger
- ❌ **Don't UPDATE or DELETE audit_log entries** at any layer
- ❌ **Don't add features beyond v2.0 scope** without PRD update

---

## What TO do

- ✅ **Read the PRD before coding.** Every section is < 500 lines and answers most questions.
- ✅ **Use fixtures to validate math.** They're pre-baked truth.
- ✅ **Pair-program the calculation engine.** It's the riskiest part of the build.
- ✅ **Surface ambiguity early.** Better to ask than to guess wrong.
- ✅ **Document deviations from PRD** with rationale and approval.
- ✅ **Run the full test suite locally** before pushing.
- ✅ **Keep PRs small and focused.** < 400 lines diff is ideal; < 1000 is acceptable.
- ✅ **Update the PRD** when you discover something it missed (treat it as a living doc).

---

## Backlog & deferred work

This repository maintains a `BACKLOG.md` file at root tracking deferred
work and post-launch improvements. Claude Code should:

1. **Read BACKLOG.md at the start of every session** to know what deferred
   work exists.
2. **Suggest tackling backlog items** when context permits and the user
   has bandwidth (e.g., between phases, after major milestones, when waiting
   for external blockers).
3. **Update BACKLOG.md** at end of session — add new P2 items identified,
   move resolved items to Done with the commit hash.

Hierarchy of priorities:
- **P0** (in PRD `12_EDGE_CASES.md`) — must be done before launch
- **P1** (in PRD or BACKLOG) — must be done before GA
- **P2** (in BACKLOG) — polish post-launch, priorité par feedback
- **Out of scope v2.0** — deferred to v3.0 entirely

---

## Reference materials

Located in `docs/reference/`:

| File | Purpose |
|------|---------|
| `PharmaPricingTool_V1.7.jsx` | Calculation engine reference (2,612 lines React) |
| `pharma_pricing_rules_reference.md` | Business rules for MFN + IRP cascade |
| `mfn_asymmetry_framework.docx` | Strategic context — why each calculation matters |
| `test_results_v11.json` | Expected outputs for VX-CFTR-NG (orphan premium) |
| `test_v20_results.json` | Expected outputs for ONC-mAb-001 (oncology biologic) |
| `run_vertex_test_v11.py` | Reference Python implementation of VX-CFTR-NG simulation |
| `run_oncmab_test_v20.py` | Reference Python implementation of ONC-mAb-001 simulation |

The Python reference scripts are particularly useful — they implement the engine in Python (target language for the production backend) and validate outputs against V1.7 jsx.

---

## Glossary

Quick reference for domain terms used throughout the codebase:

| Term | Definition |
|------|------------|
| **MFN** | Most Favored Nation — US drug pricing models tying US prices to international benchmarks |
| **Generous / Guard / Globe** | The three CMS MFN regulations (Medicaid / Part D / Part B) |
| **Method I** | Lowest GDP-PPP-adjusted ex-US price × 1.02 |
| **Method II** | Volume-weighted avg net price × 1.05 + phase-in |
| **PPP adjuster** | US GDP / Country GDP per capita PPP, with lower bound 1.000 |
| **IRP** | International Reference Pricing — cross-country price referencing rules |
| **Cascade** | Sequential application of IRP rules until convergence |
| **G2N** | Gross-to-net ratio — net revenue / gross revenue |
| **OECD-19** | The 19 reference countries used in Guard/Globe baskets |
| **Anchor** | The country setting Method I benchmark (typically CH/IE/NO) |
| **Tenant** | A customer organization (mid-cap pharma) using the SaaS |

For the full glossary, see `docs/PRD_v2/00_README.md`.

---

## When in doubt

The hierarchy of authority:

1. **Test fixtures** in `docs/PRD_v2/10_TEST_FIXTURES.md` (concrete inputs/outputs)
2. **PRD** in `docs/PRD_v2/*.md` (specifications)
3. **V1.7 reference** in `docs/reference/PharmaPricingTool_V1.7.jsx` (implementation)
4. **CLAUDE.md** (this file — process and conventions)
5. **Training data** (last resort, often outdated)

If sources conflict: fixtures > PRD > V1.7 > CLAUDE.md > training data. Surface conflicts as PRD update candidates.

---

*This file is versioned with the codebase. Updates require PR review like any other code change. Last updated: May 2026, v1.0.*
