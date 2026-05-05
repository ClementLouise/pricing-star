# Tab 1 — Asset & Markets

## Purpose

The entry point for any pricing analysis. Users define the asset (drug profile) and per-country pricing/volume data. This tab is the foundation — all other tabs depend on data entered here.

## Reference

V1.7 prototype: `AssetTab` component at `PharmaPricingTool_V1.7.jsx` line 1330+

## User stories

### US1.1 — Create new asset (PRIMARY)

```gherkin
As a Pricing Lead
I want to define a new pharmaceutical asset
So that I can model its pricing strategy across markets

Given I'm authenticated and have at least 'editor' role
When I navigate to /assets/new
Then I see an empty Asset & Markets form

Given I'm on the new asset form
When I fill in name, indication, US list price, launch year, peak year, LOE year
And I click "Create asset"
Then the asset is created with default values for unspecified fields
And I'm redirected to the asset detail page
And an entry is added to audit_log
```

### US1.2 — Set country prices and volumes

```gherkin
As a Pricing Lead
I want to define list and net prices for each market where the asset will be launched
So that I can run regulatory simulations

Given I'm on an asset's Markets tab
When I click on a country card (e.g., Germany)
Then a side panel opens showing fields for list_price, net_price, volume, launched, launch_year
When I fill in values and click "Save"
Then the country data is persisted to the current scenario
And the country card visually updates to show launched state
And the KPI bar updates with new aggregate metrics
```

### US1.3 — View baseline KPIs

```gherkin
Given I have an asset with at least 5 countries with prices
When I view the Asset & Markets tab
Then the KPI bar shows: 14-Y NPV, Peak Revenue, Total Markets Launched, US Net Price
And these metrics auto-recalculate within 500ms of any input change
```

### US1.4 — Bulk launch in basket

```gherkin
Given I'm on the Markets tab
When I click "Launch in OECD-19" or "Launch in EU-5" preset buttons
Then all countries in that basket get default prices (proportional to US list)
And launched flag is set to true for each
```

### US1.5 — Withdraw from market

```gherkin
Given I have a country with launched=true
When I toggle "Withdraw from this market"
Then withdrawn=true is set
And the country grays out visually
And it's excluded from cascade and Method II calculations
And I see a confirmation modal warning about NPV impact
```

### US1.6 — Import from CSV

```gherkin
As a Pricing Lead with existing Excel data
I want to bulk-import country prices from CSV
So that I don't manually re-enter 43 markets

Given I'm on the Markets tab
When I click "Import CSV"
And I upload a file matching the template (country_code, list_price, net_price, volume)
Then matching countries are populated with values
And validation errors are shown inline (negative prices, unknown country codes)
```

## UI layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ ASSET DETAILS                                                       │
│  Name: [VX-CFTR-NG_______]  Therapeutic area: [Cystic fibrosis ▾]  │
│  Modality: [Small molecule ▾]                                       │
│                                                                     │
│  US list price: [$370,000]  G2N: [50%]  Launch yr: [2027]          │
│  Peak yr: [2032]  LOE: [2042]  Discount rate (WACC): [10%]         │
│                                                                     │
│  US patient pop: [30,000]  Ex-US pop: [50,000]  Capture: [60%]     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ MARKETS  [Group by: Region ▾]  [Launch presets ▾]  [Import CSV]    │
│                                                                     │
│  ┌── EUROPE ──────────────────────────────────────────────────┐     │
│  │  🇩🇪 DE Germany    $288,600  net $245,310 vol 6%  [✓]      │     │
│  │  🇫🇷 FR France     $266,400  net $199,800 vol 6%  [✓]      │     │
│  │  🇬🇧 UK Britain    $277,500  net $222,000 vol 5%  [✓]      │     │
│  │  ... (collapsed groups)                                    │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌── ASIA-PACIFIC ────────────────────────────────────────────┐     │
│  │  🇯🇵 JP Japan     $314,500  net $298,775 vol 5%  [✓]      │     │
│  └────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

## Components used

- `<Panel />` for asset details + markets sections
- `<NumberInput />` for prices, percentages, populations
- `<Select />` for therapeutic area, modality
- `<CountryGrid />` (specialized) — 43-country grid grouped by region
- Country card: clickable, shows aggregate, opens detail drawer on click
- `<Drawer />` for per-country edit (right side)
- `<KPICard />` x4 in the KPI bar at top (NPV, Peak, Markets, US Net)

## Acceptance criteria

- [ ] User can create asset with minimal required fields (name, US list price, launch year, LOE)
- [ ] All asset fields can be edited inline; auto-save on blur (with debounce 500ms)
- [ ] All 43 countries from `country_reference` table render in grid
- [ ] Countries are grouped by region with collapsible sections
- [ ] Click on country card opens drawer with all editable fields
- [ ] Drawer save persists to current scenario
- [ ] KPI bar updates within 500ms of any change
- [ ] Bulk launch presets work for: OECD-19, MFN-8, EU-5, EU-27, US+CA, Custom
- [ ] Withdrawn markets show grayed out visually
- [ ] CSV import accepts the documented schema and shows row-level errors
- [ ] All actions create audit_log entries with `entity_type='asset'`
- [ ] Form validates: prices > 0, years monotonic (launch < peak < loe), volumes 0-1
- [ ] Loading skeleton shown while fetching asset data
- [ ] Empty state shown when asset has 0 launched markets

## Edge cases

- **Asset with 0 markets launched**: KPI bar shows "—" for NPV; tabs 2-9 show "Need at least one launched market" empty state
- **Duplicate country entries**: Block at API level (unique constraint on `scenario_id, country_code`)
- **US not launched**: Cannot run any simulation. Show error in KPI bar.
- **All ex-US markets withdrawn**: Method I/II cannot compute. Tabs 2-3 show appropriate empty states.
- **Negative prices entered**: Block at form validation; if API receives, return 400 validation error
- **Year before 2026**: Allow (historical asset analysis). Phase-in calculations use minimum year 2026.
- **Year after 2050**: Block at form (unrealistic).
- **Unsaved changes when navigating away**: Show "You have unsaved changes" modal

## Performance

- Initial load: < 1.5s
- Country card click → drawer open: < 100ms
- Auto-save after edit: < 500ms (debounced)
- Bulk launch preset: < 300ms (43 countries updated)
- KPI recalculation after edit: < 500ms (calls calc engine)

## API endpoints used

- `GET /assets/{asset_id}` — load asset
- `PATCH /assets/{asset_id}` — update asset fields
- `GET /scenarios/{scenario_id}` — load current scenario (with country_data)
- `PATCH /scenarios/{scenario_id}/country-data/{country_code}` — update country
- `POST /scenarios/{scenario_id}/simulate` — for KPI bar refresh

## Definition of done

- [ ] All user stories pass acceptance criteria
- [ ] All edge cases handled
- [ ] Performance budgets met
- [ ] Storybook stories for all new components
- [ ] Unit tests for form validation
- [ ] E2E test: full "create asset + launch in 5 markets + see KPIs" flow
- [ ] Accessibility: keyboard nav, screen reader announcements
- [ ] Audit log entries created for all mutations

---

*Next: read `02_regulations.md`*
