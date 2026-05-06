"""
Test fixtures for API tenant-isolation tests.
Uses SQLite in-memory DB (no PostgreSQL required) via aiosqlite.
"""
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models import Asset, AuditLog, Scenario, Tenant, User  # noqa: F401 — triggers table registration

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="module")
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with DB session override."""
    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ─── Test data helpers ────────────────────────────��──────────────────────────

def make_tenant(name: str = "Tenant A") -> Tenant:
    return Tenant(id=uuid.uuid4(), name=name, tier="trial", status="active")


def make_user(tenant: Tenant, role: str = "admin") -> User:
    return User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        auth0_user_id=f"auth0|{uuid.uuid4().hex}",
        email_masked="t***@test.com",
        name="Test User",
        role=role,
    )


def make_asset(tenant: Tenant, user: User) -> Asset:
    return Asset(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        created_by=user.id,
        name="Test Asset",
        us_list_price=180000,
        us_net_share=0.50,
        launch_year=2027,
        loe_year=2040,
        discount_rate=0.10,
        cogs_percent=0.15,
        peak_capture_rate=0.35,
        part_b_share=0.85,
        ramp_years=4,
    )
