"""Dataclasses for all engine function inputs and outputs."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GenerousResult:
    price: float                              # 2nd-lowest PPP-adjusted price
    country: str                              # Country setting the reference
    raw: float                                # Nominal (non-PPP) price of that country
    all: list[tuple[str, float, float]]       # [(code, ppp_adjusted, nominal)] sorted asc


@dataclass
class MethodIResult:
    price: float                              # lowest_ppp × 1.02
    country: str                              # Anchor country code
    raw: float                                # lowest_ppp (without ×1.02)
    all: list[tuple[str, float]]              # [(code, ppp_adjusted)] sorted asc


@dataclass
class RebateResult:
    rebate_per_unit: float
    benchmark: Optional[float]
    method_used: str                          # "I" or "II"


@dataclass
class CascadeResult:
    final: dict[str, float]                   # Final converged prices
    iterations: int                           # Iterations actually run
    history: list[dict[str, float]]           # Price snapshot per iteration
    converged: bool = True                    # False if max_iterations reached without convergence


@dataclass
class CountryData:
    """Per-country scenario data used in NPV computation."""
    volume_share: float = 0.0                 # Fraction of total ex-US patient population
    g2n_ratio: Optional[float] = None        # Static G2N override (0 < g2n ≤ 1)
    g2n_time_series: Optional[dict[str, float]] = None  # year_str → g2n


@dataclass
class ScenarioConfig:
    """Configuration for a simulation scenario."""
    country_data: dict[str, CountryData] = field(default_factory=dict)


@dataclass
class AssetConfig:
    """Asset-level configuration for NPV computation."""
    name: str
    us_list_price: float
    us_net_share: float
    launch_year: int
    patent_expiry: int
    us_patient_population: int
    ex_us_patient_population: int
    patient_capture_rate_at_peak: float
    ramp_years: int
    discount_rate: float
    part_b_share: float = 0.0               # Fraction of US revenue subject to Globe (Part B)


@dataclass
class YearlyBreakdown:
    year: int
    us_revenue: float
    ex_us_revenue: float
    total_revenue: float
    g2n_used: dict[str, float]              # country → g2n applied (for SOX audit trail)
    rebate_per_unit: float = 0.0            # MFN rebate applied this year (0 if no regulation)
    effective_us_net: float = 0.0           # us_net - rebate_per_unit (SOX audit trail)


@dataclass
class NPVResult:
    npv: float
    peak_revenue: float
    yearly_breakdown: list[YearlyBreakdown]


@dataclass
class AnchorCountry:
    country: str
    country_name: str
    nominal: float
    ppp: float
    adjusted: float                          # nominal × ppp


@dataclass
class AnchorAnalysis:
    model: str                               # "GUARD" | "GENEROUS" | "GLOBE"
    anchor: AnchorCountry
    second: AnchorCountry
    benchmark: float                         # anchor.adjusted × 1.02
    anchor_gap: float                        # second.adjusted - anchor.adjusted
    anchor_gap_pct: float                    # anchor_gap / anchor.adjusted
    is_non_obvious_anchor: bool              # True if anchor ≠ nominal-lowest
    nominal_lowest: AnchorCountry
    ringfence_recommendation: str
    all_ranked: list[AnchorCountry]          # All basket countries, sorted asc by adjusted


@dataclass
class MarketImpact:
    country: str
    country_name: str
    before: float
    after: float
    delta: float
    delta_pct: float


@dataclass
class DECascadeResult:
    opt_in_rebate_pct: float
    de_price_before: float
    de_price_after: float
    de_disclosed_delta: float
    market_impacts: list[MarketImpact]       # Only markets with |delta_pct| > 0.001
    referencing_markets_count: int
    actually_impacted_count: int
    cascade_iterations: int


@dataclass
class MonteCarloResult:
    samples_n: int
    mean: float
    p05: float
    p50: float
    p95: float
    range: float                             # p95 - p05
    sigma_input: float
