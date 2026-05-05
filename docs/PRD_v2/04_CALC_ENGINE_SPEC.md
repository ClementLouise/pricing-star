# Calculation Engine Specification

## Overview

The calculation engine is the **mathematical core** of the platform. Every formula is derived from CMS regulatory texts (Generous, Guard, Globe NPRMs December 2025) or from established IRP rules across 43 countries.

**Reference implementation**: `PharmaPricingTool_V1.7.jsx` (delivered alongside this PRD). Functions to port are listed below with line ranges and exact behavior to preserve.

**Validation**: Every function must produce identical outputs to the V1.7 reference for the test fixtures in `10_TEST_FIXTURES.md`. Any deviation is a bug.

## Engine architecture

```
                ┌─────────────────────────────┐
                │   Reference Data (config)   │
                │  PPP adjusters, baskets,    │
                │  IRP rules, phase-ins       │
                └──────────────┬──────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼────────┐  ┌──────────▼─────────┐  ┌────────▼─────────┐
│ Pure functions │  │ Composite engines  │  │ Analysis modules │
│                │  │                    │  │                  │
│ • Method I     │  │ • Cascade runner   │  │ • Anchor         │
│ • Method II    │  │ • NPV computation  │  │ • DE cascade     │
│ • Generous     │  │ • Volume projection│  │ • Monte Carlo    │
│ • Guard rebate │  │                    │  │ • Audit JSON     │
│ • Globe rebate │  │                    │  │                  │
│ • IRP per-ctry │  │                    │  │                  │
└────────────────┘  └────────────────────┘  └──────────────────┘
```

## Reference data constants

These are loaded from `country_reference` and `us_model_basket` tables at startup. Hot-reload supported (no service restart needed when CMS publishes updated values).

### `GDP_PPP_ADJUSTERS`

Map of country code → PPP adjuster (US/Country, lower bound 1.000).

Values in V1.7 (from CMS Table 5 illustrative 2024):

```python
GDP_PPP_ADJUSTERS = {
    "US": 1.000, "CA": 1.332, "FR": 1.385, "DE": 1.202, "IT": 1.422, "JP": 1.638,
    "UK": 1.438, "AU": 1.256, "KR": 1.498, "NL": 1.065, "ES": 1.560, "AT": 1.193,
    "BE": 1.197, "CZ": 1.573, "IE": 1.000, "NO": 1.000, "SE": 1.193, "CH": 1.000,
    "DK": 1.024, "IL": 1.596,
    # Non-OECD-19 markets used for IRP cascade only (not MFN benchmarks):
    "BR": 2.85, "MX": 2.60, "AR": 3.10, "CO": 2.95, "CL": 2.20,
    "CN": 2.40, "IN": 4.20,
    "PL": 1.85, "HU": 1.85, "RO": 1.85, "SK": 1.573, "BG": 1.85,
    "GR": 1.385, "PT": 1.385, "FI": 1.193,
    "SA": 1.90, "AE": 1.75, "TR": 3.20
}
```

### `US_MODEL_BASKETS`

```python
US_MODEL_BASKETS = {
    "GENEROUS": ["UK", "FR", "DE", "IT", "CA", "JP", "DK", "CH"],
    "GUARD":    ["AU","AT","BE","CA","CZ","DK","FR","DE","IE","IL","IT","JP","NL","NO","KR","ES","SE","CH","UK"],
    "GLOBE":    ["AU","AT","BE","CA","CZ","DK","FR","DE","IE","IL","IT","JP","NL","NO","KR","ES","SE","CH","UK"]
}
```

GUARD and GLOBE share the same 19-country basket. Generous uses MFN-8 (G-7 minus US, plus Denmark and Switzerland).

### `GUARD_PHASEIN` and `GLOBE_PHASEIN`

Method II phase-in adjustments by year:

