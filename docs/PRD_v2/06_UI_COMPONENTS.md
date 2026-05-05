# UI Components & Design System

## Design philosophy

The platform serves pricing professionals making consequential business decisions. The design must convey:

- **Authority** — this is a tool for serious analysis, not a consumer SaaS
- **Density** — pricing analysts work with lots of data; chrome should be minimal
- **Trustworthiness** — every number should look like it was deliberately rendered

Reference inspirations: Bloomberg Terminal (data density), Linear (modernity), Stripe Dashboard (clarity).

**Anti-patterns to avoid**:
- Cute illustrations (no rocket ships, no high-fives)
- Excessive whitespace (this is not a marketing site)
- Animations beyond functional feedback (no parallax, no fancy transitions)
- Emoji in core UI (acceptable in toasts/empty states only)

## Design tokens

### Color palette

```typescript
export const colors = {
  // Brand
  navy: {
    900: '#0F1B2D',  // Primary navy (headers, primary buttons)
    700: '#1F3251',
    500: '#3D5680',
    300: '#7A8FAB',
    100: '#D9E1ED',
  },
  gold: {
    900: '#8B5E0B',
    500: '#B8860B',  // Accent gold (KPIs, highlights)
    300: '#D4A574',
    100: '#FFF8E1',
  },

  // Functional
  red: {
    700: '#A30000',
    500: '#C00000',  // Errors, MFN exposure indicators
    300: '#FF7B72',
    100: '#FFEBEE',
  },
  green: {
    700: '#1B5E20',
    500: '#2E7D32',  // Positive deltas, "MFN escapes"
    300: '#4AC26B',
    100: '#E8F5E9',
  },
  amber: {
    500: '#F59E0B',  // Warnings, borderline
    100: '#FFF8E1',
  },
  blue: {
    500: '#1976D2',  // Informational, links
    100: '#E3F2FD',
  },

  // Neutrals (dark theme primary)
  gray: {
    50: '#F8F9FA',
    100: '#F1F3F5',
    200: '#E9ECEF',
    300: '#CED4DA',
    400: '#ADB5BD',
    500: '#6C757D',
    600: '#495057',
    700: '#343A40',
    800: '#212529',
    900: '#0D1117',  // Background dark
  },

  // Semantic aliases
  background: '#0D1117',           // App background
  panel: '#161B22',                 // Card/panel background
  panelElev: '#1C2127',             // Elevated panel
  border: '#21262D',                // Default borders
  textPrimary: '#E6EDF3',           // Primary text on dark
  textSecondary: '#8B949E',         // Secondary text
  textTertiary: '#6E7681',          // Tertiary/disabled
  textOnLight: '#212121',           // Text on white background (modals, etc)
};
```

### Typography

```typescript
export const typography = {
  fontFamily: {
    sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif',
    display: 'Calibri, "Segoe UI", system-ui, sans-serif',
    mono: '"SF Mono", "Monaco", "Inconsolata", "Fira Code", monospace',
  },

  // Type scale (rem-based)
  size: {
    xs: '0.75rem',    // 12px - eyebrow labels, captions
    sm: '0.875rem',   // 14px - body small
    base: '1rem',     // 16px - body default
    lg: '1.125rem',   // 18px - section titles small
    xl: '1.25rem',    // 20px - section titles
    '2xl': '1.5rem',  // 24px - page subtitle
    '3xl': '1.875rem',// 30px - page title
    '4xl': '2.25rem', // 36px - hero title
    '5xl': '3rem',    // 48px - extreme hero
  },

  weight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  lineHeight: {
    tight: 1.2,
    snug: 1.4,
    normal: 1.6,
  },
};
```

### Spacing

8px grid. Avoid 5px, 7px, etc.

```typescript
export const spacing = {
  0: '0',
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px',
  20: '80px',
  24: '96px',
};
```

### Borders & radii

```typescript
export const borders = {
  width: { default: '1px', thick: '2px', heavy: '4px' },
  radius: {
    none: '0',
    sm: '2px',
    base: '4px',     // Default for buttons, inputs
    md: '6px',       // Cards
    lg: '8px',       // Modals
    full: '9999px',  // Pills
  },
};
```

### Shadows

```typescript
export const shadows = {
  none: 'none',
  sm: '0 1px 2px rgba(0,0,0,0.5)',
  md: '0 4px 6px rgba(0,0,0,0.5)',
  lg: '0 10px 15px rgba(0,0,0,0.5)',
  inset: 'inset 0 1px 2px rgba(0,0,0,0.5)',
};
```

### Animation

```typescript
export const animation = {
  duration: {
    fast: '150ms',
    base: '250ms',
    slow: '400ms',
  },
  easing: {
    default: 'cubic-bezier(0.4, 0, 0.2, 1)',
    in: 'cubic-bezier(0.4, 0, 1, 1)',
    out: 'cubic-bezier(0, 0, 0.2, 1)',
  },
};
```

## Component library

### Layout components

#### `<AppShell />`

Main app layout wrapper.

