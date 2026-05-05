# Tab 4 — Rebates & G2N

## Purpose

Configure confidential rebates per country (gross-to-net ratios) and visualize the impact on Method II benchmark + NPV. Supports both static (single value) and time-variant (year-by-year) G2N for accurate modeling of:

- **AMNOG-driven erosion** (DE, FR): G2N declines progressively over 3-5 years post-launch
- **LOE cliff** (any market): G2N drops sharply approaching loss of exclusivity
- **Contract renegotiations**: Multi-year contracts with stepped rebates
- **Generic competition**: Volume + price erosion modeled per-year

Critical for accurate forecasting since list prices ≠ realized revenues, and net realization changes over an asset's lifecycle.

## Reference

V1.7 prototype: `RebatesTab` component (V1.7 supports static G2N only; v2.0 extends with time series)

## Data model

See `03_DATA_MODEL.md` "G2N Time Series resolution" section. Per country in a scenario:

- `g2n_ratio` (decimal): Static fallback. Used when no time series.
- `g2n_time_series` (jsonb): `{"2027": 0.85, "2028": 0.83, ...}`. Optional, year-by-year.

Resolution chain: time series → static override → country reference default.

## User stories

### US4.1 — View G2N defaults (static mode, default view)

```gherkin
Given I'm on the Rebates tab
And no per-year overrides exist for any country
Then I see all launched countries in static mode (single G2N column)
With country defaults from country_reference table pre-filled
And markets with aggressive rebates (G2N < 0.65) highlighted with warning pill
```

### US4.2 — Override static G2N per country

```gherkin
Given I want to model German contract changes
When I edit DE's static G2N from 0.85 to 0.75
Then the override is saved to scenario.country_data.DE.g2n_ratio
And the value applies to all years in the asset lifecycle
And Method II benchmark recomputes within 200ms
And audit log entry is created
```

### US4.3 — Switch a country to time-variant G2N

```gherkin
Given I want to model AMNOG erosion in Germany over 6 years
When I click the "⊕ Time series" button on DE's row
Then the row expands to show 15 year cells (launch_year to launch_year+14)
And each cell is pre-filled with the static G2N value (0.85)
When I edit individual year cells (2028: 0.83, 2029: 0.80, 2030: 0.75, ...)
Then the time series is saved to scenario.country_data.DE.g2n_time_series
And NPV recomputes per-year using resolved G2N values
```

### US4.4 — Bulk paste from Excel

```gherkin
Given I have a row of G2N values in Excel (one per year)
When I click in DE's first year cell and paste (Ctrl+V)
Then the values populate sequential year cells
And invalid values (e.g., > 1.0) are flagged inline
```

### US4.5 — Visualize G2N trajectory

```gherkin
Given DE has a time-variant G2N defined
When I expand DE's row
Then I see a sparkline chart showing G2N over time
And key transition years are annotated (e.g., "AMNOG 2nd renegotiation 2030")
```

### US4.6 — Apply trajectory presets

```gherkin
Given I'm editing DE's time series
When I click "Apply preset ▾"
Then I see options:
  - "AMNOG erosion" (85% Y1 → 78% Y3 → 72% Y5 → 70% terminal)
  - "LOE cliff" (stable until T-2 LOE, then 50% Y-1 LOE, 30% post-LOE)
  - "Linear erosion" (linear from initial to terminal over N years)
  - "Custom" (start from blank)
When I select a preset and confirm
Then the time series is populated automatically
And user can still edit individual cells
```

### US4.7 — Collapse back to static

```gherkin
Given DE has a time series defined
When I click "− Static" on DE's row
Then a confirmation modal asks: "Discard time series and revert to static G2N?"
When I confirm
Then g2n_time_series is cleared (set to null)
And only g2n_ratio is used (static behavior)
```

### US4.8 — Reset all G2N to defaults

```gherkin
Given multiple countries have overrides (static and/or time series)
When I click "Reset all to defaults"
Then a confirmation modal lists what will be cleared
When I confirm
Then all g2n_ratio and g2n_time_series fields are nulled
And country_reference defaults take effect
```

### US4.9 — See per-year G2N impact

```gherkin
Given I have G2N values set (static or time series)
When I view the impact analysis panel
Then I see Method II benchmark for each year of the asset lifecycle
And a "G2N drift" indicator showing how Method II changes year-over-year
And the panel highlights years where Method II crosses the rebate threshold
```