```python
GUARD_PHASEIN = {2026: -0.10, 2027: -0.20, 2028: -0.30, 2029: -0.30, 2030: -0.30, 2031: -0.30}
GLOBE_PHASEIN = {2026: -0.10, 2027: -0.20, 2028: -0.30, 2029: -0.35, 2030: -0.35, 2031: -0.35}
```

GLOBE has steeper terminal phase-in (−35%) vs GUARD (−30%).

### `IRP_RULES`

Per-country IRP basket and discount rules. See `pharma_pricing_rules_reference.md` for complete listing. Schema:

```python
IRP_RULES = {
    "DE": {"basket": ["UK","FR","IT","ES","NL","BE","AT","DK","SE","FI"], "rule": "avg", "discount": 0.05},
    "FR": {"basket": ["UK","DE","IT","ES"], "rule": "avg", "discount": 0.10},
    # ... 43 markets total
    "CN": {"basket": [], "rule": "negotiated", "discount": 0.65},
    "IN": {"basket": [], "rule": "negotiated", "discount": 0.85},
}
```

`rule` values: `"avg"` | `"min"` | `"avg_top3"` | `"negotiated"` (CN/IN special case based on US price).

## Function-by-function specification

### F1. `calculate_generous_price(country_prices: dict[str, float]) -> dict | None`

**Reference**: V1.7 lines 367-395 (`calculateGenerousPrice`)
**Purpose**: Compute the Generous Medicaid MFN reference price = 2nd-lowest GDP-PPP-adjusted in MFN-8 basket.

#### Signature

```python
def calculate_generous_price(country_prices: dict[str, float]) -> GenerousResult | None:
    """
    Args:
        country_prices: {country_code: list_price_USD}
    Returns:
        GenerousResult or None if insufficient data
    """
```

#### Output schema

```python
@dataclass
class GenerousResult:
    price: float                           # 2nd-lowest PPP-adjusted price
    country: str                           # Country code that sets the reference
    raw: float                             # Raw nominal price of that country
    all: list[tuple[str, float, float]]   # All basket countries sorted, [(code, ppp_adjusted, nominal)]
```

#### Algorithm

1. Filter `country_prices` to only include keys in `US_MODEL_BASKETS["GENEROUS"]` with non-null values
2. For each country, compute `ppp_adjusted = price * GDP_PPP_ADJUSTERS[country]` (multiply convention)
3. Sort ascending by `ppp_adjusted`
4. Return the **2nd-lowest** (index 1) — that's the Generous reference
5. If fewer than 2 valid prices: return None

#### Example

```python
prices = {"UK": 250000, "FR": 240000, "DE": 280000, "IT": 220000, "CA": 245000, "JP": 260000, "DK": 270000, "CH": 290000}
result = calculate_generous_price(prices)
# result.country = "DK" (2nd lowest after IT)
# result.price ≈ 199612 (depends on exact PPP)
```

### F2. `calculate_guard_method_i(country_prices: dict[str, float]) -> dict | None`

**Reference**: V1.7 lines 397-416 (`calculateGuardMethodI`)
**Purpose**: Compute the GUARD Method I default international benchmark.

#### Signature

```python
def calculate_guard_method_i(country_prices: dict[str, float]) -> MethodIResult | None:
    ...
```

#### Output schema

```python
@dataclass
class MethodIResult:
    price: float          # Lowest PPP-adjusted × 1.02 (the benchmark)
    country: str          # Anchor country code
    raw: float            # Raw PPP-adjusted price (without × 1.02)
    all: list[tuple[str, float]]  # All sorted [(code, ppp_adjusted)]
```

#### Algorithm

1. Filter to OECD-19 basket
2. Compute `ppp_adjusted = price * GDP_PPP_ADJUSTERS[country]`
3. Sort ascending
4. Take the lowest, multiply by 1.02 (CMS adjustment factor for Method I)
5. Return result

**Critical**: The 1.02 multiplier is the CMS-mandated upward adjustment for Method I (102% of lowest). Do not change.

