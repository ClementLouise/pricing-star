"""
Fixture A — VX-CFTR-NG (orphan premium).
All tests in this file are deployment gates: failure blocks merge.
Expected values sourced from docs/reference/test_results_v11.json.
"""

import pytest
from app.engine.cascade import run_cascade
from app.engine.methods import (
    calculate_guard_method_i,
    calculate_generous_price,
    calculate_guard_method_ii,
    calculate_guard_rebate,
)
from app.engine.npv import compute_npv
from app.engine.types import AssetConfig, CountryData, ScenarioConfig


# ─── Asset configuration (Fixture A.0) ──────────────────────────────────────

ASSET = AssetConfig(
    name="VX-CFTR-NG",
    us_list_price=370000,
    us_net_share=0.50,
    launch_year=2027,
    patent_expiry=2042,
    us_patient_population=30000,
    ex_us_patient_population=50000,
    patient_capture_rate_at_peak=0.60,
    ramp_years=5,
    discount_rate=0.10,
)

# Initial ex-US discounts applied to US list price before cascade
INITIAL_EX_US_DISCOUNT = {
    "DE": 0.78, "FR": 0.72, "UK": 0.75, "IT": 0.68, "ES": 0.62, "NL": 0.78, "BE": 0.75,
    "AT": 0.74, "CH": 0.85, "DK": 0.74, "SE": 0.74, "NO": 0.78, "FI": 0.74,
    "GR": 0.55, "PT": 0.55, "PL": 0.50, "CZ": 0.55, "HU": 0.45, "RO": 0.45,
    "SK": 0.45, "BG": 0.40, "JP": 0.85, "KR": 0.65, "AU": 0.70,
    "BR": 0.50, "MX": 0.45, "CL": 0.50, "CO": 0.40, "AR": 0.35,
    "SA": 0.55, "AE": 0.65, "CN": 0.40, "IN": 0.10,
    "CA": 0.65, "IE": 0.78, "IL": 0.65,
}

VOLUMES = {
    "DE": 0.06, "FR": 0.06, "UK": 0.05, "IT": 0.05, "ES": 0.04, "NL": 0.02,
    "BE": 0.015, "AT": 0.01, "CH": 0.01, "DK": 0.01, "SE": 0.015, "NO": 0.01, "FI": 0.005,
    "GR": 0.01, "PT": 0.01, "PL": 0.025, "CZ": 0.01, "HU": 0.005, "RO": 0.01, "SK": 0.005,
    "BG": 0.003, "JP": 0.05, "KR": 0.025, "AU": 0.02,
    "BR": 0.06, "MX": 0.04, "CL": 0.005, "CO": 0.005, "AR": 0.005,
    "SA": 0.005, "AE": 0.003, "CN": 0.30, "IN": 0.05, "CA": 0.04, "IE": 0.005, "IL": 0.003,
}

CONFIDENTIAL_REBATES = {
    "US": 0.50, "DE": 0.85, "FR": 0.75, "UK": 0.80, "IT": 0.70, "ES": 0.70,
    "NL": 0.85, "BE": 0.78, "AT": 0.85, "CH": 0.95, "DK": 0.80, "SE": 0.85,
    "NO": 0.80, "FI": 0.85, "GR": 0.55, "PT": 0.70, "PL": 0.80, "CZ": 0.85,
    "HU": 0.80, "RO": 0.75, "SK": 0.85, "BG": 0.85, "JP": 0.95, "KR": 0.85,
    "AU": 0.80, "BR": 0.75, "MX": 0.85, "CL": 0.85, "CO": 0.80, "AR": 0.70,
    "SA": 0.85, "AE": 0.85, "CN": 0.95, "IN": 0.95, "CA": 0.75, "IE": 0.80, "IL": 0.80,
}


@pytest.fixture(scope="module")
def cascaded_prices():
    initial = {"US": ASSET.us_list_price}
    for c, d in INITIAL_EX_US_DISCOUNT.items():
        initial[c] = ASSET.us_list_price * d
    return run_cascade(initial).final


