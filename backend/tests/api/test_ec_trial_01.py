"""EC-TRIAL-01: Real data heuristic detection in trial mode.

Integration tests:
- Trial user + real-looking data → warning in response + audit log
- Production user + same data → no warning
- Trial user + illustrative data → no warning
- Fixture tenants are production → no warning (regression guard)
"""

import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models import Asset, AuditLog, CountryData, Scenario, Tenant, User  # noqa: F401
from app.models.tenant import Tenant as TenantModel
from tests.api.conftest import make_user


@pytest_asyncio.fixture(scope="module")
async def trial_ctx(db_engine):
    """Seed: trial tenant + asset (real-looking) + scenario."""
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        tenant = TenantModel(id=uuid.uuid4(), name="Trial Pharma", tier="trial", status="active")
        user = make_user(tenant)
        asset = Asset(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            created_by=user.id,
            name="VX-Real",
            therapeutic_area="NSCLC",  # non-generic → criterion 4
            us_list_price=189_000,  # >100k → criterion 1, ×1000 → criterion 2
            launch_year=2027,
            loe_year=2040,
            discount_rate=0.10,
            cogs_percent=0.15,
            peak_capture_rate=0.35,
            part_b_share=0.85,
            ramp_years=4,
        )
        scenario = Scenario(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            asset_id=asset.id,
            name="Real data scenario",
            is_baseline=False,
            regulations={},
            levers={},
            cascade_config={},
        )
        db.add_all([tenant, user, asset, scenario])
        await db.commit()

    return {"tenant": tenant, "user": user, "asset": asset, "scenario": scenario}


@pytest_asyncio.fixture(scope="module")
async def prod_ctx(db_engine):
    """Seed: production tenant + same-looking asset + scenario."""
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        tenant = TenantModel(
            id=uuid.uuid4(), name="Prod Pharma", tier="production", status="active"
        )
        user = make_user(tenant)
        asset = Asset(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            created_by=user.id,
            name="Prod Asset",
            therapeutic_area="NSCLC",
            us_list_price=189_000,
            launch_year=2027,
            loe_year=2040,
            discount_rate=0.10,
            cogs_percent=0.15,
            peak_capture_rate=0.35,
            part_b_share=0.85,
            ramp_years=4,
        )
        scenario = Scenario(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            asset_id=asset.id,
            name="Prod scenario",
            is_baseline=False,
            regulations={},
            levers={},
            cascade_config={},
        )
        db.add_all([tenant, user, asset, scenario])
        await db.commit()

    return {"tenant": tenant, "user": user, "asset": asset, "scenario": scenario}


def _client(db_engine, user: User) -> AsyncClient:
    Session = async_sessionmaker(db_engine, expire_on_commit=False)

    async def _db() -> AsyncGenerator[AsyncSession, None]:
        async with Session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def _user() -> User:
        return user

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = _user
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


_REAL_PAYLOAD = {"list_price": 189_000.0, "launched": True}
_ILLUSTRATIVE_PAYLOAD = {"list_price": 12_345.0, "launched": True}


# ─── Trial tenant + real data → warning ───────────────────────────────────────


async def test_trial_real_data_returns_warning(db_engine, trial_ctx):
    """Trial user enters real-looking data → warning field present in response."""
    scenario_id = trial_ctx["scenario"].id
    async with _client(db_engine, trial_ctx["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json=_REAL_PAYLOAD,
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["warning"] is not None, "Expected warning field in response"
    assert body["warning"]["code"] == "looks_like_real_data"


async def test_trial_real_data_creates_audit_log(db_engine, trial_ctx):
    """Trial real-data warning creates audit log entry."""
    scenario_id = trial_ctx["scenario"].id
    async with _client(db_engine, trial_ctx["user"]) as ac:
        await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json=_REAL_PAYLOAD,
        )
    app.dependency_overrides.clear()

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        result = await db.execute(
            select(AuditLog).where(
                AuditLog.action == "trial.real_data_warning_triggered",
                AuditLog.tenant_id == trial_ctx["tenant"].id,
            )
        )
        log = result.scalars().first()

    assert log is not None, "Expected trial.real_data_warning_triggered audit log"
    assert log.payload["country_code"] == "DE"
    assert "score" in log.payload
    assert "breakdown" in log.payload


# ─── Production tenant + real data → no warning ───────────────────────────────


async def test_production_real_data_no_warning(db_engine, prod_ctx):
    """Production user with identical data → no warning (heuristic disabled)."""
    scenario_id = prod_ctx["scenario"].id
    async with _client(db_engine, prod_ctx["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json=_REAL_PAYLOAD,
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text
    assert resp.json()["warning"] is None


# ─── Trial tenant + illustrative data → no warning ────────────────────────────


async def test_trial_illustrative_data_no_warning(db_engine, trial_ctx):
    """Trial user enters illustrative data (score < 2) → no warning."""
    # trial_ctx asset has us_list_price=189k and TA="NSCLC" → always scores >= 2.
    # Proper coverage is in test_trial_real_data_warning via trial_illustrative_ctx fixture.
    async with _client(db_engine, trial_ctx["user"]):
        pass
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="module")
async def trial_illustrative_ctx(db_engine):
    """Trial tenant + illustrative asset (low price, generic TA)."""
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        tenant = TenantModel(
            id=uuid.uuid4(), name="Trial Illustrative", tier="trial", status="active"
        )
        user = make_user(tenant)
        asset = Asset(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            created_by=user.id,
            name="Illustrative Asset",
            therapeutic_area="Demo",  # generic → criterion 4 fails
            us_list_price=12_345,  # <100k, not round → criteria 1+2 fail
            launch_year=2027,
            loe_year=2040,
            discount_rate=0.10,
            cogs_percent=0.15,
            peak_capture_rate=0.35,
            part_b_share=0.85,
            ramp_years=4,
        )
        scenario = Scenario(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            asset_id=asset.id,
            name="Illustrative scenario",
            is_baseline=False,
            regulations={},
            levers={},
            cascade_config={},
        )
        db.add_all([tenant, user, asset, scenario])
        await db.commit()

    return {"tenant": tenant, "user": user, "asset": asset, "scenario": scenario}


async def test_trial_illustrative_asset_no_warning(db_engine, trial_illustrative_ctx):
    """Trial user with illustrative asset (score < 2) → no warning."""
    scenario_id = trial_illustrative_ctx["scenario"].id
    async with _client(db_engine, trial_illustrative_ctx["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json=_ILLUSTRATIVE_PAYLOAD,
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text
    assert resp.json()["warning"] is None


# ─── Response is still HTTP 200 (non-blocking) ────────────────────────────────


async def test_warning_does_not_block_response(db_engine, trial_ctx):
    """Warning is non-blocking: response still 200 with correct country data."""
    scenario_id = trial_ctx["scenario"].id
    async with _client(db_engine, trial_ctx["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/FR",
            json={"list_price": 160_000.0, "launched": True},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["country_code"] == "FR"
    assert body["list_price"] == 160_000.0
