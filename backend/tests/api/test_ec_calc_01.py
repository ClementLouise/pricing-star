"""EC-CALC-01: cascade non-convergence must return HTTP 422 with cascade_did_not_converge."""
import uuid
from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.engine.types import CascadeResult
from app.main import app
from app.models import Asset, AuditLog, CountryData, Scenario, SimulationResult, Tenant, User  # noqa: F401
from tests.api.conftest import make_asset, make_tenant, make_user


@pytest_asyncio.fixture(scope="module")
async def ec01_data(db_engine):
    """Seed one asset + scenario + one launched country for EC-CALC-01 tests."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        tenant = make_tenant("EC01Tenant")
        user = make_user(tenant)
        asset = make_asset(tenant, user)
        scenario = Scenario(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            asset_id=asset.id,
            name="Non-convergence scenario",
            is_baseline=False,
            regulations={},
            levers={},
            cascade_config={"require_convergence": True},
        )
        country = CountryData(
            id=uuid.uuid4(),
            scenario_id=scenario.id,
            tenant_id=tenant.id,
            country_code="DE",
            list_price=90_000.0,
            launched=True,
            withdrawn=False,
            volume=0.10,
        )
        db.add_all([tenant, user, asset, scenario, country])
        await db.commit()

    return {"tenant": tenant, "user": user, "asset": asset, "scenario": scenario}


async def test_cascade_non_convergence_returns_422(db_engine, ec01_data):
    """EC-CALC-01: 422 with cascade_did_not_converge when cascade loop exhausts iterations."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    Session = async_sessionmaker(db_engine, expire_on_commit=False)

    async def _db() -> AsyncGenerator[AsyncSession, None]:
        async with Session() as session:
            yield session

    async def _user() -> User:
        return ec01_data["user"]

    non_converged = CascadeResult(
        final={"DE": 90_000.0, "US": 180_000.0},
        iterations=5,
        history=[],
        converged=False,
    )

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = _user

    try:
        with patch("app.services.simulation.run_cascade", return_value=non_converged):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                resp = await ac.post(f"/api/scenarios/{ec01_data['scenario'].id}/simulate")
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 422, resp.text
    body = resp.json()
    assert body["detail"]["code"] == "cascade_did_not_converge"
    assert "5 iterations" in body["detail"]["message"]
