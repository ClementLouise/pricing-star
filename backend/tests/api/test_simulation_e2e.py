"""
E2E simulation pipeline tests — deployment gates.
Validates the full HTTP pipeline: asset → scenario + country data → simulate.
Tests the DB→engine mapping layer that unit fixture tests in tests/fixtures/ bypass.

These tests call the same HTTP endpoints a real client would use,
go through SQLite in-memory persistence, and assert against the same expected
NPVs as the unit fixtures. Any discrepancy reveals a bug in the mapping layer.
"""
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models import (  # noqa: F401 — ensures all tables are in Base.metadata
    Asset, AuditLog, CountryData, Scenario, SimulationResult, Tenant, User,
)
from tests.api.conftest import make_tenant, make_user


# ─── Fixture A: VX-CFTR-NG (orphan premium) ──────────────────────────────────
# Source: docs/PRD_v2/10_TEST_FIXTURES.md §A.0 and §A.1

FIXTURE_A_ASSET = {
    "name": "VX-CFTR-NG",
    "us_list_price": 370000,
    "us_net_share": 0.50,
    "launch_year": 2027,
    "loe_year": 2042,
    "us_patient_population": 30000,
    "ex_us_patient_population": 50000,
    "peak_capture_rate": 0.60,
    "ramp_years": 5,
    "discount_rate": 0.10,
}

# Discount factors applied to us_list_price to get initial (pre-cascade) list prices
FIXTURE_A_DISCOUNTS: dict[str, float] = {
    "DE": 0.78, "FR": 0.72, "UK": 0.75, "IT": 0.68, "ES": 0.62, "NL": 0.78, "BE": 0.75,
    "AT": 0.74, "CH": 0.85, "DK": 0.74, "SE": 0.74, "NO": 0.78, "FI": 0.74,
    "GR": 0.55, "PT": 0.55, "PL": 0.50, "CZ": 0.55, "HU": 0.45, "RO": 0.45,
    "SK": 0.45, "BG": 0.40, "JP": 0.85, "KR": 0.65, "AU": 0.70,
    "BR": 0.50, "MX": 0.45, "CL": 0.50, "CO": 0.40, "AR": 0.35,
    "SA": 0.55, "AE": 0.65, "CN": 0.40, "IN": 0.10,
    "CA": 0.65, "IE": 0.78, "IL": 0.65,
}

FIXTURE_A_VOLUMES: dict[str, float] = {
    "DE": 0.06, "FR": 0.06, "UK": 0.05, "IT": 0.05, "ES": 0.04, "NL": 0.02,
    "BE": 0.015, "AT": 0.01, "CH": 0.01, "DK": 0.01, "SE": 0.015, "NO": 0.01, "FI": 0.005,
    "GR": 0.01, "PT": 0.01, "PL": 0.025, "CZ": 0.01, "HU": 0.005, "RO": 0.01, "SK": 0.005,
    "BG": 0.003, "JP": 0.05, "KR": 0.025, "AU": 0.02,
    "BR": 0.06, "MX": 0.04, "CL": 0.005, "CO": 0.005, "AR": 0.005,
    "SA": 0.005, "AE": 0.003, "CN": 0.30, "IN": 0.05, "CA": 0.04, "IE": 0.005, "IL": 0.003,
}

FIXTURE_A_G2N: dict[str, float] = {
    "US": 0.50, "DE": 0.85, "FR": 0.75, "UK": 0.80, "IT": 0.70, "ES": 0.70,
    "NL": 0.85, "BE": 0.78, "AT": 0.85, "CH": 0.95, "DK": 0.80, "SE": 0.85,
    "NO": 0.80, "FI": 0.85, "GR": 0.55, "PT": 0.70, "PL": 0.80, "CZ": 0.85,
    "HU": 0.80, "RO": 0.75, "SK": 0.85, "BG": 0.85, "JP": 0.95, "KR": 0.85,
    "AU": 0.80, "BR": 0.75, "MX": 0.85, "CL": 0.85, "CO": 0.80, "AR": 0.70,
    "SA": 0.85, "AE": 0.85, "CN": 0.95, "IN": 0.95, "CA": 0.75, "IE": 0.80, "IL": 0.80,
}


# ─── Fixture B: ONC-mAb-001 (oncology biologic) ──────────────────────────────
# Source: docs/PRD_v2/10_TEST_FIXTURES.md §B.0 and §B.1

FIXTURE_B_ASSET = {
    "name": "ONC-mAb-001",
    "us_list_price": 180000,
    "us_net_share": 0.50,
    "launch_year": 2027,
    "loe_year": 2040,
    "us_patient_population": 12000,
    "ex_us_patient_population": 35000,
    "peak_capture_rate": 0.35,
    "ramp_years": 4,
    "discount_rate": 0.10,
    "part_b_share": 0.85,
}

