"""Unit tests for F11: MFN anchor analysis."""

import pytest
from app.engine.anchor import analyze_mfn_anchor
from app.engine.cascade import run_cascade


# ONC-mAb-001 initial prices (180000 × INITIAL_EX_US_DISCOUNT) then cascaded.
# IE is NOT in IRP_RULES → stays at initial 81000. CH cascades to ~55284.
_INITIAL_B = {
    "US": 180000, "DE": 90000, "JP": 86400, "CH": 99000, "CA": 90000,
    "FR": 77400, "UK": 81000, "IT": 72000, "ES": 68400, "NL": 81000,
    "BE": 77400, "AT": 77400, "SE": 81000, "DK": 81000, "NO": 86400,
    "FI": 75600, "IE": 81000, "GR": 54000, "PT": 57600, "PL": 57600,
    "CZ": 63000, "HU": 54000, "RO": 50400, "SK": 57600, "BG": 45000,
    "KR": 68400, "AU": 72000, "BR": 57600, "MX": 54000, "CL": 57600,
    "CO": 50400, "AR": 45000, "SA": 68400, "AE": 72000,
    "CN": 36000, "IN": 14400, "IL": 72000,
}
FIXTURE_B_PRICES = run_cascade(_INITIAL_B).final


class TestAnalyzeMFNAnchor:
    def test_fixture_b_anchor_is_ch(self):
        result = analyze_mfn_anchor(FIXTURE_B_PRICES, model="GUARD")
        assert result is not None
        assert result.anchor.country == "CH"

    def test_fixture_b_benchmark(self):
        result = analyze_mfn_anchor(FIXTURE_B_PRICES, model="GUARD")
        assert result is not None
        assert abs(result.benchmark - 56390) < 50  # ±$50 tolerance

    def test_fixture_b_second_is_nl(self):
        result = analyze_mfn_anchor(FIXTURE_B_PRICES, model="GUARD")
        assert result is not None
        assert result.second.country == "NL"

    def test_benchmark_is_anchor_times_102(self):
        result = analyze_mfn_anchor(FIXTURE_B_PRICES, model="GUARD")
        assert result is not None
        assert abs(result.benchmark - result.anchor.adjusted * 1.02) < 0.01

    def test_all_ranked_length(self):
        result = analyze_mfn_anchor(FIXTURE_B_PRICES, model="GUARD")
        assert result is not None
        assert len(result.all_ranked) == 19  # OECD-19 basket

    def test_all_ranked_sorted_ascending(self):
        result = analyze_mfn_anchor(FIXTURE_B_PRICES, model="GUARD")
        assert result is not None
        adjusted = [c.adjusted for c in result.all_ranked]
        assert adjusted == sorted(adjusted)

    def test_is_non_obvious_anchor(self):
        result = analyze_mfn_anchor(FIXTURE_B_PRICES, model="GUARD")
        assert result is not None
        assert result.is_non_obvious_anchor is True  # CH ≠ CZ (lowest nominal)

    def test_returns_none_if_empty_prices(self):
        assert analyze_mfn_anchor({}) is None

    def test_unknown_model_returns_none(self):
        assert analyze_mfn_anchor(FIXTURE_B_PRICES, model="UNKNOWN") is None

    def test_generous_model(self):
        result = analyze_mfn_anchor(FIXTURE_B_PRICES, model="GENEROUS")
        assert result is not None
        assert result.model == "GENEROUS"
        # Generous basket has 8 countries
        assert len(result.all_ranked) <= 8

    def test_ringfence_recommendation_string(self):
        result = analyze_mfn_anchor(FIXTURE_B_PRICES, model="GUARD")
        assert result is not None
        assert isinstance(result.ringfence_recommendation, str)
        assert len(result.ringfence_recommendation) > 10
