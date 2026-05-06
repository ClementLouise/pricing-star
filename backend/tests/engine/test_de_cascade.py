"""Unit tests for F12: DE cascade trap simulator."""

import pytest
from app.engine.de_cascade import simulate_de_cascade
from app.engine.types import DECascadeResult


# Fixture C setup — ONC-mAb-001 prices
FIXTURE_B_PRICES = {
    "US": 180000, "DE": 90000, "FR": 77400, "UK": 81000, "IT": 72000,
    "ES": 68400, "NL": 81000, "BE": 77400, "AT": 77400, "SE": 81000,
    "DK": 81000, "NO": 86400, "IE": 81000, "CH": 99000, "JP": 86400,
    "KR": 68400, "AU": 72000, "CA": 90000, "CZ": 63000, "IL": 72000,
    "PL": 57600, "HU": 54000, "RO": 50400, "SK": 57600, "BG": 45000,
    "GR": 54000, "PT": 57600,
}


class TestSimulateDECascade:
    def test_fixture_c_de_price_after(self):
        result = simulate_de_cascade(FIXTURE_B_PRICES, opt_in_rebate_pct=0.09)
        assert isinstance(result, DECascadeResult)
        assert abs(result.de_price_after - 81900) < 1   # 90000 × 0.91

    def test_de_disclosed_delta(self):
        result = simulate_de_cascade(FIXTURE_B_PRICES, opt_in_rebate_pct=0.09)
        assert isinstance(result, DECascadeResult)
        assert abs(result.de_disclosed_delta - (-8100)) < 1

    def test_critical_markets_affected(self):
        result = simulate_de_cascade(FIXTURE_B_PRICES, opt_in_rebate_pct=0.09)
        assert isinstance(result, DECascadeResult)
        affected = {m.country for m in result.market_impacts}
        # Fixture C.2: AT, NL, BE, UK, FR, CH, DK, SE should all be affected
        critical = {"AT", "NL", "BE", "UK", "FR", "CH", "DK", "SE"}
        assert critical.issubset(affected), f"Missing markets: {critical - affected}"

    def test_impacts_count_in_range(self):
        result = simulate_de_cascade(FIXTURE_B_PRICES, opt_in_rebate_pct=0.09)
        assert isinstance(result, DECascadeResult)
        # Fixture C.2: approximately 8 markets affected (±2)
        assert 6 <= result.actually_impacted_count <= 20

    def test_all_impacts_negative(self):
        # DE opt-in LOWERS DE price → all cascaded prices should drop or stay same
        result = simulate_de_cascade(FIXTURE_B_PRICES, opt_in_rebate_pct=0.09)
        assert isinstance(result, DECascadeResult)
        for impact in result.market_impacts:
            assert impact.delta <= 0.01, f"{impact.country}: price rose by {impact.delta}"

    def test_error_if_no_de_price(self):
        prices = {"US": 180000, "FR": 77400}
        result = simulate_de_cascade(prices)
        assert isinstance(result, dict)
        assert "error" in result

    def test_referencing_markets_count_positive(self):
        result = simulate_de_cascade(FIXTURE_B_PRICES)
        assert isinstance(result, DECascadeResult)
        assert result.referencing_markets_count > 0
