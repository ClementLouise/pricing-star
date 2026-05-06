"""
Fixture B — ONC-mAb-001 (oncology biologic) + Fixture D (cascade convergence).
All tests in this file are deployment gates: failure blocks merge.
Expected values sourced from docs/reference/test_v20_results.json.
"""

import pytest
from app.engine.cascade import run_cascade
from app.engine.methods import (
    calculate_guard_method_i,
    calculate_guard_method_ii,
    calculate_guard_rebate,
)
from app.engine.npv import compute_npv
from app.engine.types import AssetConfig, CountryData, ScenarioConfig


# ─── Asset configuration (Fixture B.0) ──────────────────────────────────────

ASSET = AssetConfig(
    name="ONC-mAb-001 (PD-L1 NSCLC 1L)",
    us_list_price=180000,
    us_net_share=0.50,
    launch_year=2027,
    patent_expiry=2040,
    us_patient_population=12000,
    ex_us_patient_population=35000,
    patient_capture_rate_at_peak=0.35,
    ramp_years=4,
    discount_rate=0.10,
    part_b_share=0.85,
)

INITIAL_EX_US_DISCOUNT = {
    "DE": 0.50, "JP": 0.48, "CH": 0.55, "CA": 0.50,
    "FR": 0.43, "UK": 0.45, "IT": 0.40, "ES": 0.38, "NL": 0.45,
    "BE": 0.43, "AT": 0.43, "SE": 0.45, "DK": 0.45, "NO": 0.48,
    "FI": 0.42, "IE": 0.45,
    "GR": 0.30, "PT": 0.32, "PL": 0.32, "CZ": 0.35, "HU": 0.30,
    "RO": 0.28, "SK": 0.32, "BG": 0.25,
    "KR": 0.38, "AU": 0.40,
    "BR": 0.32, "MX": 0.30, "CL": 0.32, "CO": 0.28, "AR": 0.25,
    "SA": 0.38, "AE": 0.40,
    "CN": 0.20, "IN": 0.08,
    "IL": 0.40,
}

VOLUMES = {
    "DE": 0.10, "FR": 0.08, "UK": 0.07, "IT": 0.06, "ES": 0.05,
    "NL": 0.025, "BE": 0.018, "AT": 0.012, "SE": 0.018, "DK": 0.012,
    "NO": 0.010, "FI": 0.007, "IE": 0.006,
    "JP": 0.08, "KR": 0.04, "AU": 0.025,
    "CA": 0.04,
    "CN": 0.18,
    "BR": 0.04, "MX": 0.025, "CL": 0.005, "CO": 0.008, "AR": 0.005,
    "PL": 0.015, "CZ": 0.008, "HU": 0.005, "RO": 0.008, "SK": 0.004,
    "BG": 0.003, "GR": 0.006, "PT": 0.005,
    "SA": 0.005, "AE": 0.003,
    "CH": 0.008,
    "IN": 0.025,
    "IL": 0.003,
}

