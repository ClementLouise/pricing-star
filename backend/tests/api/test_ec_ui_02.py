"""EC-UI-02: Optimistic concurrency control on PATCH endpoints.

Scenarios tested per entity (Asset, Scenario, CountryData):
  a) correct expected_updated_at → 200
  b) stale expected_updated_at → 409
  c) stale + force_override=True → 200 + audit log
  d) absent expected_updated_at → 200 (backward compat)
"""
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models import Asset, AuditLog, CountryData, Scenario, Tenant, User  # noqa: F401 — table registration
from tests.api.conftest import make_asset, make_tenant, make_user

_STALE_TS = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()


@pytest_asyncio.fixture(scope="module")
async def occ_data(db_engine):
    """Seed tenant + user + asset + scenario + country_data (DE) for OCC tests."""
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        tenant = make_tenant("OCC Tenant")
        user = make_user(tenant)
        asset = make_asset(tenant, user)
        scenario = Scenario(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            asset_id=asset.id,
            name="OCC Scenario",
            is_baseline=False,
            regulations={},
            levers={},
            cascade_config={},
        )
        cd = CountryData(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            scenario_id=scenario.id,
            country_code="DE",
            list_price=90000.0,
            launched=True,
            updated_at=datetime.now(timezone.utc),
        )
        db.add_all([tenant, user, asset, scenario, cd])
        await db.commit()
        await db.refresh(asset)
        await db.refresh(scenario)
        await db.refresh(cd)

    return {"tenant": tenant, "user": user, "asset": asset, "scenario": scenario, "cd": cd}


def _client(db_engine, user: User) -> AsyncClient:
    Session = async_sessionmaker(db_engine, expire_on_commit=False)

    async def _db() -> AsyncGenerator[AsyncSession, None]:
        async with Session() as session:
            try:
                yield session
                await session.commit()  # match real get_db() so DB writes are visible cross-session
            except Exception:
                await session.rollback()
                raise

    async def _user() -> User:
        return user

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = _user
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def _current_updated_at(db_engine, model_cls, row_id: uuid.UUID) -> str:
    """Fetch fresh updated_at from DB to avoid stale in-memory object."""
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        result = await db.execute(select(model_cls).where(model_cls.id == row_id))
        row = result.scalar_one()
        return row.updated_at.isoformat()


# ─── Scenario ─────────────────────────────────────────────────────────────────

async def test_scenario_correct_ts_returns_200(db_engine, occ_data):
    """(a) PATCH /scenarios/{id} with matching expected_updated_at → 200."""
    scenario = occ_data["scenario"]
    ts = await _current_updated_at(db_engine, Scenario, scenario.id)
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario.id}",
            json={"name": "OCC OK", "expected_updated_at": ts},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text
    assert resp.json()["name"] == "OCC OK"


async def test_scenario_stale_ts_returns_409(db_engine, occ_data):
    """(b) PATCH /scenarios/{id} with stale expected_updated_at → 409."""
    scenario = occ_data["scenario"]
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario.id}",
            json={"name": "Should fail", "expected_updated_at": _STALE_TS},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 409, resp.text
    assert "Conflict" in resp.json()["detail"]


async def test_scenario_no_ts_returns_200(db_engine, occ_data):
    """(d) PATCH /scenarios/{id} without expected_updated_at → 200 (backward compat)."""
    scenario = occ_data["scenario"]
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario.id}",
            json={"description": "no occ field"},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text


async def test_scenario_force_override_returns_200_and_audit_log(db_engine, occ_data):
    """(c) PATCH /scenarios/{id} stale + force_override=True → 200 + audit log entry."""
    scenario = occ_data["scenario"]
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario.id}",
            json={"name": "Force Write", "expected_updated_at": _STALE_TS, "force_override": True},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text
    assert resp.json()["name"] == "Force Write"

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        result = await db.execute(
            select(AuditLog).where(
                AuditLog.action == "scenario.force_overwrite_conflict",
                AuditLog.tenant_id == occ_data["tenant"].id,
            )
        )
        log = result.scalar_one_or_none()

    assert log is not None, "Expected force_overwrite_conflict audit log entry"
    assert log.payload["scenario_id"] == str(scenario.id)
    assert "before_state" in log.payload
    assert "after_state" in log.payload


# ─── Asset ────────────────────────────────────────────────────────────────────

