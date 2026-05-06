"""
Tenant isolation tests — DEPLOYMENT GATE.
User A cannot access Tenant B's assets/scenarios via any endpoint.
Failures block merge per PRD §08 and §11.
"""
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import Base, get_db
from app.main import app
from app.models import Asset, Scenario, Tenant, User  # noqa: F401 — registers tables
from tests.api.conftest import make_asset, make_tenant, make_user


@pytest_asyncio.fixture
async def ctx(db_session: AsyncSession) -> dict:
    """Two isolated tenants each with a user and an asset."""
    tenant_a = make_tenant("Acme Pharma")
    tenant_b = make_tenant("Rival Pharma")
    db_session.add_all([tenant_a, tenant_b])
    await db_session.flush()

    user_a = make_user(tenant_a, role="admin")
    user_b = make_user(tenant_b, role="admin")
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    asset_a = make_asset(tenant_a, user_a)
    asset_b = make_asset(tenant_b, user_b)
    db_session.add_all([asset_a, asset_b])
    await db_session.flush()

    return {
        "tenant_a": tenant_a, "user_a": user_a, "asset_a": asset_a,
        "tenant_b": tenant_b, "user_b": user_b, "asset_b": asset_b,
    }


def _make_client(db_session: AsyncSession, user: User) -> AsyncClient:
    """Build test client with user + DB overrides (no JWT needed)."""
    async def _db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    async def _user() -> User:
        return user

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = _user
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_user_a_cannot_read_tenant_b_asset(db_session: AsyncSession, ctx: dict) -> None:
    """PRD §08: cross-tenant GET returns 404, not 200 or 403."""
    try:
        async with _make_client(db_session, ctx["user_a"]) as ac:
            resp = await ac.get(f"/api/assets/{ctx['asset_b'].id}")
        assert resp.status_code == 404, (
            f"Expected 404 for cross-tenant access, got {resp.status_code}: {resp.text}"
        )
    finally:
        app.dependency_overrides.clear()


async def test_user_b_cannot_read_tenant_a_asset(db_session: AsyncSession, ctx: dict) -> None:
    """Mirror test: Tenant B cannot access Tenant A's data."""
    try:
        async with _make_client(db_session, ctx["user_b"]) as ac:
            resp = await ac.get(f"/api/assets/{ctx['asset_a'].id}")
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()


async def test_user_a_can_read_own_asset(db_session: AsyncSession, ctx: dict) -> None:
    """Sanity: Tenant A CAN read its own asset (returns 200)."""
    try:
        async with _make_client(db_session, ctx["user_a"]) as ac:
            resp = await ac.get(f"/api/assets/{ctx['asset_a'].id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(ctx["asset_a"].id)
    finally:
        app.dependency_overrides.clear()


async def test_list_assets_only_returns_own_tenant(db_session: AsyncSession, ctx: dict) -> None:
    """GET /assets list must not leak cross-tenant assets."""
    try:
        async with _make_client(db_session, ctx["user_a"]) as ac:
            resp = await ac.get("/api/assets")
        assert resp.status_code == 200
        ids = [item["id"] for item in resp.json()["items"]]
        assert str(ctx["asset_a"].id) in ids, "Own asset must appear in list"
        assert str(ctx["asset_b"].id) not in ids, "Cross-tenant asset must not appear in list"
    finally:
        app.dependency_overrides.clear()


async def test_viewer_cannot_create_asset(db_session: AsyncSession, ctx: dict) -> None:
    """PRD §08 permission matrix: viewer role cannot create assets."""
    viewer = make_user(ctx["tenant_a"], role="viewer")
    db_session.add(viewer)
    await db_session.flush()

    try:
        async with _make_client(db_session, viewer) as ac:
            resp = await ac.post("/api/assets", json={"name": "Hacked Asset"})
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


async def test_user_a_cannot_update_tenant_b_asset(db_session: AsyncSession, ctx: dict) -> None:
    """PATCH on another tenant's asset returns 404."""
    try:
        async with _make_client(db_session, ctx["user_a"]) as ac:
            resp = await ac.patch(
                f"/api/assets/{ctx['asset_b'].id}",
                json={"name": "Hacked"},
            )
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()


async def test_user_a_cannot_delete_tenant_b_asset(db_session: AsyncSession, ctx: dict) -> None:
    """DELETE on another tenant's asset returns 404."""
    try:
        async with _make_client(db_session, ctx["user_a"]) as ac:
            resp = await ac.delete(f"/api/assets/{ctx['asset_b'].id}")
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()