CONFIDENTIAL_REBATES = {
    "US": 0.50, "DE": 0.85, "FR": 0.75, "UK": 0.80, "IT": 0.70, "ES": 0.70,
    "NL": 0.85, "BE": 0.78, "AT": 0.85, "CH": 0.95, "DK": 0.80, "SE": 0.85,
    "NO": 0.80, "FI": 0.85, "GR": 0.55, "PT": 0.70, "PL": 0.80, "CZ": 0.85,
    "HU": 0.80, "RO": 0.75, "SK": 0.85, "BG": 0.85, "JP": 0.95, "KR": 0.85,
    "AU": 0.80, "BR": 0.75, "MX": 0.85, "CL": 0.85, "CO": 0.80, "AR": 0.70,
    "SA": 0.85, "AE": 0.85, "CN": 0.95, "IN": 0.95, "CA": 0.75, "IE": 0.80,
    "IL": 0.80, "TR": 0.70,
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


# ─── B.2 Method I anchor ──────────────────────────────────────────────────

class TestFixtureBMethodI:
    def test_anchor_country_is_ch(self, cascaded_prices):
        result = calculate_guard_method_i(cascaded_prices)
        assert result is not None
        assert result.country == "CH", f"Expected CH, got {result.country}"

    def test_price(self, cascaded_prices):
        result = calculate_guard_method_i(cascaded_prices)
        assert result is not None
        assert abs(result.price - 56389.977) < 50


# ─── B.3 Method II at year 2028 ──────────────────────────────────────────

class TestFixtureBMethodII:
    def test_method_ii_2028(self, cascaded_prices):
        net_prices = {c: p * CONFIDENTIAL_REBATES.get(c, 0.80) for c, p in cascaded_prices.items()}
        vol_dict = {c: v for c, v in VOLUMES.items() if c in cascaded_prices}
        result = calculate_guard_method_ii(net_prices, vol_dict, year=2028)
        assert result is not None
        assert abs(result - 50422.723) < 300


# ─── B.4 Per-unit rebate ──────────────────────────────────────────────────

class TestFixtureBRebate:
    def test_rebate_33610(self, cascaded_prices):
        result = calculate_guard_rebate(
            us_net_price=90000,
            method_i=56389.977,
            method_ii=50422.723,
            use_method_ii=False,
        )
        assert abs(result.rebate_per_unit - 33610.023) < 1
        assert result.method_used == "I"


# ─── B.5 Full simulation NPV — MFN scenario (deployment gate) ─────────────

class TestFixtureBNPVMFN:
    def test_mfn_npv(self, cascaded_prices, scenario_config):
        """DEPLOYMENT GATE: MFN NPV must equal $4.96B ±$5M (0.1%)."""
        result = compute_npv(
            cascaded_prices,
            ASSET,
            scenario_config,
            us_net_override=56389.977,  # effective_us_net after Guard rebate
        )
        expected = 4_962_668_554.61
        tolerance = expected * 0.001
        assert abs(result.npv - expected) < tolerance, (
            f"MFN NPV {result.npv:.0f} differs from expected {expected:.0f} "
            f"by {abs(result.npv - expected):.0f} (tolerance {tolerance:.0f})"
        )

    def test_peak_revenue_mfn(self, cascaded_prices, scenario_config):
        result = compute_npv(
            cascaded_prices, ASSET, scenario_config, us_net_override=56389.977
        )
        expected_peak = 790_603_946.54
        assert abs(result.peak_revenue - expected_peak) < expected_peak * 0.001


# ─── B.6 Baseline NPV (deployment gate) ──────────────────────────────────

class TestFixtureBNPVBaseline:
    def test_baseline_npv(self, cascaded_prices, scenario_config):
        """DEPLOYMENT GATE: Baseline NPV must equal $5.85B ±$5.85M (0.1%)."""
        result = compute_npv(cascaded_prices, ASSET, scenario_config)
        expected = 5_848_751_536.33
        tolerance = expected * 0.001
        assert abs(result.npv - expected) < tolerance, (
            f"Baseline NPV {result.npv:.0f} differs from expected {expected:.0f} "
            f"by {abs(result.npv - expected):.0f} (tolerance {tolerance:.0f})"
        )

    def test_yearly_breakdown_has_14_years(self, cascaded_prices, scenario_config):
        result = compute_npv(cascaded_prices, ASSET, scenario_config)
        assert len(result.yearly_breakdown) == 14  # min(2040-2027+1, 15) = 14


# ─── B.7 NPV erosion percentage ──────────────────────────────────────────

class TestFixtureBErosion:
    def test_npv_erosion_pct(self, cascaded_prices, scenario_config):
        baseline = compute_npv(cascaded_prices, ASSET, scenario_config)
        mfn = compute_npv(cascaded_prices, ASSET, scenario_config, us_net_override=56389.977)
        delta = mfn.npv - baseline.npv
        delta_pct = delta / baseline.npv
        # Fixture B.7: delta ≈ -$890M, -15.1% ±0.5pp
        assert abs(delta_pct - (-0.151)) < 0.005, (
            f"NPV erosion {delta_pct:.3f} outside ±0.5pp of -15.1%"
        )


# ─── Fixture D: Cascade convergence ──────────────────────────────────────

class TestFixtureDConvergence:
    def test_converges_within_max_iterations(self, cascaded_prices):
        # Re-run cascade from initial to verify convergence behavior
        initial = {"US": ASSET.us_list_price}
        for c, d in INITIAL_EX_US_DISCOUNT.items():
            initial[c] = ASSET.us_list_price * d
        result = run_cascade(initial, max_iterations=5)
        assert result.iterations <= 5, (
            f"Cascade took {result.iterations} iterations, expected ≤5"
        )
