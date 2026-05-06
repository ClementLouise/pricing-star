"""F11: MFN anchor analysis — identifies Method I anchor with ringfencing recommendations."""

import logging
from typing import Optional

from .constants import GDP_PPP_ADJUSTERS, US_MODEL_BASKETS, COUNTRY_NAMES
from .types import AnchorAnalysis, AnchorCountry

logger = logging.getLogger(__name__)


def analyze_mfn_anchor(
    prices: dict[str, float],
    model: str = "GUARD",
) -> Optional[AnchorAnalysis]:
    """
    F11: Identify the Method I anchor country and produce ringfencing recommendations.

    Returns None if the basket has no valid prices.
    """
    basket = US_MODEL_BASKETS.get(model)
    if basket is None:
        logger.error("analyze_mfn_anchor: unknown model '%s'", model)
        return None

    ranked: list[AnchorCountry] = []
    for c in basket:
        price = prices.get(c)
        if price is None or price <= 0:
            continue
        ppp = GDP_PPP_ADJUSTERS.get(c, 1.0)
        ranked.append(
            AnchorCountry(
                country=c,
                country_name=COUNTRY_NAMES.get(c, c),
                nominal=price,
                ppp=ppp,
                adjusted=price * ppp,
            )
        )

    if not ranked:
        return None

    ranked.sort(key=lambda x: x.adjusted)

    anchor = ranked[0]
    second = ranked[1] if len(ranked) > 1 else ranked[0]
    benchmark = anchor.adjusted * 1.02

    anchor_gap = second.adjusted - anchor.adjusted
    anchor_gap_pct = anchor_gap / anchor.adjusted if anchor.adjusted > 0 else 0.0

    nominal_sorted = sorted(ranked, key=lambda x: x.nominal)
    nominal_lowest = nominal_sorted[0]
    is_non_obvious = anchor.country != nominal_lowest.country

    recommendation = _ringfence_recommendation(anchor, second, anchor_gap_pct)

    return AnchorAnalysis(
        model=model,
        anchor=anchor,
        second=second,
        benchmark=benchmark,
        anchor_gap=anchor_gap,
        anchor_gap_pct=anchor_gap_pct,
        is_non_obvious_anchor=is_non_obvious,
        nominal_lowest=nominal_lowest,
        ringfence_recommendation=recommendation,
        all_ranked=ranked,
    )


def _ringfence_recommendation(anchor: AnchorCountry, second: AnchorCountry, gap_pct: float) -> str:
    gap_str = f"{gap_pct * 100:.1f}%"
    if gap_pct < 0.05:
        return (
            f"{anchor.country} anchor is fragile — {second.country} is within 5%. "
            f"Small price changes in either could shift the anchor."
        )
    if gap_pct < 0.15:
        return (
            f"{anchor.country} is the binding constraint with {gap_str} gap to {second.country}. "
            f"Price discipline in {anchor.country} directly impacts US Method I."
        )
    return (
        f"{anchor.country} firmly anchors Method I ({gap_str} gap to next country). "
        f"Highest-leverage market for US rebate negotiations."
    )
