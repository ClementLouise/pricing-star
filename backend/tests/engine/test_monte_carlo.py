"""Unit tests for F13: Monte Carlo G2N uncertainty."""

import pytest
from app.engine.monte_carlo import monte_carlo_g2n


BASE_PRICES = {
    "DE": 90000, "FR": 77400, "UK": 81000, "IT": 72000, "ES": 68400,
    "NL": 81000, "BE": 77400, "CH": 99000, "DK": 81000, "SE": 81000,
    "NO": 86400, "AU": 72000, "CA": 90000, "JP": 86400, "KR": 68400,
    "AT": 77400, "IE": 81000, "IL": 72000, "CZ": 63000,
}

BASE_G2N = {c: 0.80 for c in BASE_PRICES}


class TestMonteCarloG2N:
    def test_returns_result_with_n_samples(self):
        result = monte_carlo_g2n(BASE_PRICES, BASE_G2N, year=2028, n=100, seed=42)
        assert result is not None
        assert result.samples_n == 100

    def test_percentile_order(self):
        result = monte_carlo_g2n(BASE_PRICES, BASE_G2N, year=2028, n=200, seed=42)
        assert result is not None
        assert result.p05 <= result.p50 <= result.p95

    def test_range_is_positive(self):
        result = monte_carlo_g2n(BASE_PRICES, BASE_G2N, year=2028, n=200, seed=42)
        assert result is not None
        assert result.range > 0

    def test_seed_produces_deterministic_results(self):
        r1 = monte_carlo_g2n(BASE_PRICES, BASE_G2N, year=2028, n=100, seed=42)
        r2 = monte_carlo_g2n(BASE_PRICES, BASE_G2N, year=2028, n=100, seed=42)
        assert r1 is not None and r2 is not None
        assert r1.mean == pytest.approx(r2.mean, rel=1e-9)
        assert r1.p50 == pytest.approx(r2.p50, rel=1e-9)

    def test_different_seeds_give_different_results(self):
        r1 = monte_carlo_g2n(BASE_PRICES, BASE_G2N, year=2028, n=200, seed=1)
        r2 = monte_carlo_g2n(BASE_PRICES, BASE_G2N, year=2028, n=200, seed=2)
        assert r1 is not None and r2 is not None
        assert r1.mean != pytest.approx(r2.mean, rel=1e-3)

    def test_sigma_reported(self):
        result = monte_carlo_g2n(BASE_PRICES, BASE_G2N, year=2028, n=50, sigma=0.05, seed=42)
        assert result is not None
        assert result.sigma_input == pytest.approx(0.05)

    def test_returns_none_if_empty_prices(self):
        result = monte_carlo_g2n({}, {}, year=2028, n=10)
        assert result is None

    def test_mean_in_plausible_range(self):
        result = monte_carlo_g2n(BASE_PRICES, BASE_G2N, year=2028, n=500, seed=42)
        assert result is not None
        # Mean should be in a plausible range given base prices and G2N ~0.80
        assert 10000 < result.mean < 200000