### F3. `calculate_guard_method_ii(net_prices, volumes, year) -> float | None`

**Reference**: V1.7 lines 418-440 (`calculateGuardMethodII`)
**Purpose**: Compute volume-weighted PPP-adjusted average net price × 1.05 × phase-in.

#### Signature

```python
def calculate_guard_method_ii(
    net_prices: dict[str, float],     # {country: net_price_USD}
    volumes: dict[str, float],         # {country: volume_share}
    year: int                          # Performance year
) -> float | None:
    ...
```

#### Algorithm

1. For each country in `US_MODEL_BASKETS["GUARD"]`:
   - Skip if `net_prices[c]` or `volumes[c]` is None or zero
   - Compute `adjusted_price = net_prices[c] * GDP_PPP_ADJUSTERS[c]`
   - Accumulate `weighted_sum += adjusted_price * volumes[c]`
   - Accumulate `total_volume += volumes[c]`
2. If `total_volume == 0`: return None
3. `weighted_avg = weighted_sum / total_volume`
4. `base = weighted_avg * 1.05` (CMS Method II adjustment factor: 105%)
5. `phase_in = GUARD_PHASEIN.get(year, -0.30)` (default to terminal -30%)
6. Return `base * (1 + phase_in)`

**Critical**: Method II applies PPP adjustment **at the country level**, not after weighting. This was a subtle bug in early V1.0 implementations.

**G2N time series compatibility**: The caller is responsible for computing `net_prices[country]` using the G2N resolved for the performance `year`. The signature accepts already-computed net prices to keep the function pure. Caller pattern:

```python
# Caller code (in services/scenario.py)
net_prices = {}
for country, list_price in country_prices.items():
    g2n = resolve_g2n(country, year, scenario_config, country_reference)
    net_prices[country] = list_price * g2n

method_ii_2028 = calculate_guard_method_ii(net_prices, volumes, year=2028)
method_ii_2029 = calculate_guard_method_ii(net_prices_2029, volumes_2029, year=2029)
# Note: each year's Method II uses that year's resolved G2N
```

This means **Method II benchmark may differ year-over-year** even with stable list prices, if `g2n_time_series` defines G2N erosion. This is the intended behavior under time-variant G2N.

### F4. `calculate_globe_method_i(country_prices)` and `calculate_globe_method_ii(net_prices, volumes, year)`

**Reference**: V1.7 lines 442-489

GLOBE Method I has **identical algorithm** to GUARD Method I (same basket, same 1.02 adjustment). Implement as alias or thin wrapper.

GLOBE Method II differs only in phase-in:
- Use `GLOBE_PHASEIN` instead of `GUARD_PHASEIN`
- Otherwise identical logic to F3

### F5. `calculate_guard_rebate(us_net_price, method_i, method_ii, use_method_ii) -> dict`

**Reference**: V1.7 lines 491-499 (`calculateGuardRebate`)
**Purpose**: Compute per-unit rebate based on max(M.I, M.II) vs US net.

#### Signature

```python
def calculate_guard_rebate(
    us_net_price: float,
    method_i: float | None,
    method_ii: float | None,
    use_method_ii: bool                # Whether manufacturer submitted Method II
) -> RebateResult:
    ...
```

#### Output schema

```python
@dataclass
class RebateResult:
    rebate_per_unit: float
    benchmark: float | None
    method_used: str  # "I" or "II"
```

#### Algorithm

1. Start with `benchmark = method_i` (default to Method I)
2. If `use_method_ii` AND `method_ii` is not None:
   - `benchmark = max(method_i, method_ii)`
3. If `benchmark` is None: return `{rebate_per_unit: 0, benchmark: None}`
4. `rebate_per_unit = max(0, us_net_price - benchmark)` (rebate cannot be negative)
5. `method_used = "II" if (use_method_ii and method_ii > method_i) else "I"`

### F6. `calculate_globe_rebate(...)` 

**Reference**: V1.7 lines 502-510