## UI layout

```
┌────────────────────────────────────────────────────────────────────────┐
│ G2N OVERVIEW    [Reset all to defaults]  [Apply industry benchmarks]   │
└────────────────────────────────────────────────────────────────────────┘

┌── COUNTRY G2N OVERRIDES ──────────────────────────────────────────────┐
│ Mode  Country     Default   Current value         Net price    Action  │
│ ───   ──────      ──────    ─────────────         ─────────    ──────  │
│ ▸    🇩🇪 DE       85%       [85%]   (static)      $76,500      ⊕ TS   │
│ ▾    🇫🇷 FR       75%       Time-variant ↘        $58K→$50K    − Stat │
│      ┌──────────────────────────────────────────────────────────────┐ │
│      │ Year  G2N    Net price    Note                              │ │
│      │ 2027  [75%]  $58,050      Initial post-launch               │ │
│      │ 2028  [73%]  $56,502      AMNOG renegotiation 1             │ │
│      │ 2029  [70%]  $54,180      AMNOG renegotiation 2             │ │
│      │ 2030  [68%]  $52,632                                        │ │
│      │ 2031  [65%]  $50,310      Terminal                          │ │
│      │ ...                                                          │ │
│      │                                                              │ │
│      │ Sparkline: ▂▃▄▅▆▇  (visual G2N trajectory)                  │ │
│      │ [Apply preset ▾]  [Bulk paste]  [Reset to static]           │ │
│      └──────────────────────────────────────────────────────────────┘ │
│ ▸    🇨🇭 CH       95%       [95%]   (static)      $52,520 ⚠         │ │
│ ▸    🇮🇹 IT       70%       [70%]   (static)      $50,400           │ │
│ ...                                                                    │ │
└────────────────────────────────────────────────────────────────────────┘

┌── G2N IMPACT ANALYSIS ────────────────────────────────────────────────┐
│ Method II benchmark trajectory:                                        │
│ Year   Benchmark    Δ vs prior   Rebate triggered                     │
│ 2027   $50,423      —            ✗                                    │
│ 2028   $49,890      −1.1%        ✗                                    │
│ 2029   $48,712      −2.4%        ✓ ($1,288/dose)                      │
│ 2030   $47,103      −3.3%        ✓ ($2,897/dose)                      │
│ ...                                                                    │
│                                                                        │
│ ↑ If you assume average G2N is 5pp higher: peak benchmark $52,944    │
│ ↓ If you assume average G2N is 5pp lower:  peak benchmark $47,902    │
│                                                                        │
│ [Run Monte Carlo with ±5pp variation]                                 │
└────────────────────────────────────────────────────────────────────────┘
```

## Components used

- `<DataTable />` for country G2N grid with expand/collapse rows
- Toggle button per row: `⊕ TS` (switch to time series) or `− Stat` (revert to static)
- Inline `<NumberInput format="percentage" />` for G2N values (per-year cells when expanded)
- Sparkline chart inline (Recharts `<LineChart />` simplified)
- `<Select />` for trajectory presets dropdown
- `<Modal />` for confirmation when reverting time series → static
- `<Pill variant="warning" />` for Method I anchor flag and aggressive G2N flag
- `<DataTable />` for Method II yearly trajectory in impact panel

## Trajectory presets

The platform ships with 4 built-in G2N trajectory presets:

### `static` (default)

Single G2N value applied to all years. Backward-compatible with V1.7 behavior.

### `amnog_erosion`

```
Y1 (launch):  initial_g2n           (e.g., 0.85)
Y3:          initial_g2n - 0.07     (e.g., 0.78, after first AMNOG renegotiation)
Y5:          initial_g2n - 0.13     (e.g., 0.72, after second AMNOG renegotiation)
Y6+:         initial_g2n - 0.15     (e.g., 0.70, terminal)
```

Calibrated against typical German pharma experience post-AMNOG (Arzneimittelmarktneuordnungsgesetz).

### `loe_cliff`

```
Y1 to Y(LOE-3):  initial_g2n        (stable, e.g., 0.85)
Y(LOE-2):        initial_g2n - 0.05 (anticipation, e.g., 0.80)
Y(LOE-1):        initial_g2n - 0.20 (e.g., 0.65)
Y(LOE):          0.50               (generic competition begins)
Y(LOE+1):        0.30               (generic erosion)
Y(LOE+2)+:       0.20               (long tail)
```

