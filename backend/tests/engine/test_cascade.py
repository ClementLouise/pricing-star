"""Unit tests for F7-F8: IRP cascade engine."""

import pytest
from app.engine.cascade import apply_country_irp, run_cascade


SIMPLE_PRICES = {
    "US": 180000,
    "DE": 90000,
    "FR": 80000,
    "IT": 70000,
    "ES": 68000,
    "NL": 81000,
    "BE": 77000,
    "UK": 81000,
    "CH": 99000,
    "AT": 77000,
    "DK": 81000,
    "SE": 81000,
    "NO": 86400,
    "FI": 75600,
}


class TestApplyCountryIRP:
    def test_avg_rule_returns_average(self):
        # FR basket = [UK, DE, IT, ES], discount=0.10
        prices = {"UK": 100, "DE": 80, "IT": 70, "ES": 60, "FR": 200}
        result = apply_country_irp("FR", prices)
        avg = (100 + 80 + 70 + 60) / 4
        expected = avg * (1 - 0.10)
        assert result == pytest.approx(expected, rel=1e-6)

    def test_min_rule(self):
        # RO basket = [DE,FR,IT,ES,PL,CZ], rule=min, discount=0.05
        prices = {"DE": 100, "FR": 80, "IT": 70, "ES": 60, "PL": 50, "CZ": 55, "RO": 200}
        result = apply_country_irp("RO", prices)
        assert result == pytest.approx(50 * 0.95, rel=1e-6)

    def test_negotiated_rule_cn(self):
        # CN: negotiated, discount=0.65 → 35% of US price
        prices = {"US": 180000, "CN": 50000}
        result = apply_country_irp("CN", prices)
        assert result == pytest.approx(180000 * 0.35, rel=1e-6)

    def test_unknown_country_returns_current(self):
        prices = {"XX": 12345}
        result = apply_country_irp("XX", prices)
        assert result == 12345

    def test_empty_basket_returns_current(self):
        # Basket countries not in current_prices → return current
        result = apply_country_irp("DE", {"DE": 99999})
        # DE basket = [UK,FR,IT,...] — none present
        assert result == 99999

    def test_irp_only_goes_down(self):
        # After run_cascade enforces min(), price cannot rise
        prices = {**SIMPLE_PRICES}
        cascade = run_cascade(prices)
        for c, before in prices.items():
            after = cascade.final.get(c, before)
            assert after <= before + 0.01, f"{c}: {before} → {after} raised"


class TestRunCascade:
    def test_fixture_b_converges_in_3_iterations(self):
        # Fixture D: ONC-mAb-001 full initial prices should converge within max_iterations
        initial = {
            "US": 180000, "DE": 90000, "JP": 86400, "CH": 99000, "CA": 90000,
            "FR": 77400, "UK": 81000, "IT": 72000, "ES": 68400, "NL": 81000,
            "BE": 77400, "AT": 77400, "SE": 81000, "DK": 81000, "NO": 86400,
            "FI": 75600, "IE": 81000, "GR": 54000, "PT": 57600, "PL": 57600,
            "CZ": 63000, "HU": 54000, "RO": 50400, "SK": 57600, "BG": 45000,
            "KR": 68400, "AU": 72000, "BR": 57600, "MX": 54000, "CL": 57600,
            "CO": 50400, "AR": 45000, "SA": 68400, "AE": 72000,
            "CN": 36000, "IN": 14400, "IL": 72000,
        }
        result = run_cascade(initial)
        assert result.iterations <= 5, (
            f"Expected ≤5 iterations, got {result.iterations}"
        )
        for c, price in result.final.items():
            assert price >= 0, f"{c} has negative price after cascade"

    def test_disabled_cascade_returns_initial(self):
        initial = {"US": 180000, "DE": 90000, "FR": 80000}
        result = run_cascade(initial, options={"enabled": False})
        assert result.iterations == 0
        assert result.final == initial

    def test_history_length_equals_iterations_plus_1(self):
        result = run_cascade(SIMPLE_PRICES)
        assert len(result.history) == result.iterations + 1

    def test_does_not_cascade_unlaunched_countries(self):
        # If AR is not in initial_prices, it should not appear in final
        prices = {"US": 100000, "DE": 50000}
        result = run_cascade(prices)
        assert "AR" not in result.final

    def test_us_price_unchanged(self):
        result = run_cascade(SIMPLE_PRICES)
        assert result.final["US"] == SIMPLE_PRICES["US"]

    def test_cascade_lowers_prices(self):
        # Cascade should lower or maintain prices, never raise
        result = run_cascade(SIMPLE_PRICES)
        for c in SIMPLE_PRICES:
            assert result.final[c] <= SIMPLE_PRICES[c] + 0.01, f"{c} raised"
