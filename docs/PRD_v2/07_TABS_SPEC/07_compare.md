# Tab 7 — Compare

## Purpose

Side-by-side comparison of 2-5 scenarios with delta highlighting. Used for "before/after mitigation" stories, A/B strategy evaluation, and CFO presentations.

## Reference

V1.7 prototype: `CompareTab` component (single comparison only); v2.0 enhances to multi-scenario.

## User stories

### US7.1 — Compare baseline vs current

```gherkin
Given my asset has a baseline scenario and I'm working on a new scenario
When I navigate to Compare tab
Then by default it shows current scenario vs baseline
And displays NPV, Method I, peak revenue, US net side-by-side
And deltas are color-coded (green=positive, red=negative)
```

### US7.2 — Add additional scenarios

```gherkin
Given I'm comparing 2 scenarios
When I click "Add scenario" and select a third saved scenario
Then it appears as a new column
And deltas vs baseline are shown for the new column
And the comparison supports up to 5 scenarios
```

### US7.3 — Yearly P&L view

```gherkin
Given I'm comparing scenarios
When I scroll to "Yearly P&L"
Then I see a table with one row per year (launch year to LOE+5)
And one column per scenario showing year revenue
And a final column showing delta vs baseline
```

### US7.4 — Export comparison

```gherkin
When I click "Export comparison"
Then I can choose format: PDF (formatted report) or XLSX (raw data)
And the export captures all scenarios shown
And includes audit metadata
```

## UI layout

```
┌──────────────────────────────────────────────────────────────────┐
│ COMPARE SCENARIOS                  [Add scenario] [Export ▾]    │
└──────────────────────────────────────────────────────────────────┘

┌──── HEADLINE METRICS ────────────────────────────────────────────┐
│                Baseline         Full MFN           Mitigated     │
│  14-Y NPV       $5.85B          $4.96B (-15%)      $5.40B (-8%) │
│  Peak Revenue   $930M           $790M (-15%)       $850M (-9%)  │
│  Method I       —               $56,390            $66,200      │
│  Method I anchor —              CH                 IE           │
│  Per-unit rebate —              $33,610            $23,800      │
│  Effective US net $90,000        $56,390            $66,200      │
│  Compliance     Pre-MFN         G+G+G              G+G+G        │
└──────────────────────────────────────────────────────────────────┘

┌──── YEARLY P&L ──────────────────────────────────────────────────┐
│ Year   Baseline    Full MFN     Mitigated     Δ Mit vs Base     │
│ 2027    $972M       $786M        $880M         −$92M             │
│ 2028   $1944M      $1568M       $1764M         −$180M            │
│ 2029   $1944M      $1568M       $1764M         −$180M            │
│ ...                                                               │
└──────────────────────────────────────────────────────────────────┘

┌──── PER-COUNTRY DELTAS ──────────────────────────────────────────┐
│ Country   Baseline    Full MFN    Mitigated    Δ Mit vs Base    │
│ US        $90,000     $56,390     $66,200      −$23,800          │
│ DE        $76,500     $74,970     $74,970      −$1,530           │
│ FR        $58,050     $55,148     $55,148      −$2,902           │
│ ...                                                               │
└──────────────────────────────────────────────────────────────────┘
```

## Components used

- `<Panel />` for each section (headline, yearly, per-country)
- `<DataTable />` for tabular data (sortable, virtualized for many countries)
- `<Button variant="secondary" />` for Add scenario, Export
- `<Modal />` for "Select scenario to add"
- Color-coded cells (green/red) for delta values

## Acceptance criteria

- [ ] Compare 2-5 scenarios side-by-side
- [ ] Headline metrics row: NPV, Peak Rev, Method I, anchor, rebate, effective US net, compliance status
- [ ] Yearly P&L table with delta column
- [ ] Per-country delta table
- [ ] Export to PDF (formatted report) and XLSX (raw data)
- [ ] PDF export includes asset/scenario metadata + branding
- [ ] All comparisons use same engine version (warn if different)

## Edge cases

- **Comparing scenarios from different assets**: Block at scenario picker (only show scenarios from current asset)
- **One scenario has no simulation result**: Show "Run simulation first" empty state for that column
- **Engine version mismatch**: Show warning "Scenarios were computed with different engine versions; results may not be directly comparable. Re-run all to get apples-to-apples."
- **More than 5 scenarios selected**: Block (visual clutter)

## API endpoints used

- `POST /scenarios/compare` with array of scenario IDs

## Definition of done

- [ ] 5-scenario comparison rendering correctly
- [ ] Yearly P&L table virtualizes for long horizons
- [ ] PDF export looks production-grade (not a screenshot)
- [ ] XLSX export importable into Excel without formatting issues

---

*Next: read `08_mfn_anchor.md`*