### `linear_erosion`

```
G2N(year) = initial_g2n - (initial_g2n - terminal_g2n) * (year - launch_year) / (terminal_year - launch_year)
```

User specifies `initial_g2n`, `terminal_g2n`, `terminal_year`. Linear interpolation between.

### `custom`

User defines all years explicitly. No template applied.

## Acceptance criteria

- [ ] Default view: all launched countries in static mode with country_reference defaults
- [ ] Per-row toggle to switch between static and time series
- [ ] Time series mode shows 15 year cells (launch_year to launch_year + 14)
- [ ] Empty year cells fall back to static G2N value (or country default)
- [ ] Inline edit of static G2N: validation 0-100%, save to `g2n_ratio` field
- [ ] Inline edit of per-year G2N: validation 0-100%, save to `g2n_time_series` jsonb
- [ ] Bulk paste from Excel: detects tab-separated or comma-separated values
- [ ] Sparkline visualization for time-variant rows
- [ ] 4 trajectory presets functional (static, amnog_erosion, loe_cliff, linear_erosion, custom)
- [ ] Method II recomputes per year within 500ms after any change
- [ ] Method II yearly trajectory table updates live
- [ ] Reset to static asks for confirmation (data loss warning)
- [ ] Reset all to defaults asks for confirmation (data loss warning)
- [ ] Method I anchor country highlighted with warning pill (anchor logic unchanged)
- [ ] Aggressive G2N (< 0.65) highlighted with warning pill
- [ ] Audit log entries on every G2N change (granular: per-year edit logged separately)
- [ ] Monte Carlo button enabled if at least 5 countries have G2N (static or TS)

## Edge cases

- **G2N > 1.0**: Block at form (impossible mathematically)
- **G2N < 0.05**: Warn ("Extreme rebate; verify with payer team")
- **G2N = 0**: Block ("Use 'withdrawn' flag instead of zero G2N")
- **Time series with single entry**: System treats as static (replicates across all years). Backward-compatible.
- **Time series with sparse years**: Missing years fall back to `g2n_ratio` (static), then country reference default. Documented in audit JSON.
- **Time series year outside asset lifecycle**: Block at form ("Year must be between launch_year and loe_year + 5")
- **Time series with non-monotonic values**: Allow but show notice ("G2N increases in year X — verify intentional")
- **Asset launch year changes after time series defined**: Show warning, offer to shift or clip the series
- **All G2N at default (no overrides)**: No data stored; uses country_reference fallbacks at calc time
- **Bulk paste with > 15 values**: Take first 15, ignore rest, show notice
- **Bulk paste with text/non-numeric**: Show inline error with row indication

## Performance

- Tab load with 43 countries (all static): < 500ms
- Tab load with 5 countries time-variant + 38 static: < 800ms
- Expanding a country row to time series view: < 100ms
- Edit single G2N cell → Method II recompute: < 300ms (debounced)
- Bulk paste of 15 values → save + recompute: < 500ms

## API endpoints used

- `GET /scenarios/{id}` returns full country_data including `g2n_ratio` and `g2n_time_series`
- `PATCH /scenarios/{id}/country-data/{country_code}` updates either field
  - Body example: `{ "g2n_ratio": 0.85 }` (static)
  - Body example: `{ "g2n_time_series": { "2027": 0.85, "2028": 0.83, ... } }` (time series)
  - Body example: `{ "g2n_time_series": null }` (clear time series, revert to static)
- `POST /scenarios/{id}/simulate` recomputes Method II per year using resolved G2N
- `POST /scenarios/{id}/monte-carlo` accepts `g2n_year` parameter for which year to simulate

## Definition of done

- [ ] All 9 user stories pass acceptance criteria
- [ ] All 4 trajectory presets implemented and tested
- [ ] G2N resolution helper (in calc engine) tested against fixtures
- [ ] Per-year Method II in impact panel matches engine output
- [ ] Bulk paste from Excel works for typical workflows
- [ ] Audit JSON includes G2N values per (country, year) used in calculation
- [ ] E2E test: user creates time-variant G2N for DE, runs simulation, verifies NPV uses correct G2N per year

---

*Next: read `05_levers.md`*
