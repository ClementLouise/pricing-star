"""Unit tests for EC-TRIAL-01: real data heuristic detection."""
from types import SimpleNamespace

import pytest

from app.services.trial_heuristic import check_real_data_heuristic


def _asset(us_list_price=None, therapeutic_area=None):
    return SimpleNamespace(us_list_price=us_list_price, therapeutic_area=therapeutic_area)


def _cd(country_code: str, launched: bool = True):
    return SimpleNamespace(country_code=country_code, launched=launched)


_FIVE_OECD = [_cd(c) for c in ("DE", "FR", "UK", "IT", "ES")]
_FOUR_OECD = [_cd(c) for c in ("DE", "FR", "UK", "IT")]


# ─── Triggered cases (score >= 2) ─────────────────────────────────────────────

def test_high_price_plus_real_ta_triggers():
    """Criteria 1 + 4 (+ 2 since 189000 is ×1000) → score >= 2 → triggered."""
    result = check_real_data_heuristic(_asset(189_000, "NSCLC"), [])
    assert result.triggered
    assert result.score >= 2
    assert result.breakdown["high_list_price"]
    assert result.breakdown["real_therapeutic_area"]


def test_high_price_plus_round_number_triggers():
    """Criteria 1 + 2 → score 2 (price is both >100k and ×1000)."""
    result = check_real_data_heuristic(_asset(150_000, None), [])
    assert result.triggered
    assert result.score >= 2
    assert result.breakdown["high_list_price"]
    assert result.breakdown["marketing_round_number"]


def test_five_oecd_plus_real_ta_triggers():
    """Criteria 3 + 4 → score 2."""
    result = check_real_data_heuristic(_asset(50_000, "Oncology"), _FIVE_OECD)
    assert result.triggered
    assert result.breakdown["oecd_markets_5plus"]
    assert result.breakdown["real_therapeutic_area"]


def test_all_four_criteria_triggers():
    """All 4 criteria → score 4."""
    asset = _asset(189_000, "NSCLC")
    result = check_real_data_heuristic(asset, _FIVE_OECD)
    assert result.triggered
    assert result.score == 4
    assert all(result.breakdown.values())


def test_price_ending_99_triggers_criterion_2():
    """$199,999 ends in '99' → criterion 2 fires."""
    result = check_real_data_heuristic(_asset(199_999, "Rare Disease"), [])
    assert result.triggered
    assert result.breakdown["marketing_round_number"]
    assert result.breakdown["real_therapeutic_area"]


# ─── Not triggered cases (score < 2) ──────────────────────────────────────────

def test_low_price_no_ta_no_markets_not_triggered():
    """Illustrative data (small price, generic TA, few markets) → not triggered."""
    result = check_real_data_heuristic(_asset(12_345, "Demo"), _FOUR_OECD)
    assert not result.triggered


def test_only_criterion_1_not_triggered():
    """High price alone (score 1) → not triggered."""
    result = check_real_data_heuristic(_asset(189_432, None), [])
    assert not result.triggered
    assert result.score == 1
    assert result.breakdown["high_list_price"]
    assert not result.breakdown["marketing_round_number"]  # not a round number


def test_only_four_oecd_markets_not_criterion_3():
    """4 OECD markets launched → criterion 3 not fired."""
    result = check_real_data_heuristic(_asset(None, None), _FOUR_OECD)
    assert not result.breakdown["oecd_markets_5plus"]


def test_generic_ta_demo_not_criterion_4():
    """TA = 'demo' → criterion 4 not fired."""
    result = check_real_data_heuristic(_asset(None, "demo"), [])
    assert not result.breakdown["real_therapeutic_area"]


def test_generic_ta_test_not_criterion_4():
    """TA = 'Test' (case-insensitive) → criterion 4 not fired."""
    result = check_real_data_heuristic(_asset(None, "Test"), [])
    assert not result.breakdown["real_therapeutic_area"]


# ─── Edge cases ───────────────────────────────────────────────────────────────

def test_none_asset_returns_not_triggered():
    """None asset → no crash, not triggered."""
    result = check_real_data_heuristic(None, _FIVE_OECD)
    assert not result.triggered
    assert result.score == 0


def test_unlaunched_oecd_markets_dont_count():
    """5 OECD markets but all unlaunched → criterion 3 not fired."""
    unlaunched = [_cd(c, launched=False) for c in ("DE", "FR", "GB", "IT", "ES")]
    result = check_real_data_heuristic(_asset(None, None), unlaunched)
    assert not result.breakdown["oecd_markets_5plus"]


def test_exactly_score_2_boundary():
    """Score 2 exactly (at boundary) → triggered (criteria 3 + 4 only)."""
    # 50_432: not >100k (no c1), not round/ending-99 (no c2), 5 OECD (c3), real TA (c4)
    result = check_real_data_heuristic(_asset(50_432, "Oncology"), _FIVE_OECD)
    assert result.triggered
    assert result.score == 2


def test_false_positive_rate_synthetic_illustrative():
    """Sample illustrative dataset: < 5% false positive rate.

    6 synthetic illustrative assets — heuristic should fire on 0 of them.
    """
    illustrative_cases = [
        (_asset(10_000, "Demo"), [_cd("US")]),
        (_asset(50_000, "Test"), [_cd("DE"), _cd("FR")]),
        (_asset(75_000, None), [_cd("DE")]),
        (_asset(None, "Example"), []),
        (_asset(99_000, "Training"), _FOUR_OECD),
        (_asset(12_345, "Sample"), [_cd("US"), _cd("DE"), _cd("FR")]),
    ]
    false_positives = sum(
        1 for (asset, cds) in illustrative_cases
        if check_real_data_heuristic(asset, cds).triggered
    )
    false_positive_rate = false_positives / len(illustrative_cases)
    assert false_positive_rate < 0.05, f"False positive rate too high: {false_positive_rate:.0%}"