Identical to F5 but for GLOBE benchmarks. Simple aliasing acceptable.

### F7. `apply_country_irp(country, current_prices) -> float | None`

**Reference**: V1.7 lines 587-606 (`applyCountryIRP`)
**Purpose**: Compute new price for a single country based on IRP rule using current prices in basket.

#### Signature

```python
def apply_country_irp(country: str, current_prices: dict[str, float]) -> float | None:
    ...
```

#### Algorithm

1. Look up `IRP_RULES[country]`. If not found: return existing price unchanged.
2. Special case: `rule == "negotiated"` → return `current_prices["US"] * (1 - rule.discount)`. Used for CN, IN.
3. Resolve basket:
   - If `rule.basket == "EU_ALL"`: expand to all EU members except self
   - Otherwise use the country list
4. Filter to countries with non-null prices in `current_prices`
5. If no valid prices: return existing
6. Compute reference price based on `rule.rule`:
   - `"min"`: `min(basket_prices)`
   - `"avg"`: `sum(basket_prices) / len(basket_prices)`
   - `"avg_top3"`: top 3 highest, average them
7. `new_price = ref_price * (1 - rule.discount)`
8. Return `min(current_price, new_price)` — IRP can only **lower** the price (price discipline rule)

### F8. `run_cascade(initial_prices, max_iterations=5, options={}) -> dict`

**Reference**: V1.7 lines 608-628 (`runCascade`)
**Purpose**: Iteratively apply IRP rules across all countries until convergence.

#### Signature

```python
def run_cascade(
    initial_prices: dict[str, float],
    max_iterations: int = 5,
    options: dict = {"enabled": True}
) -> CascadeResult:
    ...
```

#### Output schema

```python
@dataclass
class CascadeResult:
    final: dict[str, float]              # Final converged prices
    iterations: int                       # Iterations actually run
    history: list[dict[str, float]]      # Snapshot per iteration
```

#### Algorithm

1. If `options.enabled == False`: return `{final: initial_prices, iterations: 0, history: [initial_prices]}`
2. `current = deep copy of initial_prices`
3. For iteration in 1..max_iterations:
   - `next = deep copy of current`
   - For each country in IRP_RULES (NOT "US" — US price is exogenous):
     - If country has initial price (was launched): `next[country] = apply_country_irp(country, current)`
   - Check convergence: `all(abs(next[c] - current[c]) < 0.01 for c in next)`
   - Update `current = next`
   - Append to history
   - If converged: break
4. Return result

**Performance budget**: 43 countries × 5 iterations = 215 IRP applications. Must complete in < 200ms.

### F9. `project_volume(base_volume, year, launch_year, peak_year, loe_year) -> float`

**Reference**: V1.7 lines 630-644 (`projectVolume`)
**Purpose**: Project volume for a given year based on lifecycle.

#### Algorithm

```python
def project_volume(base_volume, year, launch_year, peak_year, loe_year):
    if year < launch_year:
        return 0
    if year < peak_year:
        # Linear ramp from 0 to base_volume
        return base_volume * (year - launch_year + 1) / (peak_year - launch_year + 1)
    if year < loe_year:
        return base_volume  # Plateau at peak
    if year >= loe_year + 5:
        return base_volume * 0.10  # Long tail at 10%
    # Post-LOE erosion: 20% per year
    return base_volume * (1 - 0.20 * (year - loe_year))
```

The V1.7 prototype uses an S-curve ramp (sigmoid). For v2.0, **simplify to linear ramp** as shown above (matches our test fixtures and is more predictable).

### F10. `compute_npv(country_prices, scenario_config, asset_config) -> dict`

**Reference**: V1.7 has this distributed across multiple useMemo hooks
**Purpose**: Compute total NPV over launch-to-LOE horizon.

#### Algorithm

