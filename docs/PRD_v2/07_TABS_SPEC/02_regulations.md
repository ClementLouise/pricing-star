# Tab 2 — Regulations

## Purpose

Configure which MFN regulations (Generous, Guard, Globe) are active and their parameters (year, Method II submission, phase-in). The platform models the regulatory regime; this tab controls *which* regime applies to the current scenario.

## Reference

V1.7 prototype: `RegulationTab` component

## User stories

### US2.1 — Toggle regulations on/off

```gherkin
Given I'm on the Regulations tab
When I toggle "Generous" to active
Then the scenario's regulations.generous.active = true
And the KPI bar updates to show MFN-affected NPV
And an audit_log entry is created
```

### US2.2 — Configure Generous

```gherkin
Given Generous is active
When I set the launch year to 2027 and Medicaid share to 7%
Then these values are persisted
And US net price calculation includes Medicaid blending in NPV
```

### US2.3 — Configure Guard with Method II submission

```gherkin
Given Guard is active
When I toggle "Submit Method II to CMS"
Then the system computes Method II benchmark using current volumes/G2N
And displays both Method I and Method II values
And uses max(M.I, M.II) as the applicable benchmark
```

### US2.4 — Configure Globe

```gherkin
Similar to Guard but with -35% terminal phase-in (vs -30% for Guard)
Globe applies to Part B (oncology, biologics) — show Part B share from asset
```

### US2.5 — Phase-in year selection

```gherkin
Given a regulation is active
When I change the active year (2026, 2027, 2028, 2029, 2030)
Then the phase-in adjustment auto-updates per the schedule
And Method II benchmark recomputes
```

### US2.6 — Quick-presets

```gherkin
Given I want to compare scenarios fast
When I click "Pre-MFN" preset
Then all regulations are set to inactive
When I click "Full MFN 2029" preset
Then Generous=2027, Guard=2028, Globe=2029, all active
```

## UI layout

```
┌─────────────────────────────────────────────────────────────┐
│ REGULATORY SCENARIO  [Save scenario]  [Quick presets ▾]    │
└─────────────────────────────────────────────────────────────┘

┌── GENEROUS (Medicaid MFN) ─────────────────────────────────┐
│ [✓] Active     Year: [2027 ▾]   Medicaid share: [7%]      │
│ Reference: 2nd-lowest GDP-PPP in MFN-8 basket             │
│ Current reference: DK @ $58,488                            │
└────────────────────────────────────────────────────────────┘

┌── GUARD (Medicare Part D MFN) ─────────────────────────────┐
│ [✓] Active     Year: [2028 ▾]   Phase-in: -30%            │
│ [ ] Submit Method II                                        │
│ Method I (default): CH @ $56,390                          │
│ Method II (vol-weighted): $50,423                          │
│ Applicable benchmark: $56,390 (Method I dominates)        │
└────────────────────────────────────────────────────────────┘

┌── GLOBE (Medicare Part B MFN) ─────────────────────────────┐
│ [✓] Active     Year: [2029 ▾]   Phase-in: -35%            │
│ [ ] Submit Method II                                        │
│ Method I (default): CH @ $56,390                          │
│ Method II: $48,025                                         │
│ Asset Part B share: 85%                                    │
└────────────────────────────────────────────────────────────┘

┌── REBATE SUMMARY ──────────────────────────────────────────┐
│ Per-unit rebate: $33,610                                   │
│ Effective US net: $56,390 (37% erosion vs $90K baseline)  │
│ Annual rebate impact (peak year): −$403M                   │
└────────────────────────────────────────────────────────────┘
```

## Components used

- `<Panel />` × 3 (one per regulation)
- `<Toggle />` for active flag
- `<Select />` for year picker
- `<NumberInput />` for Medicaid share, phase-in (read-only)
- `<KPICard />` for benchmark values
- Quick preset dropdown

## Acceptance criteria

- [ ] All 3 regulations independently toggleable
- [ ] Year picker constrained to 2026-2031 range
- [ ] Phase-in values displayed (read-only, derived from year)
- [ ] Method I and Method II values computed live (< 200ms)
- [ ] Applicable benchmark shown with explanation (which method dominates)
- [ ] Quick presets: "Pre-MFN", "Generous only", "Generous + Guard", "Full MFN", "Stress test (worst case)"
- [ ] Save scenario triggers POST to API
- [ ] Audit log entry on every toggle change

## Edge cases

- **No countries launched in OECD-19**: Method I/II = null. Show "Insufficient data" with link to Asset tab.
- **Submit Method II but volumes are all zero**: Method II returns null. Show warning "Cannot compute Method II without volumes."
- **Year selected before launch year**: Block at form ("Regulation cannot apply before asset launches")
- **All 3 regulations off**: Show "Pre-MFN baseline" as the scenario name suggestion
- **Tenant on trial subscription**: Allow toggling but show watermark "Trial — full access in paid plan"

## API endpoints used

- `PATCH /scenarios/{id}` — update regulations field
- `POST /scenarios/{id}/simulate` — compute benchmarks

## Definition of done

- [ ] Toggling any regulation updates scenario in < 500ms
- [ ] All quick presets work correctly
- [ ] Live calculation of Method I/II without page reload
- [ ] Help text explains each regulation's effect
- [ ] Click "?" icon next to each regulation opens documentation drawer

---

*Next: read `03_cascade.md`*
