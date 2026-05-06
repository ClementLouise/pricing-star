"""
F1-F6: MFN benchmark calculation functions.
Pure functions — no side effects, fully deterministic.
"""

import logging
from typing import Optional

from .constants import GDP_PPP_ADJUSTERS, US_MODEL_BASKETS, GUARD_PHASEIN, GLOBE_PHASEIN
from .types import GenerousResult, MethodIResult, RebateResult

logger = logging.getLogger(__name__)


def calculate_generous_price(country_prices: dict[str, float]) -> Optional[GenerousResult]:
    """F1: Generous Medicaid MFN = 2nd-lowest GDP-PPP-adjusted price in MFN-8 basket."""
    basket = US_MODEL_BASKETS["GENEROUS"]
    adjusted: list[tuple[str, float, float]] = []

    for c in basket:
        price = country_prices.get(c)
        if price is None or price <= 0:
            continue
        ppp = GDP_PPP_ADJUSTERS.get(c, 1.0)
        adjusted.append((c, price * ppp, price))

    if len(adjusted) < 2:
        logger.warning("calculate_generous_price: fewer than 2 valid basket prices")
        return None

    adjusted.sort(key=lambda x: x[1])
    _, ppp_adj, nominal = adjusted[1]
    return GenerousResult(price=ppp_adj, country=adjusted[1][0], raw=nominal, all=adjusted)


def calculate_guard_method_i(country_prices: dict[str, float]) -> Optional[MethodIResult]:
    """F2: GUARD Method I = lowest GDP-PPP-adjusted in OECD-19 × 1.02."""
    return _method_i(country_prices, "GUARD")


def calculate_globe_method_i(country_prices: dict[str, float]) -> Optional[MethodIResult]:
    """F4a: GLOBE Method I — identical algorithm to GUARD Method I (same basket)."""
    return _method_i(country_prices, "GLOBE")


def _method_i(country_prices: dict[str, float], model: str) -> Optional[MethodIResult]:
    basket = US_MODEL_BASKETS[model]
    adjusted: list[tuple[str, float]] = []

    for c in basket:
        price = country_prices.get(c)
        if price is None or price <= 0:
            continue
        ppp = GDP_PPP_ADJUSTERS.get(c, 1.0)
        adjusted.append((c, price * ppp))

    if not adjusted:
        logger.warning("_method_i: no valid basket prices for model=%s", model)
        return None

    adjusted.sort(key=lambda x: x[1])
    anchor_code, anchor_ppp = adjusted[0]
    return MethodIResult(
        price=anchor_ppp * 1.02,
        country=anchor_code,
        raw=anchor_ppp,
        all=adjusted,
    )


def calculate_guard_method_ii(
    net_prices: dict[str, float],
    volumes: dict[str, float],
    year: int,
) -> Optional[float]:
    """F3: GUARD Method II = volume-weighted avg PPP-adjusted net price × 1.05 × phase-in."""
    return _method_ii(net_prices, volumes, year, "GUARD", GUARD_PHASEIN)


def calculate_globe_method_ii(
    net_prices: dict[str, float],
    volumes: dict[str, float],
    year: int,
) -> Optional[float]:
    """F4b: GLOBE Method II — same as GUARD but with GLOBE phase-in schedule."""
    return _method_ii(net_prices, volumes, year, "GLOBE", GLOBE_PHASEIN)


def _method_ii(
    net_prices: dict[str, float],
    volumes: dict[str, float],
    year: int,
    model: str,
    phasein: dict[int, float],
) -> Optional[float]:
    basket = US_MODEL_BASKETS[model]
    weighted_sum = 0.0
    total_volume = 0.0

    for c in basket:
        net = net_prices.get(c)
        vol = volumes.get(c)
        if net is None or vol is None or net <= 0 or vol <= 0:
            continue
        ppp = GDP_PPP_ADJUSTERS.get(c, 1.0)
        # PPP adjustment applied at country level before weighting (critical: not post-weighting)
        weighted_sum += (net * ppp) * vol
        total_volume += vol

    if total_volume == 0:
        return None

    weighted_avg = weighted_sum / total_volume
    base = weighted_avg * 1.05
    phase_in = phasein.get(year, -0.30)
    return base * (1 + phase_in)


def calculate_guard_rebate(
    us_net_price: float,
    method_i: Optional[float],
    method_ii: Optional[float],
    use_method_ii: bool,
) -> RebateResult:
    """F5: GUARD per-unit rebate = max(0, US net - applicable benchmark)."""
    return _rebate(us_net_price, method_i, method_ii, use_method_ii)


def calculate_globe_rebate(
    us_net_price: float,
    method_i: Optional[float],
    method_ii: Optional[float],
    use_method_ii: bool,
) -> RebateResult:
    """F6: GLOBE rebate — identical structure to GUARD rebate."""
    return _rebate(us_net_price, method_i, method_ii, use_method_ii)


def _rebate(
    us_net_price: float,
    method_i: Optional[float],
    method_ii: Optional[float],
    use_method_ii: bool,
) -> RebateResult:
    benchmark = method_i
    if use_method_ii and method_ii is not None and method_i is not None:
        benchmark = max(method_i, method_ii)
    elif use_method_ii and method_ii is not None and method_i is None:
        benchmark = method_ii

    if benchmark is None:
        return RebateResult(rebate_per_unit=0.0, benchmark=None, method_used="I")

    rebate_per_unit = max(0.0, us_net_price - benchmark)
    method_used = (
        "II"
        if use_method_ii and method_ii is not None and method_i is not None and method_ii > method_i
        else "I"
    )
    return RebateResult(rebate_per_unit=rebate_per_unit, benchmark=benchmark, method_used=method_used)