FIXTURE_B_DISCOUNTS: dict[str, float] = {
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

FIXTURE_B_VOLUMES: dict[str, float] = {
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

FIXTURE_B_G2N: dict[str, float] = {
    "US": 0.50, "DE": 0.85, "FR": 0.75, "UK": 0.80, "IT": 0.70, "ES": 0.70,
    "NL": 0.85, "BE": 0.78, "AT": 0.85, "CH": 0.95, "DK": 0.80, "SE": 0.85,
    "NO": 0.80, "FI": 0.85, "GR": 0.55, "PT": 0.70, "PL": 0.80, "CZ": 0.85,
    "HU": 0.80, "RO": 0.75, "SK": 0.85, "BG": 0.85, "JP": 0.95, "KR": 0.85,
    "AU": 0.80, "BR": 0.75, "MX": 0.85, "CL": 0.85, "CO": 0.80, "AR": 0.70,
    "SA": 0.85, "AE": 0.85, "CN": 0.95, "IN": 0.95, "CA": 0.75, "IE": 0.80,
    "IL": 0.80,
}


# ─── Regulation configs ───────────────────────────────────────────────────────

FULL_MFN_REGULATIONS = {
    "generous": {"active": True, "year": 2027},
    "guard": {"active": True, "year": 2028},
    "globe": {"active": True, "year": 2029},
}

BASELINE_REGULATIONS = {
    "generous": {"active": False},
    "guard": {"active": False},
    "globe": {"active": False},
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_client(db_session: AsyncSession, user: User) -> AsyncClient:
    """Test HTTP client with DB and auth overrides (no JWT required)."""
    async def _db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    async def _user() -> User:
        return user

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = _user
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


def _build_country_data(
    discounts: dict[str, float],
    volumes: dict[str, float],
    g2n: dict[str, float],
    us_list_price: float,
) -> dict:
    """
    Build the country_data dict for ScenarioCreate.
    list_price = pre-cascade initial price (service runs cascade internally).
    Countries absent from volumes get volume=None and are excluded from NPV.
    """
    return {
        country: {
            "list_price": round(us_list_price * discount, 6),
            "volume": volumes.get(country),
            "g2n_ratio": g2n.get(country, 0.80),
            "launched": True,
            "launch_year": 2027,
        }
        for country, discount in discounts.items()
    }


# ─── Pytest fixture ───────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def e2e_actor(db_session: AsyncSession) -> dict:
    """Isolated tenant + admin user for E2E simulation tests."""
    tenant = make_tenant("E2E Pharma")
    user = make_user(tenant, role="admin")
    db_session.add(tenant)
    db_session.add(user)
    await db_session.flush()
    return {"tenant": tenant, "user": user}


# ─── Tests ───────────────────────────────────────────────────────────────────

async def test_simulate_fixture_a_returns_46_74B(
    db_session: AsyncSession, e2e_actor: dict
) -> None:
    """
    E2E deployment gate — Fixture A (VX-CFTR-NG orphan premium).

    Full HTTP pipeline exercises _build_asset_config, _build_engine_prices,
    and _build_scenario_config mapping functions that unit tests bypass.

    Expected: NPV $46.74B ±0.1%, zero rebate (Method I > US net).
    """
    user = e2e_actor["user"]
    country_data = _build_country_data(
        FIXTURE_A_DISCOUNTS, FIXTURE_A_VOLUMES, FIXTURE_A_G2N,
        us_list_price=FIXTURE_A_ASSET["us_list_price"],  # type: ignore[arg-type]
    )

    try:
        async with _make_client(db_session, user) as ac:
            # Step 1 — create asset
            resp = await ac.post("/api/assets", json=FIXTURE_A_ASSET)
            assert resp.status_code == 201, f"POST /assets failed: {resp.text}"
            asset_id = resp.json()["id"]

            # Step 2 — create scenario with all country data inline
            resp = await ac.post(f"/api/assets/{asset_id}/scenarios", json={
                "name": "Fixture A — Full MFN G+G+G",
                "regulations": FULL_MFN_REGULATIONS,
                "country_data": country_data,
            })
            assert resp.status_code == 201, f"POST /scenarios failed: {resp.text}"
            scenario_id = resp.json()["id"]

            # Step 3 — run simulation
            resp = await ac.post(f"/api/scenarios/{scenario_id}/simulate")
            assert resp.status_code == 200, f"POST /simulate failed: {resp.text}"
            result = resp.json()["results"]

    finally:
        app.dependency_overrides.clear()

    npv = result["npv"]
    expected_npv = 46_740_264_300.06
    npv_delta_pct = abs(npv - expected_npv) / expected_npv

    assert npv_delta_pct < 0.001, (
        f"NPV {npv:.0f} deviates from expected {expected_npv:.0f} "
        f"by {npv_delta_pct:.4%} (tolerance 0.1%)"
    )
    assert result["method_i_anchor"] == "CH", (
        f"Expected CH anchor, got {result['method_i_anchor']}"
    )
    assert abs(result["method_i_value"] - 187617.035) < 50, (
        f"Method I value {result['method_i_value']:.1f} deviates from 187617 by more than $50"
    )
    assert result["per_unit_rebate"] == 0.0, (
        f"Expected zero rebate (orphan premium — Method I > US net), "
        f"got {result['per_unit_rebate']}"
    )
    assert abs(result["effective_us_net"] - 185000) < 1, (
        f"Expected effective_us_net=185000, got {result['effective_us_net']}"
    )


async def test_simulate_fixture_b_returns_4_96B(
    db_session: AsyncSession, e2e_actor: dict
) -> None:
    """
    E2E deployment gate — Fixture B (ONC-mAb-001 oncology biologic).

    Tests both MFN scenario ($4.96B) and baseline ($5.85B), then computes
    erosion (-15.1%) — the headline finding for mid-tier oncology biologics.

    Exercises the full mapping + cascade + rebate + NPV pipeline via HTTP.
    """
    user = e2e_actor["user"]
    country_data = _build_country_data(
        FIXTURE_B_DISCOUNTS, FIXTURE_B_VOLUMES, FIXTURE_B_G2N,
        us_list_price=FIXTURE_B_ASSET["us_list_price"],  # type: ignore[arg-type]
    )

    try:
        async with _make_client(db_session, user) as ac:
            # Create asset
            resp = await ac.post("/api/assets", json=FIXTURE_B_ASSET)
            assert resp.status_code == 201, f"POST /assets failed: {resp.text}"
            asset_id = resp.json()["id"]

            # MFN scenario (Guard active → rebate applies)
            resp = await ac.post(f"/api/assets/{asset_id}/scenarios", json={
                "name": "Fixture B — Full MFN G+G+G",
                "regulations": FULL_MFN_REGULATIONS,
                "country_data": country_data,
            })
            assert resp.status_code == 201, f"POST /scenarios (MFN) failed: {resp.text}"
            mfn_scenario_id = resp.json()["id"]

            # Baseline scenario (no MFN → no rebate)
            resp = await ac.post(f"/api/assets/{asset_id}/scenarios", json={
                "name": "Fixture B — Baseline (no MFN)",
                "regulations": BASELINE_REGULATIONS,
                "country_data": country_data,
            })
            assert resp.status_code == 201, f"POST /scenarios (baseline) failed: {resp.text}"
            baseline_scenario_id = resp.json()["id"]

            # Run MFN simulation
            resp = await ac.post(f"/api/scenarios/{mfn_scenario_id}/simulate")
            assert resp.status_code == 200, f"POST /simulate (MFN) failed: {resp.text}"
            mfn_result = resp.json()["results"]

            # Run baseline simulation
            resp = await ac.post(f"/api/scenarios/{baseline_scenario_id}/simulate")
            assert resp.status_code == 200, f"POST /simulate (baseline) failed: {resp.text}"
            baseline_result = resp.json()["results"]

    finally:
        app.dependency_overrides.clear()

    mfn_npv = mfn_result["npv"]
    baseline_npv = baseline_result["npv"]

    expected_mfn_npv = 4_962_668_554.61
    expected_baseline_npv = 5_848_751_536.33

    mfn_delta_pct = abs(mfn_npv - expected_mfn_npv) / expected_mfn_npv
    baseline_delta_pct = abs(baseline_npv - expected_baseline_npv) / expected_baseline_npv
    erosion_pct = (mfn_npv - baseline_npv) / baseline_npv

    assert mfn_delta_pct < 0.001, (
        f"MFN NPV {mfn_npv:.0f} deviates from expected {expected_mfn_npv:.0f} "
        f"by {mfn_delta_pct:.4%} (tolerance 0.1%)"
    )
    assert baseline_delta_pct < 0.001, (
        f"Baseline NPV {baseline_npv:.0f} deviates from expected {expected_baseline_npv:.0f} "
        f"by {baseline_delta_pct:.4%} (tolerance 0.1%)"
    )
    assert mfn_result["method_i_anchor"] == "CH", (
        f"Expected CH anchor, got {mfn_result['method_i_anchor']}"
    )
    assert abs(mfn_result["method_i_value"] - 56389.977) < 50, (
        f"Method I value {mfn_result['method_i_value']:.1f} deviates from 56390 by more than $50"
    )
    assert abs(mfn_result["per_unit_rebate"] - 33610.023) < 10, (
        f"Per-unit rebate {mfn_result['per_unit_rebate']:.1f} deviates from 33610 by more than $10"
    )
    assert abs(erosion_pct - (-0.151)) < 0.005, (
        f"NPV erosion {erosion_pct:.3f} outside ±0.5pp of -15.1% "
        f"(MFN={mfn_npv:.0f}, baseline={baseline_npv:.0f})"
    )
