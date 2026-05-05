# Tab 6 — NPV Optimizer

## Purpose

Heuristic recommendations engine that surfaces the highest-leverage actions for NPV improvement. Also the home for Audit JSON Export (SOX defensibility).

## Reference

V1.7 prototype: `OptimizerTab` component

## User stories

### US6.1 — Run optimization analysis

```gherkin
Given I have a scenario configured
When I click "Run Optimization"
Then the platform analyzes regulations, IRP cascade, levers
And generates 3-7 strategic recommendations ranked by NPV impact
And each recommendation includes: type, target market, rationale, suggested action, confidence level
```

### US6.2 — Apply recommendation

```gherkin
Given the optimizer suggests "Withdraw from GR to protect Method I anchor"
When I click "Apply" on the recommendation
Then the corresponding lever is activated automatically (e.g., GR withdrawal)
And NPV recalculates
And the recommendation moves to "Applied" section
```

### US6.3 — Export audit JSON

```gherkin
As a CFO needing SOX-defensible documentation
When I click "Export Audit JSON" on any simulation
Then a JSON file downloads with:
  - All inputs (asset, prices, regulations, levers)
  - All calculation intermediates (Method I, Method II, anchor analysis)
  - Methodology citations (CMS rule references)
  - Audit trail (6 steps)
  - Disclaimer
And the export action is logged in audit_log
```

### US6.4 — View headline KPIs

```gherkin
When I'm on the Optimizer tab
Then I see 3 KPI cards: Current NPV, Baseline NPV, Δ vs baseline
And the optimization recommendations panel below
```

## UI layout

```
┌──────────────────────────────────────────────────────────────┐
│ NPV OPTIMIZER          [Export Audit JSON]  [Run Optimization]│
└──────────────────────────────────────────────────────────────┘

┌──── HEADLINE METRICS ────────────────────────────────────────┐
│  Current NPV         Baseline (no MFN)    Δ vs baseline      │
│   $4.96B              $5.85B               −$890M (−15.1%)   │
└──────────────────────────────────────────────────────────────┘

┌──── STRATEGIC RECOMMENDATIONS (5) ───────────────────────────┐
│ ① Method II submission                                       │
│   Target: Guard regulation                                   │
│   Rationale: Method II currently $50K vs Method I $56K.     │
│   Submitting Method II won't help (Method I dominates).     │
│   Skip this lever.                                           │
│   Confidence: high   [Don't apply]                           │
│                                                               │
│ ② Withdraw from Greece                                       │
│   Target: GR                                                 │
│   Rationale: GR has lowest ex-US price; withdrawal lifts    │
│   IRP cascade and may shift anchor.                         │
│   Estimated impact: +$120M NPV                              │
│   Confidence: medium   [Apply]                               │
│                                                               │
│ ③ Set price floor in Switzerland (Method I anchor)         │
│   Target: CH                                                 │
│   Rationale: CH @ $55K anchors Method I. Resisting HTA     │
│   pressure to drop CH protects from anchor shift.           │
│   Estimated impact: +$200M NPV (if maintained)              │
│   Confidence: high   [Apply]                                 │
│                                                               │
│ ④ DO NOT opt into German confidential pricing               │
│   Target: DE                                                 │
│   Rationale: Estimated −$2.76B cascade harm vs ~$200M      │
│   confidential rebate gain. Net loss.                       │
│   Confidence: high   [Already not active]                   │
│                                                               │
│ ⑤ Defer Brazilian launch to 2029                           │
│   Target: BR                                                 │
│   Rationale: BR uses MIN rule referencing US. Launching    │
│   post-MFN sets BR price to MFN-reduced US, not full list. │
│   Confidence: medium   [Apply]                               │
└──────────────────────────────────────────────────────────────┘

┌──── APPLIED RECOMMENDATIONS (0) ─────────────────────────────┐
│ (None applied yet)                                           │
└──────────────────────────────────────────────────────────────┘
```

## Components used

- `<Panel />` for each recommendation
- `<Button variant="primary" />` for "Run Optimization"
- `<Button variant="secondary" />` for "Export Audit JSON"
- `<Button variant="link" />` for "Apply" / "Don't apply"
- `<Pill />` for confidence level (high=green, medium=gold, low=gray)
- `<KPICard />` × 3 for headline metrics

## Recommendation generation logic

The optimizer analyzes:

1. **Method II vs Method I**: If Method II < Method I, recommend NOT submitting Method II.
2. **Generous reference market**: Identify the country setting Generous reference; recommend negotiating up or withdrawing if marginal volume.
3. **Method I anchor (CH/IE/NO)**: Recommend price floor protection.
4. **IRP cascade hot-spots**: Identify markets that reference many others (DE, UK, FR); recommend disclosed price discipline.
5. **DE opt-in trap**: Always recommend NOT to opt-in for assets with broad ex-US footprint.
6. **GR withdrawal candidate**: If GR is launched and uses MIN rule, recommend withdrawal evaluation.
7. **Late-launch timing**: For BR/MX/CL using US-reference MIN rule, recommend post-MFN launch sequencing.

Each recommendation includes:
- `type`: category
- `target`: country code or regulation
- `rationale`: explanation in plain English
- `estimated_impact`: NPV delta (if computable)
- `confidence`: high / medium / low
- `action`: lever to apply (if applicable)

## Acceptance criteria

- [ ] "Run Optimization" generates 3-10 recommendations within 2s
- [ ] Recommendations are ranked by absolute NPV impact (descending)
- [ ] Each recommendation has clear rationale, target, action
- [ ] "Apply" button auto-activates corresponding lever
- [ ] "Don't apply" hides recommendation (still logged for transparency)
- [ ] Headline KPI cards update live with current scenario
- [ ] Export Audit JSON triggers browser download with timestamped filename
- [ ] Audit JSON validates against expected schema (all required fields present)

## Edge cases

- **No regulations active**: Only ~2-3 generic recommendations (e.g., "scenario is already optimal")
- **All optimizations already applied**: Show "Your scenario appears optimized" empty state
- **Insufficient data**: Show "Need at least 5 launched markets" empty state
- **Audit JSON > 5MB**: Compress with gzip; download as `.json.gz`

## API endpoints used

- `POST /scenarios/{id}/simulate` for current state
- `POST /scenarios/{id}/anchor-analysis` for anchor info
- `POST /scenarios/{id}/de-cascade` for DE opt-in impact
- `POST /simulations/{id}/audit-export` for JSON export

## Definition of done

- [ ] All 7 recommendation types implemented and tested
- [ ] Recommendations correctly ranked by NPV impact
- [ ] "Apply" auto-applies the corresponding lever in `levers` field
- [ ] Audit JSON contains all sections per `04_CALC_ENGINE_SPEC.md` F14
- [ ] Filename format: `audit_{asset_name}_{scenario_name}_{date}.json`

---

*Next: read `07_compare.md`*
