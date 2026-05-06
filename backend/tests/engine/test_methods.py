"""Unit tests for F1-F6: MFN benchmark calculation functions."""

import pytest
from app.engine.methods import (
    calculate_generous_price,
    calculate_guard_method_i,
    calculate_guard_method_ii,
    calculate_globe_method_i,
    calculate_globe_method_ii,
    calculate_guard_rebate,
    calculate_globe_rebate,
)


# Fixture A prices — VX-CFTR-NG post-cascade
FIXTURE_A_PRICES = {
    "US": 370000, "CH": 183938, "IE": 220000, "NO": 201383, "DK": 194933,
    "NL": 185060, "BE": 183405, "AT": 184467, "SE": 191069, "FI": 184467,
    "DE": 188777, "FR": 171667, "UK": 176271, "IT": 168590, "ES": 171651,
    "CZ": 168725, "IL": 240000, "KR": 240500, "JP": 237639, "AU": 220000, "CA": 240500,
}


class TestGenerousPrice:
    def test_fixture_a_anchor_country(self):
        result = calculate_generous_price(FIXTURE_A_PRICES)
        assert result is not None
        assert result.country == "DK"

    def test_fixture_a_price(self):
        result = calculate_generous_price(FIXTURE_A_PRICES)
        assert result is not None
        assert abs(result.price - 199612) < 50  # tolerance ±$50

    def test_returns_none_if_fewer_than_2_prices(self):
        result = calculate_generous_price({"UK": 100000})
        assert result is None

    def test_returns_none_if_empty(self):
        assert calculate_generous_price({}) is None

    def test_ignores_zero_prices(self):
        prices = {**FIXTURE_A_PRICES, "DE": 0}
        result = calculate_generous_price(prices)
        assert result is not None  # still ≥2 valid

    def test_all_sorted_ascending(self):
        result = calculate_generous_price(FIXTURE_A_PRICES)
        assert result is not None
        adjusted_values = [x[1] for x in result.all]
        assert adjusted_values == sorted(adjusted_values)


class TestGuardMethodI:
    def test_fixture_a_anchor(self):
        result = calculate_guard_method_i(FIXTURE_A_PRICES)
        assert result is not None
        assert result.country == "CH"

    def test_fixture_a_price(self):
        result = calculate_guard_method_i(FIXTURE_A_PRICES)
        assert result is not None
        assert abs(result.price - 187617) < 50

    def test_price_is_102_percent_of_raw(self):
        result = calculate_guard_method_i(FIXTURE_A_PRICES)
        assert result is not None
        assert abs(result.price - result.raw * 1.02) < 0.01

    def test_returns_none_if_empty(self):
        assert calculate_guard_method_i({}) is None

    def test_globe_and_guard_same_result(self):
        r_guard = calculate_guard_method_i(FIXTURE_A_PRICES)
        r_globe = calculate_globe_method_i(FIXTURE_A_PRICES)
        assert r_guard is not None and r_globe is not None
        assert abs(r_guard.price - r_globe.price) < 0.01


class TestGuardMethodII:
    def test_fixture_a_year_2028(self):
        # net_prices = list_prices × 0.50 (US net share)
        net = {c: p * 0.50 for c, p in FIXTURE_A_PRICES.items()}
        vols = {c: 0.01 for c in FIXTURE_A_PRICES}  # equal weights
        result = calculate_guard_method_ii(net, vols, year=2028)
        assert result is not None
        # Should be a positive number in plausible range
        assert 50000 < result < 300000

    def test_returns_none_if_no_volume(self):
        net = {"DE": 100000}
        vols = {}
        assert calculate_guard_method_ii(net, vols, year=2028) is None

    def test_phase_in_reduces_value(self):
        net = {c: p * 0.80 for c, p in FIXTURE_A_PRICES.items()}
        vols = {c: 0.01 for c in FIXTURE_A_PRICES}
        year_2026 = calculate_guard_method_ii(net, vols, year=2026)  # phase_in = -0.10
        year_2028 = calculate_guard_method_ii(net, vols, year=2028)  # phase_in = -0.30
        assert year_2026 is not None and year_2028 is not None
        assert year_2028 < year_2026  # 2028 has steeper phase-in than 2026

    def test_globe_uses_different_phasein(self):
        net = {c: p * 0.80 for c, p in FIXTURE_A_PRICES.items()}
        vols = {c: 0.01 for c in FIXTURE_A_PRICES}
        guard = calculate_guard_method_ii(net, vols, year=2029)   # -30%
        globe = calculate_globe_method_ii(net, vols, year=2029)   # -35%
        assert guard is not None and globe is not None
        assert globe < guard  # GLOBE has steeper phase-in


class TestRebate:
    def test_fixture_a_no_rebate(self):
        # Orphan premium: Method I (187617) > US net (185000) → rebate = 0
        result = calculate_guard_rebate(
            us_net_price=185000,
            method_i=187617,
            method_ii=156799,
            use_method_ii=False,
        )
        assert result.rebate_per_unit == 0
        assert result.benchmark == pytest.approx(187617, abs=1)
        assert result.method_used == "I"

    def test_fixture_b_rebate_33610(self):
        # Oncology biologic: rebate = max(0, 90000 - 56390) = 33610
        result = calculate_guard_rebate(
            us_net_price=90000,
            method_i=56390,
            method_ii=50423,
            use_method_ii=False,
        )
        assert result.rebate_per_unit == pytest.approx(33610, abs=1)
        assert result.method_used == "I"

    def test_use_method_ii_picks_higher(self):
        result = calculate_guard_rebate(
            us_net_price=200000,
            method_i=100000,
            method_ii=120000,
            use_method_ii=True,
        )
        assert result.benchmark == pytest.approx(120000)
        assert result.method_used == "II"

    def test_rebate_cannot_be_negative(self):
        result = calculate_guard_rebate(
            us_net_price=50000,
            method_i=80000,
            method_ii=None,
            use_method_ii=False,
        )
        assert result.rebate_per_unit == 0.0

    def test_none_benchmark_returns_zero_rebate(self):
        result = calculate_guard_rebate(
            us_net_price=100000,
            method_i=None,
            method_ii=None,
            use_method_ii=False,
        )
        assert result.rebate_per_unit == 0.0
        assert result.benchmark is None

    def test_globe_rebate_identical_structure(self):
        r_guard = calculate_guard_rebate(100000, 80000, 75000, False)
        r_globe = calculate_globe_rebate(100000, 80000, 75000, False)
        assert r_guard.rebate_per_unit == r_globe.rebate_per_unit