```tsx
<AppShell>
  <AppShell.Header />     // Top nav with logo, tenant, user menu
  <AppShell.KPIBar />     // Headline metrics (NPV, Peak Revenue, etc)
  <AppShell.TabNav />     // Horizontal tab navigation
  <AppShell.Content>      // Tab content area
    {children}
  </AppShell.Content>
  <AppShell.Footer />     // Sources, version, classification
</AppShell>
```

#### `<Panel />`

Card container for content sections.

```tsx
<Panel padding="md" elevated={false}>
  {children}
</Panel>
```

Props:
- `padding`: 'none' | 'sm' | 'md' | 'lg' (default 'md' = 24px)
- `elevated`: bool (uses panelElev color when true)
- `bordered`: bool (default true)

#### `<Stack />`

Vertical or horizontal stack with consistent spacing.

```tsx
<Stack direction="vertical" gap="md">
  <Item />
  <Item />
</Stack>
```

#### `<Grid />`

CSS Grid wrapper with responsive columns.

```tsx
<Grid columns={4} gap="md">
  <KPICard />
  <KPICard />
  <KPICard />
  <KPICard />
</Grid>
```

### Form components

#### `<Button />`

```tsx
<Button variant="primary" size="md" onClick={...} disabled={false} loading={false}>
  Run Optimization
</Button>
```

Variants:
- `primary`: Navy bg, white text — main CTAs
- `secondary`: Transparent, navy border — secondary actions
- `ghost`: No border, gray text — subtle actions
- `danger`: Red bg — destructive actions
- `link`: Looks like a link — inline actions

Sizes: `sm` (32px height), `md` (40px), `lg` (48px)

States: default, hover, active, disabled, loading (shows spinner inline)

#### `<Input />`

Text input with label, error, and helper text.

```tsx
<Input
  label="US List Price"
  prefix="$"
  suffix="USD"
  value={price}
  onChange={setPrice}
  error="Must be greater than 0"
  helper="Pre-rebate gross price per patient/year"
/>
```

#### `<NumberInput />`

Numeric input with formatting (thousands separators, currency).

```tsx
<NumberInput
  label="US List Price"
  format="currency"  // 'currency' | 'percentage' | 'integer' | 'decimal'
  precision={0}
  value={180000}
  onChange={setPrice}
/>
```

#### `<Select />`

Dropdown selector.

```tsx
<Select
  label="Therapeutic Area"
  options={[
    { value: 'oncology', label: 'Oncology' },
    { value: 'cf', label: 'Cystic Fibrosis' }
  ]}
  value={area}
  onChange={setArea}
/>
```

#### `<MultiSelect />`

Multi-selection with chips.

#### `<Toggle />` / `<Switch />`

```tsx
<Toggle
  label="Submit Method II"
  description="Voluntarily submit volume-weighted average to CMS"
  checked={submitMethodII}
  onChange={setSubmitMethodII}
/>
```

#### `<Slider />`

Numeric range slider.

```tsx
<Slider
  label="DE opt-in rebate"
  min={0}
  max={0.20}
  step={0.01}
  value={optInPct}
  onChange={setOptInPct}
  format="percentage"
  marks={[
    { value: 0, label: '0%' },
    { value: 0.09, label: '9% (default)' },
    { value: 0.20, label: '20% (max)' }
  ]}
/>
```

#### `<Checkbox />` / `<RadioGroup />`

Standard form controls.

### Data display

#### `<KPICard />`

Headline metric display.

```tsx
<KPICard
  label="14-Year NPV"
  value={5850000000}
  format="currency"
  precision={2}
  delta={-890000000}
  deltaFormat="currency"
  status="negative"  // 'positive' | 'negative' | 'neutral'
  sublabel="Pre-MFN baseline"
/>
```

Renders as:
```
14-YEAR NPV
$5.85B
↓ −$890M (−15.1%)
Pre-MFN baseline
```

#### `<DataTable />`

Sortable, filterable table for tabular data.

```tsx
<DataTable
  columns={[
    { key: 'country', label: 'Country', sortable: true },
    { key: 'price', label: 'Net Price', format: 'currency', align: 'right' },
    { key: 'volume', label: 'Volume', format: 'percentage' },
  ]}
  data={countryData}
  rowKey="country"
  onRowClick={handleClick}
/>
```

Features: sticky header, virtualized rows for large datasets, multi-column sort, column filtering.

#### `<Pill />` / `<Badge />`

Status indicators.

```tsx
<Pill variant="success">MFN escapes</Pill>
<Pill variant="warning">Borderline</Pill>
<Pill variant="danger">Significant exposure</Pill>
```

#### `<Progress />`

Progress bar (used in async job polling).

```tsx
<Progress value={45} max={100} showLabel />
```

### Charts

All charts use Recharts (existing in V1.7).

#### `<NPVWaterfall />`

Custom Recharts BarChart for NPV breakdown.

#### `<CascadeFlow />`

Sankey-like visualization of price flow across markets.

#### `<HeatMap />`

Sensitivity heatmap (Custom Recharts cell-based).

