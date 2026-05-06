"""EC-COMP-03: POST /simulations/{id}/audit-export returns SOX-grade audit JSON."""
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models import Asset, AuditLog, CountryData, Scenario, SimulationResult, Tenant, User  # noqa: F401
from tests.api.conftest import make_asset, make_tenant, make_user


@pytest_asyncio.fixture(scope="module")
async def ec03_audit_data(db_engine):
    """Seed tenant + user + asset + scenario + simulation result."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as db:
        tenant = make_tenant("EC03AuditTenant")
        user = make_user(tenant)
        asset = make_asset(tenant, user)
        scenario = Scenario(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            asset_id=asset.id,
            name="Audit Export Scenario",
            is_baseline=False,
            regulations={"guard": {"active": True}},
            levers={},
            cascade_config={},
        )
        sim = SimulationResult(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            scenario_id=scenario.id,
            computed_by=user.id,
            engine_version="1.7.0",
            computed_at=datetime.now(timezone.utc),
            npv=4_962_668_554.61,
            peak_revenue=800_000_000.0,
            method_i_value=56389.977,
            method_i_anchor="CH",
            method_ii_value=None,
            applicable_benchmark=56389.977,
            per_unit_rebate=33610.023,
            effective_us_net=56389.977,
            cascade_iterations=5,
            cascade_converged=True,
            final_prices={"US": 180000, "DE": 90000, "FR": 77400},
            yearly_breakdown=[
                {
                    "year": 2027, "us_revenue": 50_000_000, "ex_us_revenue": 20_000_000,
                    "total_net": 70_000_000, "discounted": 70_000_000,
                    "rebate_per_unit": 33610.023, "effective_us_net": 56389.977,
                },
                {
                    "year": 2028, "us_revenue": 100_000_000, "ex_us_revenue": 40_000_000,
                    "total_net": 140_000_000, "discounted": 127_272_727,
                    "rebate_per_unit": 33610.023, "effective_us_net": 56389.977,
                },
            ],
            monte_carlo_result=None,
        )
        db.add_all([tenant, user, asset, scenario, sim])
        await db.commit()

    return {"tenant": tenant, "user": user, "asset": asset, "scenario": scenario, "sim": sim}


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


async def test_audit_export_returns_200_with_expected_sections(db_engine, ec03_audit_data):
    """Audit export must return 200 with all required SOX sections."""
    sim_id = ec03_audit_data["sim"].id

    async with _make_client(db_engine, ec03_audit_data["user"]) as ac:
        resp = await ac.post(f"/api/simulations/{sim_id}/audit-export")
    app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text
    doc = resp.json()

    # Required top-level sections
    for section in ("metadata", "asset", "methodology", "inputs", "calculations", "auditTrail"):
        assert section in doc, f"Missing section: {section}"

    # metadata fields
    assert doc["metadata"]["version"] == "1.7.0" or "version" in doc["metadata"]
    assert doc["metadata"]["scenarioName"] == "Audit Export Scenario"

    # methodology must include guard and guard methodI/methodII citations
    assert "guard" in doc["methodology"]
    assert "methodI" in doc["methodology"]["guard"]
    assert "methodII" in doc["methodology"]["guard"]

    # inputs.prices must reflect final_prices
    assert doc["inputs"]["prices"]["US"] == 180000

    # calculations.npv must be present and match stored NPV
    assert doc["calculations"]["npv"] is not None
    assert abs(doc["calculations"]["npv"]["npv"] - 4_962_668_554.61) < 1


async def test_audit_export_content_disposition_header(db_engine, ec03_audit_data):
    """Audit export must include Content-Disposition attachment header."""
    sim_id = ec03_audit_data["sim"].id

    async with _make_client(db_engine, ec03_audit_data["user"]) as ac:
        resp = await ac.post(f"/api/simulations/{sim_id}/audit-export")
    app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text
    cd = resp.headers.get("content-disposition", "")
    assert "attachment" in cd
    assert "pricing-star_audit_" in cd
    assert ".json" in cd


async def test_audit_export_404_unknown_simulation(db_engine, ec03_audit_data):
    """Requesting audit export for unknown simulation_id must return 404."""
    async with _make_client(db_engine, ec03_audit_data["user"]) as ac:
        resp = await ac.post(f"/api/simulations/{uuid.uuid4()}/audit-export")
    app.dependency_overrides.clear()

    assert resp.status_code == 404, resp.text
