"""Real data heuristic for trial mode (EC-TRIAL-01).

Detects whether asset + country data looks like real pharma pricing
data vs illustrative/demo data. Non-blocking — triggers a soft warning.
"""
from dataclasses import dataclass, field

_OECD19 = frozenset({
    "AT", "AU", "BE", "CA", "CH", "CZ", "DE", "DK", "ES", "FI", "FR",
    "IE", "IL", "IT", "JP", "KR", "NL", "NO", "PT", "SE", "UK",
})

_GENERIC_AREAS = frozenset({"test", "demo", "sample", "example", "training"})


@dataclass
class HeuristicResult:
    triggered: bool
    score: int
    breakdown: dict[str, bool] = field(default_factory=dict)


def check_real_data_heuristic(asset: object, country_data: list) -> HeuristicResult:
    """Return HeuristicResult for whether asset+country data looks like real pharma pricing.

    Triggers when >= 2 of 4 criteria are met.
    See docs/PRD_v2/12_EDGE_CASES.md EC-TRIAL-01.
    """
    if asset is None:
        return HeuristicResult(triggered=False, score=0)

    score = 0
    breakdown: dict[str, bool] = {}

    price_raw = getattr(asset, "us_list_price", None)
    price = float(price_raw) if price_raw is not None else None

    # Criterion 1: list price above premium drug threshold
    c1 = price is not None and price > 100_000
    breakdown["high_list_price"] = c1
    if c1:
        score += 1

    # Criterion 2: "marketing" round number (×1000 or ends in 99/95/90)
    c2 = False
    if price is not None:
        price_int = int(price)
        c2 = price_int % 1_000 == 0 or str(price_int).endswith(("99", "95", "90"))
    breakdown["marketing_round_number"] = c2
    if c2:
        score += 1

    # Criterion 3: >= 5 OECD-19 markets with launched data
    launched_oecd = sum(
        1 for cd in country_data
        if getattr(cd, "launched", False) and getattr(cd, "country_code", "") in _OECD19
    )
    c3 = launched_oecd >= 5
    breakdown["oecd_markets_5plus"] = c3
    if c3:
        score += 1

    # Criterion 4: non-null, non-generic therapeutic area
    ta = getattr(asset, "therapeutic_area", None)
    c4 = bool(ta and ta.strip().lower() not in _GENERIC_AREAS)
    breakdown["real_therapeutic_area"] = c4
    if c4:
        score += 1

    return HeuristicResult(triggered=score >= 2, score=score, breakdown=breakdown)
