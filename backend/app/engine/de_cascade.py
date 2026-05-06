"""F12: DE cascade trap simulator — quantifies Germany confidential opt-in downstream impact."""

import logging

from .constants import DE_REFERENCING_MARKETS, COUNTRY_NAMES
from .cascade import run_cascade
from .types import DECascadeResult, MarketImpact

logger = logging.getLogger(__name__)


def simulate_de_cascade(
    current_prices: dict[str, float],
    opt_in_rebate_pct: float = 0.09,
) -> DECascadeResult | dict:
    """
    F12: Model the downstream cascade when Germany discloses a lower price via opt-in rebate.

    The DE_REFERENCING_MARKETS list is derived from IRP_RULES (any country whose basket
    contains "DE") — not hardcoded — so it stays in sync with rule updates.
    """
    de_price = current_prices.get("DE")
    if not de_price or de_price <= 0:
        return {"error": "No German price set — cannot simulate DE opt-in cascade"}

    de_price_before = de_price
    de_price_after = de_price_before * (1 - opt_in_rebate_pct)

    adjusted_prices = {**current_prices, "DE": de_price_after}
    cascade_result = run_cascade(adjusted_prices)

    impacts: list[MarketImpact] = []
    for country in DE_REFERENCING_MARKETS:
        before = current_prices.get(country)
        if before is None or before <= 0:
            continue
        after = cascade_result.final.get(country, before)
        delta = after - before
        delta_pct = delta / before if before > 0 else 0.0
        if abs(delta_pct) <= 0.001:
            continue
        impacts.append(
            MarketImpact(
                country=country,
                country_name=COUNTRY_NAMES.get(country, country),
                before=before,
                after=after,
                delta=delta,
                delta_pct=delta_pct,
            )
        )

    impacts.sort(key=lambda m: m.delta)

    return DECascadeResult(
        opt_in_rebate_pct=opt_in_rebate_pct,
        de_price_before=de_price_before,
        de_price_after=de_price_after,
        de_disclosed_delta=de_price_after - de_price_before,
        market_impacts=impacts,
        referencing_markets_count=len(DE_REFERENCING_MARKETS),
        actually_impacted_count=len(impacts),
        cascade_iterations=cascade_result.iterations,
    )
