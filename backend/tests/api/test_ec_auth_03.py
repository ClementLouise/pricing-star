"""EC-AUTH-03: API key revocation — DELETE /v1/api-keys/{id}."""
import uuid
from collections.abc import AsyncGenerator

import bcrypt
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models import ApiKey, AuditLog, Asset, Scenario, SimulationResult, Tenant, User  # noqa: F401
from tests.api.conftest import make_tenant, make_user

# Low bcrypt cost for test speed (production uses 12)
_BCRYPT_ROUNDS = 4

# Unique prefix for this test's API key — avoids collision with other test keys
_TEST_KEY = "ppi_ec03_" + "x" * 20


@pytest_asyncio.fixture(scope="module")
async def ec03_data(db_engine):
    """Seed two tenants, admin + editor users, and one API key."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        tenant = make_tenant("EC03Tenant")
        admin = make_user(tenant, role="admin")
        editor = make_user(tenant, role="editor")

        other_tenant = make_tenant("EC03OtherTenant")
        other_admin = make_user(other_tenant, role="admin")

        key_hash = bcrypt.hashpw(_TEST_KEY.encode(), bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)).decode()
        api_key = ApiKey(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            created_by=admin.id,
            name="EC03 test key",
            key_hash=key_hash,
            key_prefix=_TEST_KEY[:8],
            permissions={},
        )

        db.add_all([tenant, admin, editor, other_tenant, other_admin, api_key])
        await db.commit()

    return {
        "tenant": tenant,
        "admin": admin,
        "editor": editor,
        "other_tenant": other_tenant,
        "other_admin": other_admin,
        "api_key": api_key,
    }


def _client_for(db_engine, user: User) -> AsyncClient:
    """JWT-style test client: bypasses require_auth via get_current_user override."""
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


def _api_key_client(db_engine) -> AsyncClient:
    """Real-auth client: sends API key Bearer token, only overrides get_db."""
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

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides.pop(get_current_user, None)
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {_TEST_KEY}"},
    )


# ─── Test a: admin revokes their own key → 204 ────────────────────────────────

async def test_admin_revokes_own_key(db_engine, ec03_data):
    key_id = ec03_data["api_key"].id

    async with _client_for(db_engine, ec03_data["admin"]) as ac:
        resp = await ac.delete(f"/v1/api-keys/{key_id}")
    app.dependency_overrides.clear()

    assert resp.status_code == 204, resp.text


# ─── Test b: editor cannot revoke → 403 ──────────────────────────────────────

async def test_editor_cannot_revoke(db_engine, ec03_data):
    # Use a fresh key so it's not already revoked from test (a)
    from sqlalchemy.ext.asyncio import async_sessionmaker

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        fresh_key = ApiKey(
            id=uuid.uuid4(),
            tenant_id=ec03_data["tenant"].id,
            created_by=ec03_data["admin"].id,
            name="Editor target key",
            key_hash="dummy_hash_editor",
            key_prefix="ppi_edtr",
            permissions={},
        )
        db.add(fresh_key)
        await db.commit()

    async with _client_for(db_engine, ec03_data["editor"]) as ac:
        resp = await ac.delete(f"/v1/api-keys/{fresh_key.id}")
    app.dependency_overrides.clear()

    assert resp.status_code == 403, resp.text


# ─── Test c: cross-tenant → 404 ──────────────────────────────────────────────

async def test_cross_tenant_returns_404(db_engine, ec03_data):
    # other_admin tries to revoke a key belonging to tenant (not other_tenant)
    key_id = ec03_data["api_key"].id

    async with _client_for(db_engine, ec03_data["other_admin"]) as ac:
        resp = await ac.delete(f"/v1/api-keys/{key_id}")
    app.dependency_overrides.clear()

    assert resp.status_code == 404, resp.text


# ─── Test d: already-revoked key → 200 idempotent ────────────────────────────

async def test_revoke_already_revoked_is_idempotent(db_engine, ec03_data):
    # The key was revoked in test (a); revoking again should return 200
    key_id = ec03_data["api_key"].id

    async with _client_for(db_engine, ec03_data["admin"]) as ac:
        resp = await ac.delete(f"/v1/api-keys/{key_id}")
    app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text


# ─── Test e: revoked key returns 401 on auth ─────────────────────────────────

async def test_revoked_key_auth_returns_401(db_engine, ec03_data):
    # The key was revoked in test (a). A request using it should return 401.
    async with _api_key_client(db_engine) as ac:
        resp = await ac.get("/api/me")
    app.dependency_overrides.clear()

    assert resp.status_code == 401, resp.text
    assert "revoked" in resp.json()["detail"].lower()


# ─── Test f: GET /api-keys shows revoked key with revoked_at set ──────────────

async def test_list_shows_revoked_key(db_engine, ec03_data):
    key_id = ec03_data["api_key"].id

    async with _client_for(db_engine, ec03_data["admin"]) as ac:
        resp = await ac.get("/v1/api-keys")
    app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text
    keys = resp.json()
    match = next((k for k in keys if k["id"] == str(key_id)), None)
    assert match is not None, "Revoked key should still appear in list"
    assert match["revoked_at"] is not None, "revoked_at must be set"
