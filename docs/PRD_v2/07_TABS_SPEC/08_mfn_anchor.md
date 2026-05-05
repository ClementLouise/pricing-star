# Tab 8 — MFN Anchor Analysis

## Purpose

The differentiating feature of v1.7+. Identifies the Method I anchor (typically CH/IE/NO under multiply convention), surfaces non-obvious anchors, and provides ringfencing recommendations.

This is the tab that demonstrates "what Excel cannot do" — automated PPP-aware anchor identification.

## Reference

V1.7 prototype: `MFNAnchorTab` component (lines 2080-2230)

## User stories

### US8.1 — Identify Method I anchor

```gherkin
Given my scenario has at least 5 OECD-19 countries with prices
When I navigate to MFN Anchor tab
Then the Method I anchor is identified automatically
And displayed as a hero KPI: country name, PPP-adjusted price, benchmark
```

### US8.2 — See non-obvious anchor warning

```gherkin
Given the lowest nominal-price country differs from the Method I anchor
When the anchor is identified
Then a yellow alert banner explains:
  "Counter-intuitive anchor detected: lowest nominal price is $X (Italy)
   but PPP-adjusted Method I anchor is $Y (Switzerland)"
And tells me why (PPP=1.000 in CH means no upward adjustment)
```

### US8.3 — Ringfencing recommendation

```gherkin
Given an anchor is identified
Then a recommendation is generated based on:
  - Gap between #1 and #2 candidate
  - Anchor's nominal price level
  - Asset profile (orphan/oncology/specialty)

Examples:
  - "CH anchor is fragile (NL within 5%) — small price changes shift the anchor"
  - "CH firmly anchors Method I (15% gap to next candidate) — most leveraged market"
  - "CH price already at floor — further pressure not advisable"
```

### US8.4 — View anchor ranking

```gherkin
When I view the ranking table
Then I see all OECD-19 countries sorted by PPP-adjusted price ascending
With columns: rank, country, nominal price, PPP adjuster, PPP-adjusted, vs anchor %
And the anchor row is highlighted with anchor icon
```

### US8.5 — Switch between Generous/Guard/Globe baskets

```gherkin
When I click the basket selector
Then I can switch between GENEROUS (MFN-8), GUARD (OECD-19), GLOBE (OECD-19)
And the analysis updates to show that basket's anchor
For Generous: shows 2nd-lowest (the reference rule)
For Guard/Globe: shows lowest (the Method I rule)
```

## UI layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ MFN ANCHOR ANALYSIS    Basket: [GUARD ▾]                            │
└──────────────────────────────────────────────────────────────────────┘

┌──── ⚠ NON-OBVIOUS ANCHOR DETECTED ───────────────────────────────────┐
│ Lowest nominal price is $54,000 (CZ) but Method I anchor is         │
│ $55,284 (CH). Switzerland PPP=1.000 means no upward adjustment;     │
│ Czech Republic PPP=1.573 multiplies its price upward to $84,942.    │
│ This is invisible in Excel-based analysis.                          │
└──────────────────────────────────────────────────────────────────────┘

┌──── HEADLINE KPIs ───────────────────────────────────────────────────┐
│  Method I Anchor   PPP-Adjusted Price   Method I Benchmark   Gap to #2│
│  🇨🇭 CH             $55,284               $56,390               +4.7%  │
│  Switzerland       Nominal $55K × 1.000  × 1.02                vs NL │
└──────────────────────────────────────────────────────────────────────┘

┌──── 🛡 RINGFENCING RECOMMENDATION ───────────────────────────────────┐
│ CH is the binding constraint with 4.7% gap to NL. Price discipline  │
│ in CH directly impacts US Method I.                                  │
│                                                                       │
│ Suggested actions:                                                   │
│  • Resist HTA pressure in CH below $55,000                          │
│  • Set price floor at 60% of US list for CH (currently 55%)         │
│  • Consider withholding from CH if NL becomes anchor                │
└──────────────────────────────────────────────────────────────────────┘

┌──── OECD-19 RANKING ─────────────────────────────────────────────────┐
│ Rank  Country         Nominal     PPP      PPP-Adj      Vs Anchor   │
│ ⚓ #1   🇨🇭 Switzerland  $55,284   1.000   $55,284     ANCHOR        │
│   #2   🇳🇱 Netherlands   $54,354   1.065   $57,887     +4.7%         │
│   #3   🇩🇰 Denmark       $57,117   1.024   $58,488     +5.8%         │
│   #4   🇳🇴 Norway        $58,953   1.000   $58,953     +6.6%         │
│   #5   🇧🇪 Belgium       $53,848   1.197   $64,456     +16.6%        │
│   ...                                                                 │
└──────────────────────────────────────────────────────────────────────┘

┌──── METHODOLOGY NOTE ────────────────────────────────────────────────┐
│ Method I = lowest GDP-PPP-adjusted price across OECD-19 × 1.02       │
│ PPP adjuster from CMS Table 5 (illustrative 2024)                    │
│ Convention: PPP-adjusted = nominal × adjuster (multiply)             │
│ Source: CMS Federal Register § 514.5                                 │
└──────────────────────────────────────────────────────────────────────┘
```

## Components used

- `<Select />` for basket switcher
- Alert banner (yellow/warning style) for non-obvious anchor
- `<KPICard />` × 4 for headline metrics
- `<Panel />` with gold left-border for ringfencing recommendation
- `<DataTable />` for OECD-19 ranking with anchor row highlight
- `<Pill />` for "ANCHOR" tag
- Country flag emoji renderer

## Acceptance criteria

- [ ] Anchor identified within 100ms (computed client-side from already-loaded data)
- [ ] Non-obvious anchor warning displays only when anchor ≠ lowest nominal
- [ ] Ringfencing recommendation generated based on gap thresholds (<5%, 5-15%, >15%)
- [ ] Ranking table sortable by any column
- [ ] Anchor row highlighted with anchor icon and accent color
- [ ] Basket switcher works for GENEROUS, GUARD, GLOBE
- [ ] Methodology note always visible at bottom for defensibility
- [ ] If <5 countries: show empty state "Need at least 5 OECD-19 prices set"

## Edge cases

- **No CH/IE/NO launched**: Show warning "PPP=1.000 markets not launched. Anchor may be unstable; consider launch in CH/IE for ringfencing leverage."
- **Anchor at boundary**: If two countries have identical PPP-adjusted prices, sort by alphabetical fallback; flag as "tied anchor".
- **All countries withdraw or zero price**: Show "No anchor — Method I cannot compute"
- **Generous mode with <2 launched**: Cannot compute (needs 2nd-lowest). Show specific message.
- **Method I anchor changes after lever applied**: Show "Anchor shift detected" notification.

## API endpoints used

- `POST /scenarios/{id}/anchor-analysis` (with `model` query param)

Or computed client-side from cached scenario data + reference data (faster).

## Definition of done

- [ ] Anchor identification works for all 3 baskets
- [ ] Non-obvious anchor warning surfaces correctly
- [ ] Ringfencing recommendations match logic in `04_CALC_ENGINE_SPEC.md` F11
- [ ] Ranking table fully functional
- [ ] Methodology citation always visible
- [ ] Demo-able in 30 seconds for prospect

---

*Next: read `09_de_cascade.md`*
