"""
GDPR Article 20 data portability endpoints.

  GET /export/my-data      — full tenant data export (any authenticated user)
  GET /export/tenant-pack  — same, admin-only, includes all users list
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_role
from app.database import get_db
from app.models.user import User
from app.repos.api_key import ApiKeyRepo
from app.repos.asset import AssetRepo
from app.repos.audit import AuditRepo
from app.repos.scenario import ScenarioRepo
from app.repos.simulation_result import SimulationResultRepo
from app.repos.tenant import TenantRepo
from app.repos.user import UserRepo
from app.services.audit_pack import ExportTooLargeError, build_gdpr_export
from fastapi import HTTPException, status

router = APIRouter(prefix="/export", tags=["export"])

_admin = require_role(["admin"])


def _user_to_dict(u: object) -> dict:
    return {
        "id": str(u.id),  # type: ignore[attr-defined]
        "name": u.name,  # type: ignore[attr-defined]
        "email_masked": u.email_masked,  # type: ignore[attr-defined]
        "role": u.role,  # type: ignore[attr-defined]
        "has_seen_welcome": u.has_seen_welcome,  # type: ignore[attr-defined]
        "created_at": u.created_at.isoformat(),  # type: ignore[attr-defined]
    }


def _tenant_to_dict(t: object) -> dict:
    return {
        "id": str(t.id),  # type: ignore[attr-defined]
        "name": t.name,  # type: ignore[attr-defined]
        "tier": t.tier,  # type: ignore[attr-defined]
        "status": t.status,  # type: ignore[attr-defined]
        "trial_expires_at": t.trial_expires_at.isoformat() if t.trial_expires_at else None,  # type: ignore[attr-defined]
        "created_at": t.created_at.isoformat(),  # type: ignore[attr-defined]
    }


def _asset_to_dict(a: object) -> dict:
    return {
        "id": str(a.id),  # type: ignore[attr-defined]
        "name": a.name,  # type: ignore[attr-defined]
        "therapeutic_area": a.therapeutic_area,  # type: ignore[attr-defined]
        "modality": a.modality,  # type: ignore[attr-defined]
        "indication": a.indication,  # type: ignore[attr-defined]
        "us_list_price": float(a.us_list_price) if a.us_list_price is not None else None,  # type: ignore[attr-defined]
        "us_net_share": float(a.us_net_share) if a.us_net_share is not None else None,  # type: ignore[attr-defined]
        "launch_year": a.launch_year,  # type: ignore[attr-defined]
        "loe_year": a.loe_year,  # type: ignore[attr-defined]
        "discount_rate": float(a.discount_rate) if a.discount_rate is not None else None,  # type: ignore[attr-defined]
        "created_at": a.created_at.isoformat(),  # type: ignore[attr-defined]
    }


def _scenario_to_dict(s: object) -> dict:
    return {
        "id": str(s.id),  # type: ignore[attr-defined]
        "asset_id": str(s.asset_id),  # type: ignore[attr-defined]
        "name": s.name,  # type: ignore[attr-defined]
        "description": s.description,  # type: ignore[attr-defined]
        "is_baseline": s.is_baseline,  # type: ignore[attr-defined]
        "regulations": s.regulations,  # type: ignore[attr-defined]
        "levers": s.levers,  # type: ignore[attr-defined]
        "cascade_config": s.cascade_config,  # type: ignore[attr-defined]
        "created_at": s.created_at.isoformat(),  # type: ignore[attr-defined]
    }


def _sim_to_dict(s: object) -> dict:
    return {
        "id": str(s.id),  # type: ignore[attr-defined]
        "scenario_id": str(s.scenario_id),  # type: ignore[attr-defined]
        "engine_version": s.engine_version,  # type: ignore[attr-defined]
        "npv": float(s.npv),  # type: ignore[attr-defined]
        "peak_revenue": float(s.peak_revenue) if s.peak_revenue is not None else None,  # type: ignore[attr-defined]
        "method_i_value": float(s.method_i_value) if s.method_i_value is not None else None,  # type: ignore[attr-defined]
        "method_i_anchor": s.method_i_anchor,  # type: ignore[attr-defined]
        "cascade_converged": s.cascade_converged,  # type: ignore[attr-defined]
        "computed_at": s.computed_at.isoformat(),  # type: ignore[attr-defined]
    }


def _api_key_to_dict(k: object) -> dict:
    return {
        "id": str(k.id),  # type: ignore[attr-defined]
        "name": k.name,  # type: ignore[attr-defined]
        "key_prefix": k.key_prefix,  # type: ignore[attr-defined]
        "permissions": k.permissions,  # type: ignore[attr-defined]
        "created_at": k.created_at.isoformat(),  # type: ignore[attr-defined]
        "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,  # type: ignore[attr-defined]
        "expires_at": k.expires_at.isoformat() if k.expires_at else None,  # type: ignore[attr-defined]
        "revoked_at": k.revoked_at.isoformat() if k.revoked_at else None,  # type: ignore[attr-defined]
    }


def _audit_log_to_dict(e: object) -> dict:
    return {
        "id": str(e.id),  # type: ignore[attr-defined]
        "action": e.action,  # type: ignore[attr-defined]
        "payload": e.payload,  # type: ignore[attr-defined]
        "created_at": e.created_at.isoformat(),  # type: ignore[attr-defined]
    }


async def _collect_tenant_data(
    user: User, db: AsyncSession
) -> tuple[dict, dict, list, list, list, list, list]:
    """Collect all tenant data needed for GDPR export. Returns (user_dict, tenant, assets, scenarios, sims, keys, logs)."""
    tenant = await TenantRepo(db).get_by_id(user.tenant_id)
    assets = await AssetRepo(db).list_all(user.tenant_id)
    scenarios = await ScenarioRepo(db).list_all_for_tenant(user.tenant_id)
    simulations = await SimulationResultRepo(db).list_all_for_tenant(user.tenant_id)
    api_keys = await ApiKeyRepo(db).list(user.tenant_id)
    audit_logs = await AuditRepo(db).list_recent_for_tenant(user.tenant_id)

    return (
        _user_to_dict(user),
        _tenant_to_dict(tenant) if tenant else {"id": str(user.tenant_id)},
        [_asset_to_dict(a) for a in assets],
        [_scenario_to_dict(s) for s in scenarios],
        [_sim_to_dict(s) for s in simulations],
        [_api_key_to_dict(k) for k in api_keys],
        [_audit_log_to_dict(e) for e in audit_logs],
    )


@router.get("/my-data")
async def my_data_export(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """GDPR Article 20 — full data export for the authenticated user's tenant."""
    user_dict, tenant_dict, assets, scenarios, sims, keys, logs = await _collect_tenant_data(user, db)

    try:
        pack_bytes = build_gdpr_export(
            user=user_dict,
            tenant=tenant_dict,
            assets=assets,
            scenarios=scenarios,
            simulations=sims,
            api_keys=keys,
            audit_logs=logs,
        )
    except ExportTooLargeError as exc:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(exc)) from exc

    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="user.gdpr_data_exported",
        payload={"asset_count": len(assets), "scenario_count": len(scenarios)},
    )
    await db.commit()

    filename = f"pricingstar_my-data_{date.today().isoformat()}.zip"
    return Response(
        content=pack_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/tenant-pack")
async def tenant_pack_export(
    user: User = Depends(_admin),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Admin-only full tenant data export including all users."""
    all_users = await UserRepo(db).list_for_tenant(user.tenant_id)

    user_dict, tenant_dict, assets, scenarios, sims, keys, logs = await _collect_tenant_data(user, db)

    all_users_dicts = [_user_to_dict(u) for u in all_users]
    user_dict_with_all = {**user_dict, "_all_users": all_users_dicts}

    try:
        pack_bytes = build_gdpr_export(
            user=user_dict_with_all,
            tenant=tenant_dict,
            assets=assets,
            scenarios=scenarios,
            simulations=sims,
            api_keys=keys,
            audit_logs=logs,
        )
    except ExportTooLargeError as exc:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(exc)) from exc

    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="admin.tenant_pack_exported",
        payload={
            "asset_count": len(assets),
            "user_count": len(all_users),
        },
    )
    await db.commit()

    filename = f"pricingstar_tenant-pack_{date.today().isoformat()}.zip"
    return Response(
        content=pack_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
