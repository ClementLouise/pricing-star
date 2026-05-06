"""Asset management endpoints — per PRD §05."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api._occ import check_occ
from app.auth import require_role
from app.database import get_db
from app.models.asset import Asset
from app.models.user import User
from app.repos.asset import AssetRepo
from app.repos.audit import AuditRepo
from app.schemas.asset import AssetCreate, AssetDuplicate, AssetRead, AssetUpdate
from app.schemas.common import Page


def _asset_snapshot(asset: Asset) -> dict:
    return {
        "name": asset.name,
        "therapeutic_area": asset.therapeutic_area,
        "modality": asset.modality,
        "indication": asset.indication,
        "us_list_price": float(asset.us_list_price) if asset.us_list_price is not None else None,
        "us_net_share": float(asset.us_net_share) if asset.us_net_share is not None else None,
        "launch_year": asset.launch_year,
        "peak_year": asset.peak_year,
        "loe_year": asset.loe_year,
        "cogs_percent": float(asset.cogs_percent),
        "discount_rate": float(asset.discount_rate),
        "us_patient_population": asset.us_patient_population,
        "ex_us_patient_population": asset.ex_us_patient_population,
        "peak_capture_rate": float(asset.peak_capture_rate),
        "part_b_share": float(asset.part_b_share),
        "ramp_years": asset.ramp_years,
    }

router = APIRouter(prefix="/assets", tags=["assets"])

_editor = require_role(["admin", "editor"])
_viewer = require_role(["admin", "editor", "viewer"])


@router.get("", response_model=Page[AssetRead])
async def list_assets(
    archived: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    cursor: uuid.UUID | None = Query(None),
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> Page[AssetRead]:
    repo = AssetRepo(db)
    items = await repo.list(user.tenant_id, include_archived=archived, limit=limit + 1, cursor=cursor)
    next_cursor = str(items[-1].id) if len(items) > limit else None
    return Page(items=[AssetRead.model_validate(a) for a in items[:limit]], next_cursor=next_cursor)


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreate,
    user: User = Depends(_editor),
    db: AsyncSession = Depends(get_db),
) -> AssetRead:
    repo = AssetRepo(db)
    asset = await repo.create(user.tenant_id, user.id, payload)
    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="asset.create",
        payload={"asset_id": str(asset.id), "name": asset.name},
    )
    return AssetRead.model_validate(asset)


@router.get("/{asset_id}", response_model=AssetRead)
async def get_asset(
    asset_id: uuid.UUID,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> AssetRead:
    asset = await AssetRepo(db).get(asset_id, user.tenant_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return AssetRead.model_validate(asset)


@router.patch("/{asset_id}", response_model=AssetRead)
async def update_asset(
    asset_id: uuid.UUID,
    payload: AssetUpdate,
    user: User = Depends(_editor),
    db: AsyncSession = Depends(get_db),
) -> AssetRead:
    repo = AssetRepo(db)
    asset = await repo.get(asset_id, user.tenant_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    is_force_conflict = check_occ(asset.updated_at, payload.expected_updated_at, payload.force_override)
    before_snapshot = _asset_snapshot(asset) if is_force_conflict else None
    conflicting_ts = asset.updated_at.isoformat() if is_force_conflict else None

    asset = await repo.update(asset, payload)

    if is_force_conflict:
        _occ_excl = frozenset({"expected_updated_at", "force_override"})
        await AuditRepo(db).log(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action="asset.force_overwrite_conflict",
            payload={
                "asset_id": str(asset_id),
                "conflicting_updated_at": conflicting_ts,
                "client_expected_at": payload.expected_updated_at.isoformat() if payload.expected_updated_at else None,
                "before_state": before_snapshot,
                "after_state": payload.model_dump(exclude_none=True, exclude=_occ_excl),
            },
        )
    else:
        await AuditRepo(db).log(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action="asset.update",
            payload={"asset_id": str(asset_id)},
        )
    return AssetRead.model_validate(asset)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_asset(
    asset_id: uuid.UUID,
    user: User = Depends(_editor),
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = AssetRepo(db)
    asset = await repo.get(asset_id, user.tenant_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    await repo.archive(asset)
    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="asset.archive",
        payload={"asset_id": str(asset_id)},
    )


@router.post("/{asset_id}/duplicate", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def duplicate_asset(
    asset_id: uuid.UUID,
    payload: AssetDuplicate,
    user: User = Depends(_editor),
    db: AsyncSession = Depends(get_db),
) -> AssetRead:
    repo = AssetRepo(db)
    asset = await repo.get(asset_id, user.tenant_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    clone = await repo.duplicate(asset, payload.new_name, user.id)
    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="asset.duplicate",
        payload={"source_id": str(asset_id), "new_id": str(clone.id)},
    )
    return AssetRead.model_validate(clone)
