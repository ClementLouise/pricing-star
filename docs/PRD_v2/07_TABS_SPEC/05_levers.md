# Tab 5 — Strategic Levers

## Purpose

Apply strategic mitigation actions (withdrawals, price floors, delayed launches, DE opt-in) and see their NPV impact in real time. This is where pricing teams "play" with mitigation strategies.

## Reference

V1.7 prototype: `LeversTab` component

## User stories

### US5.1 — Withdraw from low-impact markets

```gherkin
Given I want to protect Method I anchor by withdrawing from a country
When I toggle "Withdraw" for Greece
Then GR is excluded from cascade and Method I/II calculations
And NPV recomputes (likely small loss from GR + smaller MFN rebate)
And the lever is added to scenario.levers.withdrawals
```

### US5.2 — Set price floor for ringfencing

```gherkin
Given Switzerland is my Method I anchor
When I set a price floor of 65% of US list for CH
Then if cascade or any lever would push CH below this, it stays at floor
And a yellow indicator shows "Price floor protecting CH anchor"
```

### US5.3 — Delay launch sequencing

```gherkin
Given I want to delay Brazil's launch to 2029 (after Method I is set in 2028)
When I set "Delayed launch" for BR to 2029
Then BR's IRP rule won't apply for 2027-2028 cascade
And BR's volumes start contributing only in 2029
```

### US5.4 — Toggle DE opt-in (advanced)

```gherkin
Given I'm considering German Medical Research Act opt-in
When I toggle "DE opt-in (Medizinforschungsgesetz)"
Then DE disclosed price drops by 9pp (default)
And cascade re-runs with new DE
And the simulator estimates ex-US NPV impact (~$2.76B harm typical)
```

### US5.5 — Compare lever impact

```gherkin
Given I've applied 3 levers
When I view the "Lever impact" panel
Then I see each lever's individual NPV delta
And the combined effect (which may differ from sum due to interactions)
```

## UI layout

```
┌─────────────────────────────────────────────────────────────┐
│ STRATEGIC LEVERS                                            │
└─────────────────────────────────────────────────────────────┘

┌── WITHDRAWALS ─────────────────────────────────────────────┐
│ Currently launched markets (toggle to withdraw):           │
│  [✓] DE Germany   [✓] FR France   [ ] GR Greece (withdrawn)│
│  ...                                                        │
└────────────────────────────────────────────────────────────┘

┌── PRICE FLOORS (ringfencing) ──────────────────────────────┐
│ Set minimum price as % of US list for protection:          │
│  Country     Floor       Current price    Status           │
│  CH         [65%]        $117,000         🛡 Protected      │
│  IE         [60%]        $108,000                          │
│  NO         [62%]        $111,600                          │
└────────────────────────────────────────────────────────────┘

┌── DELAYED LAUNCHES ────────────────────────────────────────┐
│ Country     Original yr    Delay to                        │
│  BR         2027           [2029 ▾]                        │
│  IN         2027           [None ▾]                        │
└────────────────────────────────────────────────────────────┘

┌── ADVANCED LEVERS ─────────────────────────────────────────┐
│  [ ] DE opt-in (Medical Research Act)                      │
│      ⚠ Estimated −$2.76B ex-US NPV harm                    │
│                                                              │
│  [ ] Method II submission (Guard)                          │
│      Currently: would push benchmark to $50K (worse)       │
└────────────────────────────────────────────────────────────┘

┌── LEVER IMPACT SUMMARY ────────────────────────────────────┐
│ Withdrawals:        −$50M NPV (lost ex-US revenue)         │
│ Price floors:       +$200M NPV (lower MFN rebate)          │
│ Delayed launches:   −$80M NPV (delayed revenue)            │
│ DE opt-in:          −$0M (not active)                      │
│ ──────────────────────────────────                         │
│ Combined:           +$70M NPV                              │
└────────────────────────────────────────────────────────────┘
```

## Components used

- `<Panel />` per lever category
- `<Toggle />` for withdrawals, opt-in, Method II submission
- `<NumberInput format="percentage" />` for price floors
- `<Select />` for delayed launch year
- `<KPICard />` showing per-lever NPV impact
- `<Pill variant="warning" />` for "Protected" / "DE opt-in active"

## Acceptance criteria

- [ ] All 4 lever categories functional independently
- [ ] Each lever change triggers cascade re-run + NPV recalc within 500ms
- [ ] Lever impact summary shows individual + combined effects
- [ ] Toggling DE opt-in clearly warns about estimated NPV harm
- [ ] Price floor enforcement: cascade cannot push price below floor
- [ ] Delayed launch updates IRP rule application timing
- [ ] All lever changes saved to scenario.levers and audit logged

## Edge cases

- **Withdraw from Method I anchor (e.g., CH)**: Show warning "Withdrawing CH may shift Method I to NL/IE/NO. Verify your assumptions."
- **All ex-US markets withdrawn**: Method I/II = null. Block save with explanation.
- **Price floor > current price**: Allow (commitment to higher price); warn that cascade will push price up to floor.
- **Delayed launch beyond LOE**: Block ("Cannot delay launch past loss of exclusivity")
- **DE opt-in with DE not launched**: Block ("Cannot apply DE opt-in if Germany is not launched")
- **Combined lever conflicts**: e.g., withdraw + price floor for same country → show conflict modal, ask user to resolve

## API endpoints used

- `PATCH /scenarios/{id}` — update levers field
- `POST /scenarios/{id}/simulate` — recompute with levers applied
- `POST /scenarios/{id}/de-cascade` — for DE opt-in impact estimate

## Definition of done

- [ ] All levers can be applied independently or combined
- [ ] Lever impact summary updates live
- [ ] Conflicts (e.g., withdraw + floor) are detected and surfaced
- [ ] DE opt-in shows estimated harm prominently before activation

---

*Next: read `06_optimizer.md`*
