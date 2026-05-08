"""Audit Pack download endpoints — simulation-level and asset-level ZIP exports."""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_role
from app.database import get_db
from app.engine.audit import generate_audit_json
from app.engine.types import NPVResult, YearlyBreakdown
from app.models.user import User
from app.repos.asset import AssetRepo
from app.repos.audit import AuditRepo
from app.repos.scenario import CountryDataRepo, ScenarioRepo
from app.repos.simulation_result import SimulationResultRepo
from app.services.audit_pack import (
    ExportTooLargeError,
    build_asset_pack,
    build_simulation_pack,
)

router = APIRouter(tags=["audit"])

_viewer = require_role(["admin", "editor", "viewer"])


def _sim_to_dict(sim: object) -> dict:
    """Flatten a SimulationResult ORM object to a plain dict for the service layer."""
    return {
        "simulation_id": str(sim.id),  # type: ignore[attr-defined]
        "engine_version": sim.engine_version,  # type: ignore[attr-defined]
        "computed_at": sim.computed_at.isoformat(),  # type: ignore[attr-defined]
        "npv": float(sim.npv),  # type: ignore[attr-defined]
        "peak_revenue": float(sim.peak_revenue) if sim.peak_revenue is not None else None,  # type: ignore[attr-defined]
        "method_i_value": float(sim.method_i_value) if sim.method_i_value is not None else None,  # type: ignore[attr-defined]
        "method_i_anchor": sim.method_i_anchor,  # type: ignore[attr-defined]
        "method_ii_value": float(sim.method_ii_value) if sim.method_ii_value is not None else None,  # type: ignore[attr-defined]
        "applicable_benchmark": (  # type: ignore[attr-defined]
            float(sim.applicable_benchmark) if sim.applicable_benchmark is not None else None
        ),
        "per_unit_rebate": (  # type: ignore[attr-defined]
            float(sim.per_unit_rebate) if sim.per_unit_rebate is not None else None
        ),
        "effective_us_net": (  # type: ignore[attr-defined]
            float(sim.effective_us_net) if sim.effective_us_net is not None else None
        ),
        "cascade_iterations": sim.cascade_iterations,  # type: ignore[attr-defined]
        "cascade_converged": sim.cascade_converged,  # type: ignore[attr-defined]
        "final_prices": sim.final_prices or {},  # type: ignore[attr-defined]
        "yearly_breakdown": sim.yearly_breakdown or [],  # type: ignore[attr-defined]
    }


def _asset_to_dict(asset: object) -> dict:
    return {
        "name": asset.name,  # type: ignore[attr-defined]
        "therapeutic_area": asset.therapeutic_area,  # type: ignore[attr-defined]
        "modality": asset.modality,  # type: ignore[attr-defined]
        "launch_year": asset.launch_year,  # type: ignore[attr-defined]
        "patent_expiry": asset.loe_year,  # type: ignore[attr-defined]
        "discount_rate": float(asset.discount_rate) if asset.discount_rate is not None else None,  # type: ignore[attr-defined]
    }


def _asset_to_meta(asset: object) -> dict:
    """Full asset dict keyed by OVERVIEW_KEYS — used for asset_full.xlsx export."""
    a = asset  # type: ignore[attr-defined]
    return {
        "asset_id": str(a.id),
        "updated_at": a.updated_at.isoformat(),
        "name": a.name,
        "therapeutic_area": a.therapeutic_area,
        "modality": a.modality,
        "indication": a.indication,
        "us_list_price": float(a.us_list_price) if a.us_list_price is not None else None,
        "us_net_share": float(a.us_net_share) if a.us_net_share is not None else None,
        "launch_year": a.launch_year,
        "peak_year": a.peak_year,
        "loe_year": a.loe_year,
        "cogs_percent": float(a.cogs_percent),
        "discount_rate": float(a.discount_rate),
        "us_patient_population": a.us_patient_population,
        "ex_us_patient_population": a.ex_us_patient_population,
        "peak_capture_rate": float(a.peak_capture_rate),
        "part_b_share": float(a.part_b_share),
        "ramp_years": a.ramp_years,
    }


def _scenario_to_config(scenario: object, country_data_rows: list) -> dict:
    s = scenario  # type: ignore[attr-defined]
    return {
        "name": s.name,
        "description": s.description,
        "is_baseline": s.is_baseline,
        "regulations": s.regulations,
        "levers": s.levers,
        "cascade_config": s.cascade_config,
        "country_data": [
            {
                "country_code": cd.country_code,
                "list_price": float(cd.list_price) if cd.list_price is not None else None,
                "net_price": float(cd.net_price) if cd.net_price is not None else None,
                "volume": float(cd.volume) if cd.volume is not None else None,
                "launched": cd.launched,
                "launch_year": cd.launch_year,
                "withdrawn": cd.withdrawn,
                "g2n_ratio": float(cd.g2n_ratio) if cd.g2n_ratio is not None else None,
                "g2n_time_series": cd.g2n_time_series,
            }
            for cd in country_data_rows
        ],
    }


