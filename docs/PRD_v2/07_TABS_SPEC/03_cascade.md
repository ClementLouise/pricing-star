# Tab 3 — IRP Cascade

## Purpose

Visualize and interact with the 43-market International Reference Pricing cascade. Users see how prices propagate across markets when one country's price changes (cascade effect).

## Reference

V1.7 prototype: `CascadeTab` component

## User stories

### US3.1 — Run cascade

```gherkin
Given I have at least 5 countries launched with prices
When I'm on the Cascade tab
Then the cascade runs automatically on tab open
And final prices are displayed for all 43 markets
And the number of iterations to converge is shown
```

### US3.2 — Adjust cascade settings

```gherkin
Given I'm on the Cascade tab
When I toggle "Enable cascade" off
Then prices stay at initial values (no propagation)
When I change "Max iterations" from 5 to 10
Then re-run cascade with new limit
```

### US3.3 — See per-iteration evolution

```gherkin
When I click "Show iteration history"
Then a table appears showing all 5 iteration snapshots
And I can identify which markets stabilized at each iteration
```

### US3.4 — Identify cascade hotspots

```gherkin
Given the cascade has run
When I view the markets list
Then I see indicators for "Most cascading" (markets that drove most changes)
And "Most affected" (markets whose prices changed most)
```

## UI layout

```
┌─────────────────────────────────────────────────────────────┐
│ IRP CASCADE                                                 │
│ [✓] Enable cascade  Max iterations: [5]  [Run again]       │
│                                                             │
│ Cascade converged in 3 iterations                          │
│ Total price changes: 28 markets affected                   │
└─────────────────────────────────────────────────────────────┘

┌── MARKET PRICES (post-cascade) ──────────────────────────┐
│ [Show only changed]  [Group by region]                    │
│                                                            │
│  Country    Initial    Final     Δ        Iters to stable │
│  DE         $90,000    $88,200   -2.0%    2              │
│  FR         $77,400    $73,560   -5.0%    3              │
│  UK         $81,000    $77,544   -4.3%    3              │
│  ...                                                       │
└────────────────────────────────────────────────────────────┘

┌── ITERATION HISTORY ──────────────────────────────────────┐
│ Iter 0 (initial)  Iter 1   Iter 2   Iter 3 (converged)   │
│ DE: $90,000       $90,000  $88,200  $88,200              │
│ FR: $77,400       $73,560  $73,560  $73,560              │
└────────────────────────────────────────────────────────────┘
```

## Components used

- `<Panel />` for cascade controls + results
- `<Toggle />` for enable cascade
- `<NumberInput />` for max iterations (range 1-20)
- `<Button />` for "Run again"
- `<DataTable />` for market prices
- `<DataTable />` for iteration history (with column per iteration)
- `<Pill />` for "converged" / "did not converge" status

## Acceptance criteria

- [ ] Cascade runs automatically on tab open if data sufficient
- [ ] Cascade completes in < 200ms for 43 markets
- [ ] Final prices displayed for all launched markets
- [ ] Initial vs Final delta column shows price change
- [ ] Iteration count and convergence status visible
- [ ] "Show only changed" filter hides markets with delta = 0
- [ ] Iteration history table shows snapshot at each iteration
- [ ] Manual "Run again" button re-executes cascade
- [ ] If max iterations reached without convergence: show warning + suggest increasing max

## Edge cases

- **Cascade does not converge in max_iterations**: Display warning prominently. Suggest increasing max iterations (up to 20). Beyond that, indicates a likely circular IRP rule that should be reported as a bug.
- **No countries launched**: Show empty state.
- **Cascade disabled**: All "final" prices = initial. No iteration history shown.
- **Single country launched**: Cascade trivially converges in 0 iterations.
- **Negotiated countries (CN, IN)**: Show as "Negotiated -65%" / "Negotiated -85%" with no IRP basket.
- **Greek MIN rule**: Show GR's basket-MIN logic separately (warns about aggressive cascade)

## Performance

- Cascade execution: < 200ms (server-side)
- Tab render with results: < 300ms
- Interactive re-run: < 500ms total

## API endpoints used

- `POST /scenarios/{id}/simulate` — returns final_prices and cascade metadata
- (No separate cascade endpoint; it's part of full simulation)

## Definition of done

- [ ] All user stories pass acceptance criteria
- [ ] Performance budget met
- [ ] Iteration history visualization clear
- [ ] Convergence status visually obvious

---

*Next: read `04_rebates.md`*
