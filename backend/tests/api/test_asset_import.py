"""API integration tests for the bulk XLSX import endpoints.

Covers:
  GET  /api/import/template
  POST /api/import/dry-run
  POST /api/import/execute
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.auth import TenantContext, get_current_user, require_auth
from app.database import get_db
from app.main import app
from app.models import Asset, AuditLog, Tenant, User  # noqa: F401
from app.models.tenant import Tenant as TenantModel
from app.services.asset_import import build_import_template
from tests.api.conftest import make_user

_XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="module")
async def import_ctx(db_engine):
    """Seed: one production tenant + one admin user."""
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        tenant = TenantModel(
            id=uuid.uuid4(), name="ImportTestTenant",
            tier="production", status="active",
        )
        user = make_user(tenant, role="admin")
        db.add_all([tenant, user])
        await db.commit()
    return {"tenant": tenant, "user": user}


def _client(db_engine, user: User, tenant_tier: str = "production") -> AsyncClient:
    """Return a test AsyncClient with auth + DB overridden."""
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

    async def _ctx() -> TenantContext:
        return TenantContext(
            tenant_id=user.tenant_id,
            tenant_tier=tenant_tier,
            trial_expires_at=None,
            auth0_user_id=f"test|{user.id}",
        )

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = _user
    app.dependency_overrides[require_auth] = _ctx
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ── Template endpoint ─────────────────────────────────────────────────────────

async def test_template_returns_xlsx(db_engine, import_ctx):
    """GET /api/import/template returns 200 with xlsx content-type."""
    async with _client(db_engine, import_ctx["user"]) as ac:
        resp = await ac.get("/api/import/template?asset_name=My+Test")
    app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text
    assert "spreadsheetml" in resp.headers["content-type"]
    assert resp.headers["content-disposition"].startswith("attachment")
    assert len(resp.content) > 1000  # non-empty XLSX


# ── Dry-run endpoint ──────────────────────────────────────────────────────────

async def test_dry_run_valid_file_returns_valid_true(db_engine, import_ctx):
    """Valid template XLSX → dry-run returns valid=true with no errors."""
    xlsx = build_import_template("Dry Run Drug")
    async with _client(db_engine, import_ctx["user"]) as ac:
        resp = await ac.post(
            "/api/import/dry-run",
            data={"mode": "create_new"},
            files={"file": ("test.xlsx", xlsx, _XLSX_MIME)},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["valid"] is True
    assert body["errors"] == []
    assert body["summary"]["scenario_count"] == 1


async def test_dry_run_invalid_bytes_returns_valid_false(db_engine, import_ctx):
    """Non-XLSX bytes → dry-run returns valid=false with INVALID_XLSX error."""
    async with _client(db_engine, import_ctx["user"]) as ac:
        resp = await ac.post(
            "/api/import/dry-run",
            data={"mode": "create_new"},
            files={"file": ("bad.xlsx", b"garbage bytes", _XLSX_MIME)},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["valid"] is False
    assert any(e["code"] == "INVALID_XLSX" for e in body["errors"])


async def test_dry_run_oversized_file_returns_413(db_engine, import_ctx):
    """File > 10 MB → 413 response."""
    big_content = b"x" * (10 * 1024 * 1024 + 1)
    async with _client(db_engine, import_ctx["user"]) as ac:
        resp = await ac.post(
            "/api/import/dry-run",
            data={"mode": "create_new"},
            files={"file": ("big.xlsx", big_content, _XLSX_MIME)},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 413, resp.text


# ── Execute endpoint ──────────────────────────────────────────────────────────

async def test_execute_without_confirmed_returns_400(db_engine, import_ctx):
    """confirmed=false (default) → 400 without touching the DB."""
    xlsx = build_import_template("Not Confirmed")
    async with _client(db_engine, import_ctx["user"]) as ac:
        resp = await ac.post(
            "/api/import/execute",
            data={"mode": "create_new", "confirmed": "false"},
            files={"file": ("test.xlsx", xlsx, _XLSX_MIME)},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 400, resp.text


async def test_execute_valid_file_creates_asset_in_db(db_engine, import_ctx):
    """Valid XLSX + confirmed=true → 201 + asset row exists in DB."""
    user = import_ctx["user"]
    xlsx = build_import_template("Imported Drug")

    async with _client(db_engine, user) as ac:
        resp = await ac.post(
            "/api/import/execute",
            data={"mode": "create_new", "confirmed": "true"},
            files={"file": ("test.xlsx", xlsx, _XLSX_MIME)},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 201, resp.text
    body = resp.json()
    asset_id = uuid.UUID(body["asset_id"])
    assert len(body["scenario_ids"]) == 1

    # Verify the asset exists in the DB
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        asset = await db.get(Asset, asset_id)
    assert asset is not None
    assert asset.name == "Imported Drug"
    assert asset.tenant_id == user.tenant_id


async def test_execute_validation_errors_return_422(db_engine, import_ctx):
    """Confirmed=true but file has errors → 422 with error list (no DB write)."""
    async with _client(db_engine, import_ctx["user"]) as ac:
        resp = await ac.post(
            "/api/import/execute",
            data={"mode": "create_new", "confirmed": "true"},
            files={"file": ("bad.xlsx", b"not valid xlsx", _XLSX_MIME)},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 422, resp.text
    detail = resp.json()["detail"]
    assert any(e["code"] == "INVALID_XLSX" for e in detail["errors"])