#### `<AnchorRanking />`

Horizontal bar chart for Method I anchor candidates.

### Feedback components

#### `<Toast />`

Top-right corner notification.

```tsx
toast.success("Scenario saved");
toast.error("Cascade failed to converge");
toast.warning("Some countries missing prices");
```

Auto-dismisses after 5 seconds (configurable).

#### `<Modal />`

```tsx
<Modal
  open={open}
  onClose={close}
  title="Delete scenario?"
  size="md"
  footer={
    <>
      <Button variant="ghost" onClick={close}>Cancel</Button>
      <Button variant="danger" onClick={confirm}>Delete</Button>
    </>
  }
>
  This action cannot be undone.
</Modal>
```

#### `<Drawer />`

Slide-out panel from right edge. Used for filter panels, details views.

#### `<Skeleton />`

Loading placeholder.

#### `<EmptyState />`

```tsx
<EmptyState
  icon={<NoData />}
  title="No scenarios yet"
  description="Create your first scenario to see MFN impact"
  action={<Button>Create scenario</Button>}
/>
```

### Navigation

#### `<Tabs />`

Horizontal tab navigation (used for the 9 main tabs).

```tsx
<Tabs activeId={activeTab} onChange={setActiveTab}>
  <Tabs.Tab id="asset" icon={<Settings />} label="Asset & Markets" />
  <Tabs.Tab id="regulation" icon={<Layers />} label="Regulations" />
</Tabs>
```

#### `<Breadcrumbs />`

```tsx
<Breadcrumbs>
  <Breadcrumb href="/assets">Assets</Breadcrumb>
  <Breadcrumb href="/assets/abc">VX-CFTR-NG</Breadcrumb>
  <Breadcrumb current>Full MFN Scenario</Breadcrumb>
</Breadcrumbs>
```

#### `<UserMenu />`

Top-right dropdown with user info, settings, sign out.

### Specialized components (domain-specific)

#### `<CountryFlag />`

Renders 2-letter ISO country code as flag emoji.

```tsx
<CountryFlag code="DE" size="md" showLabel />
// Renders: 🇩🇪 Germany
```

Note: emoji flags don't render in DejaVu Sans server-side. For PDF export, use country names or ISO codes only.

#### `<CountryGrid />`

42-country grid for price/volume input.

```tsx
<CountryGrid
  data={countryData}
  onChange={updateCountry}
  groupBy="region"  // 'region' | 'mfn-basket' | 'alphabetical'
  visibleFields={['list_price', 'net_price', 'volume', 'launched']}
/>
```

#### `<RegulationToggleGroup />`

Three-way toggle for Generous/Guard/Globe activation.

#### `<MFNExposureBadge />`

Color-coded badge for MFN risk classification.

```tsx
<MFNExposureBadge level="significant" />
// Renders: red badge "SIGNIFICANT EXPOSURE"
```

Levels: `minimal` (green), `borderline` (gold), `significant` (red), `severe` (dark red)

#### `<ScenarioCompareTable />`

Side-by-side scenario comparison with delta highlighting.

#### `<MethodIAnchorPanel />`

Visual Method I anchor identification + recommendation.

## Component states

Every interactive component must implement the following states:

| State | Trigger | Visual |
|-------|---------|--------|
| Default | Resting | Base styling |
| Hover | Mouse over | Subtle bg/border change |
| Active | Mousedown | Pressed appearance |
| Focus | Keyboard nav | Visible focus ring (a11y) |
| Disabled | Cannot interact | 50% opacity, no pointer events |
| Loading | Async operation | Inline spinner OR replaced with skeleton |
| Error | Validation failed | Red border + error message below |

## Accessibility requirements

- All interactive elements: keyboard navigable (Tab, Enter, Esc)
- All form inputs: associated `<label>` (no placeholder-only labels)
- Color contrast: WCAG AA minimum (4.5:1 for body text, 3:1 for UI elements)
- Focus indicators: visible 2px ring on all focusable elements
- ARIA labels for icon-only buttons
- Screen reader announcements for async state changes (toast, modal, error)
- Skip-to-content link for keyboard users
- Reduced motion: respect `prefers-reduced-motion`

## Theme

V2.0 ships **dark theme only** (matches V1.7 prototype).

Light theme deferred to v2.1+ (low demand from mid-cap pricing audience who use the tool for hours and prefer dark).

## Responsive design

**Primary target**: 1440px+ desktop (where pricing analysts work).

**Minimum supported**: 1280px (smaller laptops).

**Mobile**: Not supported in v2.0. Display "best on desktop" message below 1024px. The product workflow is incompatible with mobile (massive country grids, dense data tables).

## Component documentation

Each component must be documented with:

- TypeScript prop interface
- 3+ usage examples
- States gallery (default/hover/disabled/loading/error)
- Accessibility notes
- Storybook story (mandatory before merge)

Storybook URL: `https://storybook.pricingstar.example.com`

---

*Next: read `07_TABS_SPEC/01_asset_markets.md`*
