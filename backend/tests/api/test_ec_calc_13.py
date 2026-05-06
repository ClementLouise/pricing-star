"""EC-CALC-13: g2n_time_series years must be within asset lifecycle [launch_year, loe_year+5]."""
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
async def ec13_data(db_engine):
    """Seed tenant + user + asset (launch_year=2027, loe_year=2040) + scenario."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        tenant = make_tenant("EC13Tenant")
        user = make_user(tenant)
        asset = make_asset(tenant, user)  # launch_year=2027, loe_year=2040
        scenario = Scenario(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            asset_id=asset.id,
            name="G2N lifecycle test scenario",
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


async def test_g2n_year_before_launch_rejected(db_engine, ec13_data):
    """g2n_time_series year before launch_year (2027) must return 422."""
    scenario_id = ec13_data["scenario"].id

    async with _make_client(db_engine, ec13_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/DE",
            json={"g2n_time_series": {"2025": 0.85}, "launched": True, "list_price": 90000},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 422, resp.text
    assert "2025" in resp.text
    assert "outside asset lifecycle" in resp.text


async def test_g2n_year_after_loe_plus5_rejected(db_engine, ec13_data):
    """g2n_time_series year after loe_year+5 (2045) must return 422."""
    scenario_id = ec13_data["scenario"].id

    async with _make_client(db_engine, ec13_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/FR",
            json={"g2n_time_series": {"2050": 0.80}, "launched": True, "list_price": 78000},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 422, resp.text
    assert "2050" in resp.text


async def test_g2n_year_within_lifecycle_accepted(db_engine, ec13_data):
    """g2n_time_series year within [2027, 2045] must be accepted."""
    scenario_id = ec13_data["scenario"].id

    async with _make_client(db_engine, ec13_data["user"]) as ac:
        resp = await ac.patch(
            f"/api/scenarios/{scenario_id}/country-data/UK",
            json={"g2n_time_series": {"2030": 0.80}, "launched": True, "list_price": 81000},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text


async def test_g2n_lifecycle_enforced_on_scenario_create(db_engine, ec13_data):
    """Creating a scenario with out-of-lifecycle g2n_time_series must return 422."""
    asset_id = ec13_data["asset"].id

    async with _make_client(db_engine, ec13_data["user"]) as ac:
        resp = await ac.post(
            f"/api/assets/{asset_id}/scenarios",
            json={
                "name": "Bad G2N lifecycle",
                "country_data": {
                    "DE": {"g2n_time_series": {"2020": 0.85}, "launched": True, "list_price": 90000},
                },
            },
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 422, resp.text
    assert "2020" in resp.text