@pytest.fixture(scope="module")
def scenario_config():
    return ScenarioConfig(
        country_data={
            c: CountryData(volume_share=VOLUMES[c], g2n_ratio=CONFIDENTIAL_REBATES.get(c, 0.80))
            for c in VOLUMES
        }
    )


# ─── A.2 Method I anchor analysis ──────────────────────────────────────────

class TestFixtureAMethodI:
    def test_anchor_country_is_ch(self, cascaded_prices):
        result = calculate_guard_method_i(cascaded_prices)
        assert result is not None
        assert result.country == "CH", f"Expected CH anchor, got {result.country}"

    def test_price(self, cascaded_prices):
        result = calculate_guard_method_i(cascaded_prices)
        assert result is not None
        assert abs(result.price - 187617.035) < 50


# ─── A.3 Method II at year 2028 ────────────────────────────────────────────

class TestFixtureAMethodII:
    def test_method_ii_2028(self, cascaded_prices):
        net_prices = {c: p * CONFIDENTIAL_REBATES.get(c, 0.80) for c, p in cascaded_prices.items()}
        vol_dict = {c: v for c, v in VOLUMES.items() if c in cascaded_prices}
        result = calculate_guard_method_ii(net_prices, vol_dict, year=2028)
        assert result is not None
        assert abs(result - 156799.399) < 200


# ─── A.4 Generous price ────────────────────────────────────────────────────

class TestFixtureAGenerous:
    def test_anchor_country_is_dk(self, cascaded_prices):
        result = calculate_generous_price(cascaded_prices)
        assert result is not None
        assert result.country == "DK"

    def test_price(self, cascaded_prices):
        result = calculate_generous_price(cascaded_prices)
        assert result is not None
        assert abs(result.price - 199612) < 50


# ─── A.5 Per-unit rebate ───────────────────────────────────────────────────

class TestFixtureARebate:
    def test_no_rebate_orphan_premium(self):
        # Method I (187617) > US net (185000) → zero rebate
        result = calculate_guard_rebate(
            us_net_price=185000,
            method_i=187617.035,
            method_ii=156799.399,
            use_method_ii=False,
        )
        assert result.rebate_per_unit == 0.0
        assert result.method_used == "I"


# ─── A.6 Full simulation NPV (deployment gate) ─────────────────────────────

class TestFixtureANPV:
    def test_baseline_npv(self, cascaded_prices, scenario_config):
        """DEPLOYMENT GATE: Baseline NPV must equal $46.74B ±$47M (0.1%)."""
        result = compute_npv(cascaded_prices, ASSET, scenario_config)
        expected = 46_740_264_300.06
        tolerance = expected * 0.001  # ±0.1%
        assert abs(result.npv - expected) < tolerance, (
            f"Baseline NPV {result.npv:.0f} differs from expected {expected:.0f} "
            f"by {abs(result.npv - expected):.0f} (tolerance {tolerance:.0f})"
        )

    def test_full_mfn_npv_unchanged_for_orphan(self, cascaded_prices, scenario_config):
        """Orphan premium: MFN doesn't bite → NPV unchanged vs baseline."""
        us_net = ASSET.us_list_price * ASSET.us_net_share  # 185000
        result = compute_npv(cascaded_prices, ASSET, scenario_config, us_net_override=us_net)
        expected = 46_740_264_300.06
        tolerance = expected * 0.001
        assert abs(result.npv - expected) < tolerance

    def test_peak_revenue(self, cascaded_prices, scenario_config):
        result = compute_npv(cascaded_prices, ASSET, scenario_config)
        expected_peak = 7_600_294_422.79
        assert abs(result.peak_revenue - expected_peak) < expected_peak * 0.001

    def test_yearly_breakdown_has_15_years(self, cascaded_prices, scenario_config):
        result = compute_npv(cascaded_prices, ASSET, scenario_config)
        assert len(result.yearly_breakdown) == 15  # patent_expiry(2042) - launch(2027) + 1 = 16, capped at 15
