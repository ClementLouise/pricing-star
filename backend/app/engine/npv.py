"""
F9-F10: Volume projection and NPV computation.
resolve_g2n helper implements the 3-step fallback chain for SOX-defensible audit.
"""

import logging
from typing import Optional

from .types import AssetConfig, ScenarioConfig, CountryData, NPVResult, YearlyBreakdown

logger = logging.getLogger(__name__)

_DEFAULT_G2N_FALLBACK = 0.80


def project_volume(
    base_volume: float,
    year: int,
    launch_year: int,
    peak_year: int,
    loe_year: int,
) -> float:
    """
    F9: Linear ramp from 0 to base_volume, plateau at peak, post-LOE erosion.
    Uses linear ramp (not S-curve) per PRD §04 specification.
    """
    if year < launch_year:
        return 0.0
    if year < peak_year:
        return base_volume * (year - launch_year + 1) / (peak_year - launch_year + 1)
    if year < loe_year:
        return base_volume
    if year >= loe_year + 5:
        return base_volume * 0.10
    return base_volume * (1.0 - 0.20 * (year - loe_year))


def resolve_g2n(
    country: str,
    year: int,
    scenario_config: ScenarioConfig,
    country_reference: dict[str, dict],
) -> float:
    """
    Resolve G2N for (country, year) using the 3-step fallback chain.

    1. scenario_config.country_data[country].g2n_time_series[year]  — if present
    2. scenario_config.country_data[country].g2n_ratio               — if not null
    3. country_reference[country]["default_g2n_ratio"]               — fallback

    Raises ValueError if no value can be resolved.
    """
    cd: CountryData = scenario_config.country_data.get(country, CountryData())

    # Step 1: time series lookup
    if cd.g2n_time_series is not None:
        if len(cd.g2n_time_series) == 1:
            return float(next(iter(cd.g2n_time_series.values())))
        year_key = str(year)
        if year_key in cd.g2n_time_series:
            return float(cd.g2n_time_series[year_key])

    # Step 2: per-country static override
    if cd.g2n_ratio is not None:
        return float(cd.g2n_ratio)

    # Step 3: country reference default
    ref = country_reference.get(country, {})
    if "default_g2n_ratio" in ref:
        return float(ref["default_g2n_ratio"])

    raise ValueError(f"Cannot resolve G2N for {country} year {year}: not in country_reference")


def compute_npv(
    country_prices: dict[str, float],
    asset_config: AssetConfig,
    scenario_config: ScenarioConfig,
    country_reference: Optional[dict[str, dict]] = None,
    us_net_override: Optional[float] = None,
    us_net_schedule: Optional[dict[int, float]] = None,
) -> NPVResult:
    """
    F10: Compute total NPV over the asset lifecycle horizon.

    us_net_schedule: year → effective_us_net mapping (EC-CALC-17 time-variant rebate).
                     Takes precedence over us_net_override when provided.
    us_net_override: single effective_us_net applied to all years (deprecated in favour of
                     us_net_schedule; kept for backward compatibility with callers that
                     pre-compute a single rebate).

    Horizon = min(patent_expiry - launch_year + 1, 15) years, matching V2.0 reference.
    """
    if country_reference is None:
        country_reference = {}

    launch = asset_config.launch_year
    peak = launch + asset_config.ramp_years
    loe = asset_config.patent_expiry
    rate = asset_config.discount_rate

    horizon = min(loe - launch + 1, 15)

    us_base_volume = (
        asset_config.us_patient_population * asset_config.patient_capture_rate_at_peak
    )
    total_ex_us = (
        asset_config.ex_us_patient_population * asset_config.patient_capture_rate_at_peak
    )
    us_net_default = asset_config.us_list_price * asset_config.us_net_share

    npv = 0.0
    peak_revenue = 0.0
    yearly_breakdown: list[YearlyBreakdown] = []

    for year in range(launch, launch + horizon):
        # Resolve effective US net for this year (schedule > override > default)
        if us_net_schedule is not None:
            us_net = us_net_schedule.get(year, us_net_default)
        elif us_net_override is not None:
            us_net = us_net_override
        else:
            us_net = us_net_default

        rebate_this_year = us_net_default - us_net  # 0 when no rebate applies

        us_vol = project_volume(us_base_volume, year, launch, peak, loe)
        us_rev = us_vol * us_net

        ex_us_rev = 0.0
        g2n_used: dict[str, float] = {}

        for country, cd in scenario_config.country_data.items():
            lp = country_prices.get(country)
            if lp is None or lp <= 0:
                continue
            if cd.volume_share <= 0:
                continue

            cv = project_volume(total_ex_us * cd.volume_share, year, launch, peak, loe)
            if cv <= 0:
                continue

            try:
                g2n = resolve_g2n(country, year, scenario_config, country_reference)
            except ValueError:
                g2n = _DEFAULT_G2N_FALLBACK
                logger.warning("resolve_g2n fallback for %s year %d: using %.2f", country, year, g2n)

            g2n_used[country] = g2n
            ex_us_rev += cv * lp * g2n

        total_rev = us_rev + ex_us_rev
        discount_factor = (1 + rate) ** (year - launch)
        npv += total_rev / discount_factor

        if year == peak:
            peak_revenue = total_rev

        yearly_breakdown.append(
            YearlyBreakdown(
                year=year,
                us_revenue=us_rev,
                ex_us_revenue=ex_us_rev,
                total_revenue=total_rev,
                g2n_used=g2n_used,
                rebate_per_unit=rebate_this_year,
                effective_us_net=us_net,
            )
        )

    return NPVResult(npv=npv, peak_revenue=peak_revenue, yearly_breakdown=yearly_breakdown)
