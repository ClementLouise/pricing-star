"""Tests for GET /api/dashboard/recent-activity."""

import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models import (  # noqa: F401 — triggers table registration
    Asset,
    AuditLog,
    Scenario,
    Tenant,
    User,
)
from tests.api.conftest import make_tenant, make_user

_URL = "/api/dashboard/recent-activity"


@pytest_asyncio.fixture(scope="module")
async def dash_data(db_engine):
    """Seed two tenants with users and audit log entries.

    Tenant A: admin + viewer + 30 normal logs + 1 noisy "simulation.computed" log
    Tenant B: admin + 3 normal logs
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        tenant_a = make_tenant("DashTenantA")
        admin_a = make_user(tenant_a, role="admin")
        viewer_a = make_user(tenant_a, role="viewer")

        tenant_b = make_tenant("DashTenantB")
        admin_b = make_user(tenant_b, role="admin")

        now = datetime.now(UTC)

        # 30 normal logs for tenant A, spread over time so ordering is deterministic
        logs_a = [
            AuditLog(
                id=uuid.uuid4(),
                tenant_id=tenant_a.id,
                user_id=admin_a.id,
                action="asset.created",
                payload={"asset_name": f"Drug {i}"},
                created_at=now - timedelta(minutes=i),
            )
            for i in range(30)
        ]
        # Noisy entry (must be excluded from results)
        noisy = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_a.id,
            user_id=admin_a.id,
            action="simulation.computed",
            payload={},
            created_at=now - timedelta(minutes=5),
        )
        # 3 logs for tenant B
        logs_b = [
            AuditLog(
                id=uuid.uuid4(),
                tenant_id=tenant_b.id,
                user_id=admin_b.id,
                action="scenario.created",
                payload={"scenario_name": f"S{i}"},
                created_at=now - timedelta(minutes=i),
            )
            for i in range(3)
        ]

        db.add_all([tenant_a, admin_a, viewer_a, tenant_b, admin_b])
        db.add_all(logs_a + [noisy] + logs_b)
        await db.commit()

    return {
        "tenant_a": tenant_a,
        "admin_a": admin_a,
        "viewer_a": viewer_a,
        "tenant_b": tenant_b,
        "admin_b": admin_b,
    }


def _client_for(db_engine, user: User) -> AsyncClient:
    """Test client that bypasses JWT auth via get_current_user override."""
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


# ─── Test a: returns entries in descending order ──────────────────────────────


async def test_recent_activity_returns_recent_entries(db_engine, dash_data):
    async with _client_for(db_engine, dash_data["admin_a"]) as ac:
        resp = await ac.get(_URL)
    app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text
    items = resp.json()["items"]
    assert len(items) == 20  # default limit, 30 normal logs seeded
    timestamps = [item["created_at"] for item in items]
    assert timestamps == sorted(timestamps, reverse=True), "must be newest-first"


# ─── Test b: noisy actions are excluded ──────────────────────────────────────


async def test_recent_activity_filters_noisy_actions(db_engine, dash_data):
    async with _client_for(db_engine, dash_data["admin_a"]) as ac:
        resp = await ac.get(_URL)
    app.dependency_overrides.clear()

    assert resp.status_code == 200
    actions = {item["action"] for item in resp.json()["items"]}
    assert "simulation.computed" not in actions
    assert "asset.viewed" not in actions
    assert "user.welcome_dismissed" not in actions


# ─── Test c: limit param is respected ────────────────────────────────────────


async def test_recent_activity_respects_limit(db_engine, dash_data):
    async with _client_for(db_engine, dash_data["admin_a"]) as ac:
        resp = await ac.get(f"{_URL}?limit=10")
    app.dependency_overrides.clear()

    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 10


# ─── Test d: tenant isolation — admin_b sees only tenant B entries ────────────


async def test_recent_activity_tenant_isolation(db_engine, dash_data):
    async with _client_for(db_engine, dash_data["admin_b"]) as ac:
        resp = await ac.get(_URL)
    app.dependency_overrides.clear()

    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 3, "tenant B has exactly 3 logs"
    tenant_b_id = str(dash_data["tenant_b"].id)
    # All items belong to tenant B's user (admin_b)
    admin_b_id = str(dash_data["admin_b"].id)
    for item in items:
        assert item["user_id"] == admin_b_id


# ─── Test e: viewer role gets 200, not 403 ────────────────────────────────────


async def test_recent_activity_viewer_can_access(db_engine, dash_data):
    async with _client_for(db_engine, dash_data["viewer_a"]) as ac:
        resp = await ac.get(_URL)
    app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text


# ─── Test f: unauthenticated request returns 4xx ─────────────────────────────


async def test_recent_activity_unauthenticated_returns_4xx():
    # No dependency overrides — HTTPBearer rejects the request before DB access
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get(_URL)

    assert resp.status_code in (401, 403), (
        f"Expected 4xx for unauthenticated request, got {resp.status_code}"
    )
