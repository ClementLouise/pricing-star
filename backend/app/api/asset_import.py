"""Bulk XLSX import endpoints — template download, dry-run validation, and execute."""
from __future__ import annotations

import uuid
from dataclasses import asdict

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import TenantContext, require_auth, require_role
from app.database import get_db
from app.models.user import User
from app.repos.audit import AuditRepo
from app.services.asset_import import (
    ImportMode,
    build_import_template,
    execute_import_plan,
    parse_xlsx,
)

router = APIRouter(prefix="/import", tags=["import"])

_editor = require_role(["admin", "editor"])
_viewer = require_role(["admin", "editor", "viewer"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


def _errs(errors: list) -> list[dict]:
    return [asdict(e) for e in errors]


@router.get("/template")
async def download_template(
    asset_name: str = Query("My Asset", max_length=200),
    user: User = Depends(_viewer),
) -> Response:
    """Return an empty XLSX import template (5 sheets, one sample row)."""
    xlsx_bytes = build_import_template(asset_name)
    slug = asset_name.replace(" ", "_")[:40]
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="pricing-star_template_{slug}.xlsx"'},
    )


@router.post("/dry-run")
async def dry_run_import(
    file: UploadFile = File(...),
    mode: ImportMode = Form(ImportMode.CREATE_NEW),
    target_asset_id: uuid.UUID | None = Form(None),
    user: User = Depends(_editor),
) -> dict:
    """
    Parse and validate an XLSX import file without touching the database.
    Returns errors, warnings, and a row-count summary.
    """
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Le fichier dépasse la limite de 10 Mo ({len(content):,} octets)",
        )
    plan = parse_xlsx(content, mode, target_asset_id)
    return {
        "valid": not plan.errors,
        "mode": plan.mode.value,
        "errors": _errs(plan.errors),
        "warnings": _errs(plan.warnings),
        "summary": plan.summary,
    }


@router.post("/execute", status_code=status.HTTP_201_CREATED)
async def execute_import(
    file: UploadFile = File(...),
    mode: ImportMode = Form(...),
    target_asset_id: uuid.UUID | None = Form(None),
    confirmed: bool = Form(False),
    user: User = Depends(_editor),
    ctx: TenantContext = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Execute a validated XLSX import. All-or-nothing transaction.
    Requires confirmed=true — run dry-run first to surface validation errors.
    """
    if not confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Définissez confirmed=true pour exécuter l'import. Lancez d'abord le dry-run.",
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Le fichier dépasse la limite de 10 Mo ({len(content):,} octets)",
        )

    plan = parse_xlsx(content, mode, target_asset_id)
    if plan.errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Le fichier contient des erreurs de validation.",
                "errors": _errs(plan.errors),
                "warnings": _errs(plan.warnings),
                "summary": plan.summary,
            },
        )

    result = await execute_import_plan(
        plan=plan,
        db=db,
        tenant_id=user.tenant_id,
        user_id=user.id,
        tier=ctx.tenant_tier,
        trial_expires_at=ctx.trial_expires_at,
    )

    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action=f"asset.import_{mode.value}",
        payload={
            "asset_id": result.get("asset_id"),
            "mode": mode.value,
            "scenario_count": len(result.get("scenario_ids", [])),
            "country_data_count": result.get("country_data_count"),
        },
    )
    await db.commit()

    return {
        **result,
        "warnings": _errs(plan.warnings),
    }
