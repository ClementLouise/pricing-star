"""EC-TRIAL-08: duplicate trial signup with same auth0_user_id must return 409."""
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.main import app
from app.models import Asset, AuditLog, CountryData, Scenario, SimulationResult, Tenant, User  # noqa: F401

WEBHOOK_SECRET = "test-webhook-secret"
WEBHOOK_HEADERS = {"x-webhook-secret": WEBHOOK_SECRET}

SIGNUP_PAYLOAD = {
    "auth0_user_id": "auth0|ec08_duplicate_test",
    "email": "dup@example.com",
    "name": "Dup User",
    "registered_at": "2026-05-06T10:00:00Z",
}


@pytest_asyncio.fixture(scope="module")
async def ec_trial08_db(db_engine):
    """Yield a sessionmaker bound to the shared in-memory DB."""
    from sqlalchemy.ext.asyncio import async_sessionmaker
    return async_sessionmaker(db_engine, expire_on_commit=False)


def _make_webhook_client(Session) -> AsyncClient:
    async def _db() -> AsyncGenerator[AsyncSession, None]:
        async with Session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _db
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_duplicate_signup_returns_409(db_engine, ec_trial08_db):
    """Second signup with same auth0_user_id on an active trial must return 409."""
    with (
        patch("app.config.settings.webhook_secret", WEBHOOK_SECRET),
        patch("app.services.trial.set_user_tenant_metadata", new=AsyncMock()),
    ):
        # First signup — must succeed (204)
        async with _make_webhook_client(ec_trial08_db) as ac:
            resp1 = await ac.post(
                "/internal/webhooks/auth0/post-registration",
                json=SIGNUP_PAYLOAD,
                headers=WEBHOOK_HEADERS,
            )
        app.dependency_overrides.clear()
        assert resp1.status_code == 204, f"First signup failed: {resp1.text}"

        # Second signup with same auth0_user_id — must return 409
        async with _make_webhook_client(ec_trial08_db) as ac:
            resp2 = await ac.post(
                "/internal/webhooks/auth0/post-registration",
                json=SIGNUP_PAYLOAD,
                headers=WEBHOOK_HEADERS,
            )
        app.dependency_overrides.clear()

    assert resp2.status_code == 409, f"Expected 409 on duplicate, got {resp2.status_code}: {resp2.text}"
    assert "already exists" in resp2.text.lower() or "sign in" in resp2.text.lower()