async def test_asset_correct_ts_returns_200(db_engine, occ_data):
    """(a) PATCH /assets/{id} with matching expected_updated_at → 200."""
    asset = occ_data["asset"]
    ts = await _current_updated_at(db_engine, Asset, asset.id)
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/assets/{asset.id}",
            json={"therapeutic_area": "Oncology", "expected_updated_at": ts},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text


async def test_asset_stale_ts_returns_409(db_engine, occ_data):
    """(b) PATCH /assets/{id} with stale expected_updated_at → 409."""
    asset = occ_data["asset"]
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/assets/{asset.id}",
            json={"name": "Fail", "expected_updated_at": _STALE_TS},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 409, resp.text


async def test_asset_no_ts_returns_200(db_engine, occ_data):
    """(d) PATCH /assets/{id} without expected_updated_at → 200 (backward compat)."""
    asset = occ_data["asset"]
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/assets/{asset.id}",
            json={"modality": "small molecule"},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text


async def test_asset_force_override_returns_200_and_audit_log(db_engine, occ_data):
    """(c) PATCH /assets/{id} stale + force_override=True → 200 + audit log entry."""
    asset = occ_data["asset"]
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/assets/{asset.id}",
            json={"name": "Force Asset", "expected_updated_at": _STALE_TS, "force_override": True},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        result = await db.execute(
            select(AuditLog).where(
                AuditLog.action == "asset.force_overwrite_conflict",
                AuditLog.tenant_id == occ_data["tenant"].id,
            )
        )
        log = result.scalar_one_or_none()

    assert log is not None, "Expected force_overwrite_conflict audit log entry"
    assert log.payload["asset_id"] == str(asset.id)
    assert "before_state" in log.payload
    assert "after_state" in log.payload


# ─── CountryData ──────────────────────────────────────────────────────────────

async def _current_cd_updated_at(db_engine, scenario_id: uuid.UUID, country_code: str) -> str:
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        result = await db.execute(
            select(CountryData).where(
                CountryData.scenario_id == scenario_id,
                CountryData.country_code == country_code,
            )
        )
        cd = result.scalar_one()
        return cd.updated_at.isoformat()


async def test_country_data_correct_ts_returns_200(db_engine, occ_data):
    """(a) PATCH country-data with matching expected_updated_at → 200."""
    scenario_id = occ_data["scenario"].id
    ts = await _current_cd_updated_at(db_engine, scenario_id, "DE")
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json={"list_price": 95000.0, "launched": True, "expected_updated_at": ts},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text


async def test_country_data_stale_ts_returns_409(db_engine, occ_data):
    """(b) PATCH country-data with stale expected_updated_at → 409."""
    scenario_id = occ_data["scenario"].id
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json={"list_price": 99999.0, "launched": True, "expected_updated_at": _STALE_TS},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 409, resp.text


async def test_country_data_no_ts_returns_200(db_engine, occ_data):
    """(d) PATCH country-data without expected_updated_at → 200 (backward compat)."""
    scenario_id = occ_data["scenario"].id
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json={"list_price": 91000.0, "launched": True},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text


async def test_country_data_new_country_no_conflict(db_engine, occ_data):
    """New country code (INSERT path) → 200 regardless of expected_updated_at."""
    scenario_id = occ_data["scenario"].id
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/FR",
            json={"list_price": 78000.0, "launched": True},
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text
    assert "updated_at" in resp.json()


async def test_country_data_force_override_returns_200_and_audit_log(db_engine, occ_data):
    """(c) PATCH country-data stale + force_override=True → 200 + audit log entry."""
    scenario_id = occ_data["scenario"].id
    async with _client(db_engine, occ_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json={
                "list_price": 100000.0,
                "launched": True,
                "expected_updated_at": _STALE_TS,
                "force_override": True,
            },
        )
    app.dependency_overrides.clear()
    assert resp.status_code == 200, resp.text

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        result = await db.execute(
            select(AuditLog).where(
                AuditLog.action == "country_data.force_overwrite_conflict",
                AuditLog.tenant_id == occ_data["tenant"].id,
            )
        )
        log = result.scalar_one_or_none()

    assert log is not None, "Expected force_overwrite_conflict audit log entry"
    assert log.payload["scenario_id"] == str(scenario_id)
    assert log.payload["country_code"] == "DE"
    assert "before_state" in log.payload
    assert "after_state" in log.payload