def _build_audit_json_for_sim(
    asset_dict: dict, scenario: object, sim: object, user_id: str
) -> dict:
    npv_result = NPVResult(
        npv=float(sim.npv),  # type: ignore[attr-defined]
        peak_revenue=float(sim.peak_revenue) if sim.peak_revenue is not None else 0.0,  # type: ignore[attr-defined]
        yearly_breakdown=[
            YearlyBreakdown(
                year=row["year"],
                us_revenue=row["us_revenue"],
                ex_us_revenue=row["ex_us_revenue"],
                total_revenue=row.get("total_net", row["us_revenue"] + row["ex_us_revenue"]),
                g2n_used={},
                rebate_per_unit=row.get("rebate_per_unit", 0.0),
                effective_us_net=row.get("effective_us_net", 0.0),
            )
            for row in (sim.yearly_breakdown or [])  # type: ignore[attr-defined]
        ],
    )
    return generate_audit_json(
        asset=asset_dict,
        scenario=scenario.name if scenario else None,  # type: ignore[attr-defined]
        prices=sim.final_prices or {},  # type: ignore[attr-defined]
        regulations=scenario.regulations if scenario else {},  # type: ignore[attr-defined]
        npv_result=npv_result,
        anchor_analysis=None,
        generated_by=user_id,
    )


@router.get("/simulations/{simulation_id}/audit-pack")
async def simulation_audit_pack(
    simulation_id: uuid.UUID,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download a ZIP audit pack (audit.json + prices.xlsx + README) for one simulation."""
    sim = await SimulationResultRepo(db).get(simulation_id, user.tenant_id)
    if sim is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found")

    scenario = await ScenarioRepo(db).get(sim.scenario_id, user.tenant_id)
    asset = await AssetRepo(db).get(scenario.asset_id, user.tenant_id) if scenario else None

    asset_dict = _asset_to_dict(asset) if asset else {"name": "unknown"}
    scenario_name = scenario.name if scenario else "unknown"
    sim_dict = _sim_to_dict(sim)
    audit_json = _build_audit_json_for_sim(asset_dict, scenario, sim, str(user.id))

    try:
        pack_bytes = build_simulation_pack(
            asset=asset_dict,
            scenario_name=scenario_name,
            sim=sim_dict,
            audit_json=audit_json,
            generated_by=str(user.id),
        )
    except ExportTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(exc)
        ) from exc

    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="simulation.audit_pack_downloaded",
        payload={"simulation_id": str(simulation_id)},
    )
    await db.commit()

    asset_slug = (asset.name if asset else "unknown").replace(" ", "_")
    filename = f"pricing-star_audit_{asset_slug}_{date.today().isoformat()}.zip"
    return Response(
        content=pack_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/assets/{asset_id}/audit-pack")
async def asset_audit_pack(
    asset_id: uuid.UUID,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download a ZIP audit pack for all simulations of an asset."""
    asset = await AssetRepo(db).get(asset_id, user.tenant_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    scenarios = await ScenarioRepo(db).list(asset_id, user.tenant_id)
    sim_repo = SimulationResultRepo(db)
    cd_repo = CountryDataRepo(db)
    asset_dict = _asset_to_dict(asset)
    asset_meta = _asset_to_meta(asset)

    packs: list[dict] = []
    scenario_configs: list[dict] = []

    for scenario in scenarios:
        # Build scenario config (all scenarios, including those without simulations)
        cd_rows = await cd_repo.list_for_scenario(scenario.id)
        scenario_configs.append(_scenario_to_config(scenario, cd_rows))

        # Simulation packs (only scenarios with at least one simulation)
        latest_sims = await sim_repo.list_for_scenario(scenario.id, user.tenant_id, limit=1)
        if not latest_sims:
            continue
        sim = latest_sims[0]
        sim_dict = _sim_to_dict(sim)
        audit_json = _build_audit_json_for_sim(asset_dict, scenario, sim, str(user.id))
        packs.append({"scenario_name": scenario.name, "sim": sim_dict, "audit_json": audit_json})

    if not packs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No simulations found for this asset",
        )

    try:
        pack_bytes = build_asset_pack(
            asset=asset_dict,
            packs=packs,
            generated_by=str(user.id),
            asset_meta=asset_meta,
            scenario_configs=scenario_configs,
        )
    except ExportTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(exc)
        ) from exc

    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="asset.audit_pack_downloaded",
        payload={"asset_id": str(asset_id), "simulation_count": len(packs)},
    )
    await db.commit()

    asset_slug = asset.name.replace(" ", "_")
    filename = f"pricing-star_asset_{asset_slug}_{date.today().isoformat()}.zip"
    return Response(
        content=pack_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