1. For year in `launch_year` to `launch_year + 14`:
   - Compute US revenue: `us_volume * us_net_price` (US G2N already baked into `us_net_price`)
   - For each ex-US country with launched price:
     - `country_volume = project_volume(...) * ex_us_total * country_share`
     - `g2n_for_year = resolve_g2n(country, year, scenario_config)` ← see helper below
     - `revenue += country_volume * list_price * g2n_for_year`
   - `discount_factor = (1 + WACC) ^ (year - launch_year)`
   - `discounted_revenue = revenue / discount_factor`
   - Sum into NPV
2. Track peak revenue (max year revenue without discount)
3. Return `{npv, peak_revenue, yearly_breakdown}` where `yearly_breakdown` includes per-country `g2n_used` for audit traceability

#### Helper: `resolve_g2n(country, year, scenario_config) -> float`

Implements the fallback chain documented in `03_DATA_MODEL.md` "G2N Time Series resolution":

```python
def resolve_g2n(country: str, year: int, scenario_config: dict, country_reference: dict) -> float:
    """
    Resolve the G2N for (country, year) following the fallback chain:
    1. country_data.g2n_time_series[year]   if present
    2. country_data.g2n_ratio                if not null
    3. country_reference.default_g2n_ratio   fallback
    
    Returns: float in (0, 1]
    Raises: ValueError if no value can be resolved (country not in reference)
    """
    cd = scenario_config["country_data"].get(country, {})
    
    # Step 1: time series lookup
    ts = cd.get("g2n_time_series")
    if ts is not None:
        # Special case: single-entry time series replicates across all years
        if len(ts) == 1:
            return float(next(iter(ts.values())))
        # Multi-entry: lookup specific year
        if str(year) in ts:
            return float(ts[str(year)])
        # Year not in series: fall through to step 2
    
    # Step 2: per-country static override
    if cd.get("g2n_ratio") is not None:
        return float(cd["g2n_ratio"])
    
    # Step 3: country reference default
    if country in country_reference:
        return float(country_reference[country]["default_g2n_ratio"])
    
    raise ValueError(f"Cannot resolve G2N for {country} year {year}: not in country_reference")
```

**Critical**: The resolution must be deterministic. Same (country, year, scenario) input → same G2N output across the entire NPV calculation.

**Audit trail**: Every NPV result must include the `g2n_used` per (country, year) tuple in `yearly_breakdown` so auditors can verify which G2N was applied. This is required for SOX 404 defensibility.

### F11. `analyze_mfn_anchor(prices, model='GUARD') -> dict`

**Reference**: V1.7 lines 663-718 (`analyzeMFNAnchor`)
**Purpose**: Identify Method I anchor + ringfencing recommendations.

See V1.7 reference for full output structure. Key outputs:

```python
@dataclass
class AnchorAnalysis:
    model: str                          # 'GUARD' | 'GENEROUS' | 'GLOBE'
    anchor: dict                        # {country, countryName, nominal, ppp, adjusted}
    second: dict                        # 2nd anchor candidate
    benchmark: float                    # anchor.adjusted * 1.02
    anchor_gap: float
    anchor_gap_pct: float
    is_non_obvious_anchor: bool         # True if anchor != lowest nominal
    nominal_lowest: dict
    ringfence_recommendation: str       # Pre-formatted English string
    all_ranked: list[dict]
```

### F12. `simulate_de_cascade(current_prices, opt_in_rebate_pct=0.09) -> dict`

**Reference**: V1.7 lines 720-770 (`simulateDECascade`)
**Purpose**: Quantify the impact of Germany's confidential pricing opt-in.

#### Algorithm

1. If no German price: return error
2. `de_after = de_before * (1 - opt_in_rebate_pct)`
3. Build adjusted_prices with new DE
4. Run full cascade
5. For each market in `DE_REFERENCING_MARKETS` (27 hardcoded countries):
   - Compute price delta (before vs after)
6. Return aggregated impact

