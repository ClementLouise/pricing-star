# Tab 9 — DE Cascade Trap Simulator

## Purpose

Interactive simulator quantifying the impact of the German Medical Research Act (March 2026) confidential pricing opt-in. The opt-in offers ~9pp lower disclosed German price in exchange for confidential rebate access — but cascades to ~27 markets via IRP, often causing massive ex-US NPV harm.

This is the second differentiating feature of v1.7+. Prospects often have NEVER quantified this trap.

## Reference

V1.7 prototype: `DECascadeTab` component (lines 2235-2440)

## User stories

### US9.1 — Quantify DE opt-in impact at default 9pp

```gherkin
Given I have a scenario with Germany launched
When I navigate to DE Cascade tab
Then I see the default 9pp opt-in slider
And the simulator shows:
  - DE disclosed price before/after
  - Number of markets affected (typically 8-12 of 27 referencing)
  - Estimated ex-US NPV impact (typically -$1B to -$5B for mid-cap)
```

### US9.2 — Adjust opt-in rebate slider

```gherkin
Given I'm on DE Cascade tab
When I drag the slider from 9% to 15%
Then the simulation re-runs in real-time (debounced 200ms)
And impact metrics update accordingly
```

### US9.3 — See per-market impact

```gherkin
When the simulation runs
Then I see a table listing all DE-referencing markets that were affected
With columns: country, price before/after, delta absolute, delta %, annual revenue impact
And rows are sorted by annual revenue impact (most negative first)
```

### US9.4 — See decision recommendation

```gherkin
Given the simulator computes impact
When the estimated NPV harm exceeds $1B
Then a red recommendation banner appears:
  "DO NOT opt into German confidential pricing for this asset.
   Estimated harm $X.XXB exceeds typical confidential rebate gain (~$200M)."
And the recommendation is computed using `analyze_de_opt_in_recommendation()` heuristic
```

### US9.5 — Educational context

```gherkin
Given a user is unfamiliar with the DE opt-in mechanism
When they hover the "?" icon next to "DE opt-in"
Then a tooltip explains:
  "The German Medical Research Act (Mar 2026) lets manufacturers opt into
   confidential pricing in exchange for ~9pp lower disclosed price.
   Because 27 ex-US markets reference Germany, this disclosed cut cascades
   broadly. The platform quantifies this 27-market cascade, which is
   invisible to Excel-based analysis."
```

## UI layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ DE CASCADE TRAP SIMULATOR  [?]                                       │
└──────────────────────────────────────────────────────────────────────┘

┌──── OPT-IN SLIDER ───────────────────────────────────────────────────┐
│ DE disclosed price reduction (opt-in rebate)            -9.0 pp      │
│ Med Research Act offers ~9% lower disclosed price for                │
│ confidential pricing access                                          │
│                                                                       │
│ [---------●----------------------]                                   │
│  0%    9% (default)         20% (max)                                │
└──────────────────────────────────────────────────────────────────────┘

┌──── HEADLINE METRICS ────────────────────────────────────────────────┐
│  DE Before     DE After      Markets affected    Estimated NPV impact│
│  $90,000       $81,900       8 / 27              -$2.76B             │
│  Disclosed     Δ -$8,100     27 reference DE    ≈ 8x annual harm     │
└──────────────────────────────────────────────────────────────────────┘

┌──── ⚠ RECOMMENDATION: DO NOT OPT-IN ─────────────────────────────────┐
│ The cascade harm exceeds typical confidential rebate benefit.        │
│ Estimated cost: -$2.76B in 14-year ex-US NPV                         │
│ Typical confidential rebate gain: ~$200M                             │
│ Net impact: -$2.56B                                                  │
└──────────────────────────────────────────────────────────────────────┘

┌──── PER-MARKET CASCADE IMPACT ───────────────────────────────────────┐
│ Country     Before      After       Δ           Δ%         Annual   │
│ 🇦🇹 AT       $81,000     $65,610     -$15,390    -19.0%    -$48M     │
│ 🇳🇱 NL       $77,400     $62,694     -$14,706    -19.0%    -$71M     │
│ 🇧🇪 BE       $77,400     $62,694     -$14,706    -19.0%    -$26M     │
│ 🇬🇧 UK       $81,000     $65,610     -$15,390    -19.0%    -$56M     │
│ 🇫🇷 FR       $77,400     $62,694     -$14,706    -19.0%    -$71M     │
│ 🇨🇭 CH       $99,000     $80,190     -$18,810    -19.0%    -$8M      │
│ 🇩🇰 DK       $81,000     $65,610     -$15,390    -19.0%    -$8M      │
│ 🇸🇪 SE       $81,000     $65,610     -$15,390    -19.0%    -$15M     │
└──────────────────────────────────────────────────────────────────────┘

┌──── EDUCATIONAL NOTE ────────────────────────────────────────────────┐
│ Why this matters: Most pricing analysts focus on the German rebate   │
│ calculation alone. They miss the 27-market cascade because it's      │
│ invisible in Excel. This simulator surfaces it in seconds — exactly  │
│ the type of insight that justifies dedicated MFN-aware tooling.      │
└──────────────────────────────────────────────────────────────────────┘
```

## Components used

- `<Slider />` for opt-in percentage (0-20%, step 1%)
- `<KPICard />` × 4 for headline metrics
- Red callout banner for "DO NOT OPT-IN" recommendation
- `<DataTable />` for per-market impact (sortable)
- Tooltip component for educational context

## Acceptance criteria

- [ ] Slider drag triggers re-simulation within 300ms (debounced)
- [ ] All DE-referencing markets identified from IRP_RULES
- [ ] Per-market impact table shows only affected markets (delta != 0)
- [ ] Sorted by annual revenue impact (most negative first)
- [ ] Estimated NPV impact = annual_impact × discount_multiplier (≈8 for 14y at 10% WACC)
- [ ] Recommendation banner appears when NPV harm > $1B
- [ ] If DE not launched: empty state with link to launch
- [ ] Tooltip explains DE opt-in mechanism

## Edge cases

- **DE not launched**: Empty state. Cannot run simulation.
- **Slider at 0%**: All deltas = 0. "No impact (no opt-in)."
- **No DE-referencing markets launched**: Show "DE opt-in would have minimal cascade impact (no referencing markets launched)."
- **Asset has no ex-US presence**: Same as above; suggest "DE opt-in may be acceptable for US-only assets" with caveat about future launches.
- **Very high opt-in rate (15%+)**: NPV harm > $5B. Banner still says DO NOT, but with stronger language.
- **Slider modification during async simulation**: Cancel previous request; only show latest result.

## Performance

- Slider drag → simulation result: < 300ms (debounced 200ms + cascade < 200ms = stretches budget)
- Initial tab load with auto-simulation: < 500ms

## API endpoints used

- `POST /scenarios/{id}/de-cascade` with `{ opt_in_rebate_pct: 0.09 }`

## Definition of done

- [ ] Slider responsive and feels smooth
- [ ] All DE-referencing markets surface correctly
- [ ] Recommendation banner triggers at $1B threshold
- [ ] Demo-able in 30 seconds (the "wow" moment)
- [ ] Educational note clearly explains the value vs Excel

---

*This is the last tab spec. Next: read `08_AUTH_PERMISSIONS.md`*
