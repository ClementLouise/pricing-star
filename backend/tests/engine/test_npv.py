"""Unit tests for F9-F10: volume projection and NPV computation."""

import pytest
from app.engine.npv import project_volume, resolve_g2n, compute_npv
from app.engine.types import AssetConfig, CountryData, ScenarioConfig


class TestProjectVolume:
    def test_zero_before_launch(self):
        assert project_volume(1000, 2026, 2027, 2032, 2042) == 0

    def test_ramp_increases_linearly(self):
        v1 = project_volume(1000, 2027, 2027, 2032, 2042)
        v2 = project_volume(1000, 2028, 2027, 2032, 2042)
        assert v2 > v1

    def test_plateau_at_peak(self):
        base = 1000
        # During plateau: peak ≤ year < loe
        v_peak = project_volume(base, 2032, 2027, 2032, 2042)
        v_mid = project_volume(base, 2035, 2027, 2032, 2042)
        assert v_peak == pytest.approx(base, rel=1e-6)
        assert v_mid == pytest.approx(base, rel=1e-6)

    def test_post_loe_erosion(self):
        base = 1000
        loe = 2040
        # year = loe → 1 - 0.20*0 = 1.0 (no erosion yet)
        assert project_volume(base, loe, 2027, 2031, loe) == pytest.approx(base, rel=1e-6)
        # year = loe + 1 → 1 - 0.20*1 = 0.80
        assert project_volume(base, loe + 1, 2027, 2031, loe) == pytest.approx(base * 0.80, rel=1e-6)
        # year = loe + 5 → 10% long tail
        assert project_volume(base, loe + 5, 2027, 2031, loe) == pytest.approx(base * 0.10, rel=1e-6)

    def test_ramp_reaches_full_at_peak_year(self):
        base = 5000
        launch, peak = 2027, 2032
        v = project_volume(base, peak, launch, peak, 2042)
        # At year == peak: year < peak is False, year < loe is True → returns base
        assert v == pytest.approx(base, rel=1e-6)


class TestResolveG2N:
    def test_time_series_single_entry(self):
        cd = CountryData(g2n_time_series={"2027": 0.75})
        config = ScenarioConfig(country_data={"DE": cd})
        assert resolve_g2n("DE", 2028, config, {}) == pytest.approx(0.75)

    def test_time_series_multi_entry(self):
        cd = CountryData(g2n_time_series={"2028": 0.72, "2029": 0.68})
        config = ScenarioConfig(country_data={"FR": cd})
        assert resolve_g2n("FR", 2028, config, {}) == pytest.approx(0.72)
        assert resolve_g2n("FR", 2029, config, {}) == pytest.approx(0.68)

    def test_fallback_to_g2n_ratio(self):
        cd = CountryData(g2n_ratio=0.80)
        config = ScenarioConfig(country_data={"UK": cd})
        assert resolve_g2n("UK", 2028, config, {}) == pytest.approx(0.80)

    def test_fallback_to_country_reference(self):
        config = ScenarioConfig(country_data={})
        ref = {"CH": {"default_g2n_ratio": 0.95}}
        assert resolve_g2n("CH", 2028, config, ref) == pytest.approx(0.95)

    def test_raises_if_no_fallback(self):
        config = ScenarioConfig(country_data={})
        with pytest.raises(ValueError, match="Cannot resolve G2N"):
            resolve_g2n("ZZ", 2028, config, {})


class TestComputeNPV:
    def _make_asset(self) -> AssetConfig:
        return AssetConfig(
            name="Test Asset",
            us_list_price=180000,
            us_net_share=0.50,
            launch_year=2027,
            patent_expiry=2040,
            us_patient_population=12000,
            ex_us_patient_population=35000,
            patient_capture_rate_at_peak=0.35,
            ramp_years=4,
            discount_rate=0.10,
        )

    def _make_scenario(self, prices: dict) -> ScenarioConfig:
        # Equal-weight volumes with g2n_ratio=0.80 for all countries
        return ScenarioConfig(
            country_data={
                c: CountryData(volume_share=0.01, g2n_ratio=0.80)
                for c in prices if c != "US"
            }
        )

    def test_npv_positive(self):
        prices = {"US": 180000, "DE": 90000, "FR": 77400, "UK": 81000}
        asset = self._make_asset()
        scenario = self._make_scenario(prices)
        result = compute_npv(prices, asset, scenario)
        assert result.npv > 0

    def test_peak_revenue_positive(self):
        prices = {"US": 180000, "DE": 90000}
        asset = self._make_asset()
        scenario = self._make_scenario(prices)
        result = compute_npv(prices, asset, scenario)
        assert result.peak_revenue > 0

    def test_us_net_override_reduces_npv(self):
        prices = {"US": 180000, "DE": 90000}
        asset = self._make_asset()
        scenario = self._make_scenario(prices)
        base_result = compute_npv(prices, asset, scenario)
        reduced_result = compute_npv(prices, asset, scenario, us_net_override=50000)
        assert reduced_result.npv < base_result.npv

    def test_yearly_breakdown_has_correct_years(self):
        prices = {"US": 180000}
        asset = self._make_asset()
        scenario = ScenarioConfig(country_data={})
        result = compute_npv(prices, asset, scenario)
        years = [row.year for row in result.yearly_breakdown]
        assert years[0] == 2027
        assert len(years) == 14  # min(2040-2027+1, 15) = 14

    def test_yearly_breakdown_g2n_tracked(self):
        prices = {"US": 180000, "DE": 90000}
        asset = self._make_asset()
        scenario = ScenarioConfig(
            country_data={"DE": CountryData(volume_share=0.10, g2n_ratio=0.85)}
        )
        result = compute_npv(prices, asset, scenario)
        peak_row = next(r for r in result.yearly_breakdown if r.year == 2027 + asset.ramp_years)
        assert "DE" in peak_row.g2n_used
        assert peak_row.g2n_used["DE"] == pytest.approx(0.85)
