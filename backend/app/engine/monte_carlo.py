"""F13: Monte Carlo G2N uncertainty — confidence intervals on Method II benchmark."""

import math
import random
import logging
from typing import Optional

from .methods import calculate_guard_method_ii
from .types import MonteCarloResult

logger = logging.getLogger(__name__)


def monte_carlo_g2n(
    base_prices: dict[str, float],
    base_g2n: dict[str, float],
    year: int,
    model: str = "GUARD",
    n: int = 500,
    sigma: float = 0.05,
    seed: Optional[int] = None,
) -> Optional[MonteCarloResult]:
    """
    F13: Monte Carlo simulation — N samples of perturbed G2N → Method II confidence bands.

    seed: if provided, produces deterministic results (required for fixture tests).
    Clip G2N samples to [0.30, 1.0] to stay within plausible pharmaceutical rebate range.
    """
    rng = random.Random(seed) if seed is not None else random.Random()
    samples: list[float] = []

    for _ in range(n):
        perturbed_net: dict[str, float] = {}
        for country, list_price in base_prices.items():
            if list_price is None or list_price <= 0:
                continue
            base = base_g2n.get(country, 0.80)
            # Box-Muller transform for normal distribution
            u1 = rng.random() or 1e-10  # guard against log(0)
            u2 = rng.random()
            z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            g2n_sample = max(0.30, min(1.0, base + z * sigma))
            perturbed_net[country] = list_price * g2n_sample

        # Use list prices as volumes proxy for method_ii (matches V1.7 reference)
        m2 = calculate_guard_method_ii(perturbed_net, base_prices, year)
        if m2 is not None:
            samples.append(m2)

    if not samples:
        logger.warning("monte_carlo_g2n: no valid samples produced")
        return None

    samples.sort()
    count = len(samples)
    mean = sum(samples) / count
    p05 = samples[int(count * 0.05)]
    p50 = samples[int(count * 0.50)]
    p95 = samples[int(count * 0.95)]

    return MonteCarloResult(
        samples_n=count,
        mean=mean,
        p05=p05,
        p50=p50,
        p95=p95,
        range=p95 - p05,
        sigma_input=sigma,
    )
