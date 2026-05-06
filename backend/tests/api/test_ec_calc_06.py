"""EC-CALC-06: zero and negative prices must be rejected at Pydantic validation layer."""
import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models import Asset, AuditLog, CountryData, Scenario, SimulationResult, Tenant, User  # noqa: F401
from tests.api.conftest import make_asset, make_tenant, make_user


@pytest_asyncio.fixture(scope="module")
async def ec06_data(db_engine):
    """Seed tenant + user + asset + scenario for EC-CALC-06 tests."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        tenant = make_tenant("EC06Tenant")
        user = make_user(tenant)
        asset = make_asset(tenant, user)
        scenario = Scenario(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            asset_id=asset.id,
            name="Price validation scenario",
            is_baseline=False,
            regulations={},
            levers={},
            cascade_config={},
        )
        db.add_all([tenant, user, asset, scenario])
        await db.commit()

    return {"tenant": tenant, "user": user, "asset": asset, "scenario": scenario}


def _make_client(db_engine, user: User) -> AsyncClient:
    from sqlalchemy.ext.asyncio import async_sessionmaker

    Session = async_sessionmaker(db_engine, expire_on_commit=False)

    async def _db() -> AsyncGenerator[AsyncSession, None]:
        async with Session() as session:
            yield session

    async def _user() -> User:
        return user

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = _user
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ─── Asset price validation ────────────────────────────────────────────────────

async def test_asset_zero_price_rejected(db_engine, ec06_data):
    """us_list_price = 0 must return 422 (Pydantic gt=0 constraint)."""
    async with _make_client(db_engine, ec06_data["user"]) as ac:
        resp = await ac.post("/api/assets", json={
            "name": "Zero price asset",
            "us_list_price": 0,
        })
    app.dependency_overrides.clear()

    assert resp.status_code == 422, resp.text
    body = resp.json()
    detail_str = str(body).lower()
    assert "greater than 0" in detail_str or "gt" in detail_str or "greater_than" in detail_str


async def test_asset_negative_price_rejected(db_engine, ec06_data):
    """us_list_price = -100 must return 422."""
    async with _make_client(db_engine, ec06_data["user"]) as ac:
        resp = await ac.post("/api/assets", json={
            "name": "Negative price asset",
            "us_list_price": -100,
        })
    app.dependency_overrides.clear()

    assert resp.status_code == 422, resp.text


async def test_asset_valid_price_accepted(db_engine, ec06_data):
    """us_list_price = 100000 must return 201."""
    async with _make_client(db_engine, ec06_data["user"]) as ac:
        resp = await ac.post("/api/assets", json={
            "name": "Valid price asset",
            "us_list_price": 100_000,
        })
    app.dependency_overrides.clear()

    assert resp.status_code == 201, resp.text


# ─── Country data price validation ────────────────────────────────────────────

async def test_country_data_zero_list_price_rejected(db_engine, ec06_data):
    """list_price = 0 on country-data must return 422."""
    scenario_id = ec06_data["scenario"].id

    async with _make_client(db_engine, ec06_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json={"list_price": 0, "launched": True},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 422, resp.text
    body = resp.json()
    detail_str = str(body).lower()
    assert "greater than 0" in detail_str or "gt" in detail_str or "greater_than" in detail_str


async def test_country_data_negative_list_price_rejected(db_engine, ec06_data):
    """list_price = -500 on country-data must return 422."""
    scenario_id = ec06_data["scenario"].id

    async with _make_client(db_engine, ec06_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json={"list_price": -500, "launched": True},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 422, resp.text


async def test_country_data_zero_net_price_rejected(db_engine, ec06_data):
    """net_price = 0 on country-data must return 422."""
    scenario_id = ec06_data["scenario"].id

    async with _make_client(db_engine, ec06_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json={"net_price": 0, "launched": True},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 422, resp.text


async def test_country_data_valid_price_accepted(db_engine, ec06_data):
    """list_price = 100000 on country-data must succeed."""
    scenario_id = ec06_data["scenario"].id

    async with _make_client(db_engine, ec06_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json={"list_price": 100_000, "launched": True},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text
