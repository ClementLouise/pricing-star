# Reference Materials

This directory contains **read-only reference materials** that the PRD points to. Claude Code should treat these as authoritative source documents — they define the product's expected behavior, business rules, and validation fixtures.

## Hierarchy of authority

When information conflicts, follow this hierarchy (defined in `CLAUDE.md`):

1. **Test fixtures** (`test_results_v11.json`, `test_v20_results.json`) — concrete inputs/outputs
2. **PRD** (`docs/PRD_v2/*.md`) — specifications
3. **V1.7 reference** (`PharmaPricingTool_V1.7.jsx`) — implementation
4. **Business rules** (`pharma_pricing_rules_reference.md`) — domain knowledge
5. **CLAUDE.md** — process and conventions
6. **Training data** — last resort

## Files

### `PharmaPricingTool_V1.7.jsx` ⭐ THE MOST IMPORTANT REFERENCE

168 KB, 2,612 lines of React code. **This is the calculation engine specification.**

Every math function in the production build must be ported from this file with **identical outputs** for the test fixtures. The PRD (`docs/PRD_v2/04_CALC_ENGINE_SPEC.md`) references specific line ranges in this file:

- Lines 367-395: `calculateGenerousPrice`
- Lines 397-416: `calculateGuardMethodI`
- Lines 418-440: `calculateGuardMethodII`
- Lines 442-489: `calculateGlobeMethodI`, `calculateGlobeMethodII`
- Lines 491-510: `calculateGuardRebate`, `calculateGlobeRebate`
- Lines 587-606: `applyCountryIRP`
- Lines 608-628: `runCascade`
- Lines 663-718: `analyzeMFNAnchor` (V1.7 differentiator)
- Lines 720-770: `simulateDECascade` (V1.7 differentiator)
- Lines 772-845: `generateAuditJSON`
- Lines 870-906: `monteCarloG2N`

When in doubt about a calculation's exact behavior, **read the V1.7 source** — don't infer from the PRD alone.

### `pharma_pricing_rules_reference.md` ⭐ BUSINESS RULES MASTER

130 KB markdown document. **The complete reference for all MFN regulations and IRP cascade rules across 43 markets.**

Contents:
- **CMS Generous (Medicaid MFN)** — full rule, basket, references
- **CMS Guard (Medicare Part D MFN)** — full rule including Method I and Method II algorithms
- **CMS Globe (Medicare Part B MFN)** — full rule including Globe-specific phase-in
- **GDP-PPP adjusters** — table for all OECD-19 countries with sources
- **IRP rules per country** — for all 43 markets:
  - Reference basket
  - Calculation rule (avg, min, top3, etc.)
  - Discount applied
  - Cascade timing
  - Source citations
- **Per-region notes** — EU, Asia-Pacific, LATAM, MENA specifics
- **Special cases** — China negotiated, India MIN-from-US, German Medical Research Act, Greek MIN cascade, Brazilian CMED, etc.
- **Phase-in schedules** — year-by-year MFN phase-in for Guard and Globe
- **Definitions and glossary** — every technical term

This file is the **business knowledge backbone**. The PRD assumes Claude Code can refer to this document for any business rule clarification.

### `mfn_asymmetry_framework.docx` and `.pdf`

13-page strategic framework document. Provides the **business context** for why each calculation matters.

Key insight: MFN doesn't bite uniformly. Two test cases (orphan premium, oncology biologic) demonstrate that the same regulation produces $0 NPV impact for one profile and -$894M for another. The product's value proposition is built on this framework.

Read this file to understand:
- Why the Method I anchor analysis (Tab 8) is the differentiating feature
- Why the DE cascade trap (Tab 9) is the second differentiator
- Why audit-grade documentation matters (SOX 404 defensibility)
- Decision rules for classifying any pharma asset's MFN exposure

### `test_results_v11.json`

Validated outputs for **VX-CFTR-NG** (orphan premium asset profile).

Headline results:
- Pre-MFN NPV: $46.74B
- Full MFN NPV: $46.74B (delta = $0, MFN escapes)
- Method I anchor: CH @ $183,938 PPP-adjusted
- Method I benchmark: $187,617 (>US net $185K, no rebate triggers)

Used by `docs/PRD_v2/10_TEST_FIXTURES.md` Fixture A.

### `test_v20_results.json`

Validated outputs for **ONC-mAb-001** (oncology biologic asset profile).

Headline results:
- Pre-MFN NPV: $5.85B
- Full MFN NPV: $4.96B (delta = -$894M, -15.1% erosion)
- Method I anchor: CH @ $55,284 PPP-adjusted
- Method I benchmark: $56,390 (<US net $90K, $33,610/dose rebate triggers)

Used by `docs/PRD_v2/10_TEST_FIXTURES.md` Fixture B.

### `run_vertex_test_v11.py`

18 KB Python script. **Reference Python implementation of the VX-CFTR-NG simulation.**

Particularly useful because:
1. Production backend is Python (per `02_TECH_STACK.md`)
2. This script ports the V1.7 jsx engine to Python
3. Validates Python output matches V1.7 jsx output (same NPV $46.74B)
4. Pattern to follow when implementing the production engine

Read this file when porting calculation functions from V1.7 to the production Python backend.

### `run_oncmab_test_v20.py`

21 KB Python script. **Reference Python implementation of the ONC-mAb-001 simulation.**

Same role as `run_vertex_test_v11.py` but for the oncology profile. Together, these two files prove that the engine is portable and that fixtures are reproducible.

### `pharma_validation_template.xlsx`

46 KB Excel file with 7 sheets. **Validation fixtures in Excel format** — useful for QA team and pricing analysts who want to verify calculations independently.

Sheets:
1. Inputs — asset configurations
2. Country data — prices, volumes, G2N per country
3. Method I calculations — step-by-step
4. Method II calculations — step-by-step
5. Cascade trace — iteration-by-iteration
6. NPV breakdown — year-by-year revenue
7. Audit summary — final results

This file is **not** consumed programmatically. It's a human-readable validation tool. Useful for:
- Validating engine outputs against pen-and-paper calculations
- Onboarding new pricing analysts to the methodology
- Defensibility: showing auditors the math step-by-step

## What Claude Code should do with these files

1. **Read** them when relevant to the current task. Don't try to memorize all 130KB of `pharma_pricing_rules_reference.md`; just `grep` for the country or rule you need.
2. **Cite** them in code comments when implementing a non-obvious behavior:
   ```python
   # Per pharma_pricing_rules_reference.md "Greek MIN cascade",
   # GR uses min() rule and references all EU markets
   def apply_gr_irp(prices: dict[str, float]) -> float:
       ...
   ```
3. **Treat them as immutable**. These are committed reference materials; modifying them is a separate workflow (PRD update + sign-off).
4. **Validate against fixtures** at every Phase 1 milestone. If your engine produces different results from `test_results_v11.json` or `test_v20_results.json`, your engine has a bug.

## What's NOT in this directory (and why)

The following files exist but were **not** included as references because they're either internal tooling or marketing materials:

- Persona briefs, GTM deck, wireframes — useful for product context but not for build
- Architecture diagrams Word doc — superseded by `02_TECH_STACK.md`
- Release notes for V1.7 — historical only

If you need any of these, request access separately.

---

*Back to: `CLAUDE.md` (root)*