`DE_REFERENCING_MARKETS` is a hardcoded list of 27 markets (V1.7 lines 723-727). This list should be **derived from IRP_RULES** in v2.0 (any country whose basket contains "DE") rather than hardcoded — keeps it in sync with rule updates.

### F13. `monte_carlo_g2n(base_prices, base_g2n, year, model, n=500, sigma=0.05) -> dict`

**Reference**: V1.7 lines 870-906 (`monteCarloG2N`)
**Purpose**: Monte Carlo confidence intervals on Method II benchmark.

#### Algorithm

1. For i in 1..N:
   - For each country, sample G2N from normal distribution centered on base_g2n[c] with sigma
   - Clip to [0.30, 1.0]
   - Compute perturbed Method II
2. Sort N samples
3. Compute mean, P05, P50, P95
4. Return statistics

**Performance**: N=500 typical, complete in < 5 seconds. Run async if N > 100.

### F14. `generate_audit_json(asset, scenario, prices, regulations, npv_result, anchor_analysis) -> dict`

**Reference**: V1.7 lines 772-845 (`generateAuditJSON`)
**Purpose**: SOX-grade audit document for a pricing decision.

#### Output structure

See V1.7 reference for complete schema. Key sections:

- `metadata`: tool version, timestamp, user, classification
- `asset`: full asset config
- `methodology`: regulation rules with CMS citations
- `pppAdjusters`: full adjuster table snapshot
- `inputs`: all prices and regulation toggles
- `calculations`: anchor analysis, NPV
- `auditTrail`: 6-step methodology trail
- `disclaimer`: standard CMS proposed-rule basis

Generated JSON should be valid, self-contained (no external references), and human-readable when pretty-printed.

## Cross-cutting requirements

### Error handling

All functions must:

- Accept None / missing data gracefully (return None, not raise)
- Validate inputs at function entry (raise `ValidationError` on type errors)
- Log warnings for unusual inputs (e.g., negative prices, PPP < 1.0) — do not silently correct

### Determinism

All functions except `monte_carlo_g2n` must be **deterministic**. Same inputs → same outputs, every time. No timestamps in output, no random seeds.

For Monte Carlo, accept an optional `seed` parameter for reproducibility:

```python
def monte_carlo_g2n(..., seed: int | None = None) -> dict:
    rng = random.Random(seed) if seed else random.Random()
    ...
```

### Versioning

The engine is versioned independently from the platform:
- Engine v1.7.0 = matches V1.7 jsx reference
- Engine v1.7.1+ = bug fixes only, no behavior changes
- Engine v1.8.0+ = new functions added (e.g., GR clawback, BR CMED), existing functions unchanged

Output of `compute_simulation` includes `engine_version` for traceability.

### Performance

| Function | Budget | Notes |
|----------|--------|-------|
| F1-F6 (basic calcs) | < 5ms | Pure arithmetic |
| F7 (apply_country_irp) | < 5ms | Per call |
| F8 (run_cascade) | < 200ms | 43 countries × 5 iterations |
| F9 (project_volume) | < 1ms | Trivial |
| F10 (compute_npv) | < 500ms | 14-year loop × 43 countries |
| F11 (analyze_mfn_anchor) | < 50ms | Sort + compute |
| F12 (simulate_de_cascade) | < 300ms | Includes cascade re-run |
| F13 (monte_carlo_g2n) | < 5s for N=500 | Async if larger |
| F14 (generate_audit_json) | < 100ms | Just data assembly |

Profile and optimize if any function exceeds budget by >2×.

### Test fixtures

Every function must have unit tests using fixtures from `10_TEST_FIXTURES.md`. Integration tests must validate the full pipeline against the two reference scenarios:

- VX-CFTR-NG (orphan premium): Full MFN NPV must equal $46.74B (±$10M tolerance)
- ONC-mAb-001 (oncology biologic): Full MFN NPV must equal $4.96B (±$5M tolerance)

If integration tests fail, **deployment must be blocked**.

---

*Next: read `05_API_CONTRACTS.md`*
