"""EC-TRIAL-05: API key creation must be blocked for trial tenants."""
import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models import Asset, AuditLog, CountryData, Scenario, SimulationResult, Tenant, User  # noqa: F401
from tests.api.conftest import make_tenant, make_user


@pytest_asyncio.fixture(scope="module")
async def ec_trial05_data(db_engine):
    """Seed trial tenant + admin user."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        trial_tenant = make_tenant("TrialTenant05")  # tier="trial" by default
        trial_admin = make_user(trial_tenant, role="admin")
        db.add_all([trial_tenant, trial_admin])
        await db.commit()

    return {"tenant": trial_tenant, "user": trial_admin}


def _make_client(db_engine, user: User) -> AsyncClient:
    from sqlalchemy.ext.asyncio import async_sessionmaker

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


async def test_trial_admin_cannot_create_api_key(db_engine, ec_trial05_data):
    """Trial admin must get 403 feature_not_in_trial when POSTing to /api-keys."""
    async with _make_client(db_engine, ec_trial05_data["user"]) as ac:
        resp = await ac.post("/v1/api-keys", json={"name": "Trial key attempt"})
    app.dependency_overrides.clear()

    assert resp.status_code == 403, resp.text
    detail = resp.json()["detail"]
    assert detail["code"] == "feature_not_in_trial"
    assert "production" in detail["message"].lower()
