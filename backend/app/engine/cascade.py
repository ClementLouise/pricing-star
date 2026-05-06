"""
F7-F8: IRP cascade engine.
Applies per-country IRP rules iteratively until convergence.
"""

import logging
from typing import Optional

from .constants import IRP_RULES
from .types import CascadeResult

logger = logging.getLogger(__name__)


def apply_country_irp(country: str, current_prices: dict[str, float]) -> Optional[float]:
    """
    F7: Compute new IRP-constrained price for a single country.
    Returns the reference price × (1 - discount), or current price if no rule applies.
    The min(current, new) enforcement is applied in run_cascade — not here.
    """
    rule = IRP_RULES.get(country)
    if rule is None:
        return current_prices.get(country)

    if rule["rule"] == "negotiated":
        # CN/IN: price is a percentage of the US list price
        us_price = current_prices.get("US", 0.0) or 0.0
        return us_price * (1 - rule["discount"])

    basket: list[str] = rule["basket"]
    basket_prices = [
        current_prices[c]
        for c in basket
        if c in current_prices and current_prices[c] is not None and current_prices[c] > 0
    ]

    if not basket_prices:
        return current_prices.get(country)

    if rule["rule"] == "min":
        ref = min(basket_prices)
    elif rule["rule"] == "avg_top3":
        ref = sum(sorted(basket_prices, reverse=True)[:3]) / min(3, len(basket_prices))
    elif rule["rule"] == "avg_lowest_3":
        ref = sum(sorted(basket_prices)[:3]) / min(3, len(basket_prices))
    else:
        # Default: arithmetic average
        ref = sum(basket_prices) / len(basket_prices)

    return ref * (1 - rule["discount"])


def run_cascade(
    initial_prices: dict[str, float],
    max_iterations: int = 5,
    options: Optional[dict] = None,
) -> CascadeResult:
    """
    F8: Iteratively apply IRP rules across all launched countries until convergence.
    Only cascades countries that are present in initial_prices (launched markets).
    """
    if options is None:
        options = {}

    if not options.get("enabled", True):
        return CascadeResult(
            final=dict(initial_prices),
            iterations=0,
            history=[dict(initial_prices)],
        )

    current = dict(initial_prices)
    history: list[dict[str, float]] = [dict(current)]

    iterations_run = 0
    for i in range(max_iterations):
        next_prices = dict(current)

        for country in IRP_RULES:
            if country == "US":
                continue
            # Only cascade countries that are launched (present in initial_prices)
            if country not in initial_prices or initial_prices[country] is None:
                continue

            new_price = apply_country_irp(country, current)
            if new_price is not None:
                current_price = current.get(country, new_price)
                next_prices[country] = min(current_price, new_price)

        # Relative convergence threshold: 0.1% matches Python reference (run_oncmab_test_v20.py)
        max_rel_change = max(
            (abs((next_prices.get(c) or 0.0) - (current.get(c) or 0.0)) / (current.get(c) or 1.0)
             for c in next_prices if (current.get(c) or 0.0) > 0),
            default=0.0,
        )
        converged = max_rel_change < 0.001

        history.append(dict(next_prices))
        current = next_prices
        iterations_run = i + 1

        if converged:
            break

    return CascadeResult(final=current, iterations=iterations_run, history=history)
