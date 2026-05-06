"""Asset repository — every query filters by tenant_id per PRD §03."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate


class AssetRepo:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list(
        self,
        tenant_id: uuid.UUID,
        include_archived: bool = False,
        limit: int = 50,
        cursor: uuid.UUID | None = None,
    ) -> list[Asset]:
        q = select(Asset).where(Asset.tenant_id == tenant_id)
        if not include_archived:
            q = q.where(Asset.archived_at.is_(None))
        if cursor is not None:
            q = q.where(Asset.id > cursor)
        q = q.order_by(Asset.created_at.desc()).limit(limit)
        result = await self._db.execute(q)
        return list(result.scalars().all())

    async def get(self, asset_id: uuid.UUID, tenant_id: uuid.UUID) -> Asset | None:
        result = await self._db.execute(
            select(Asset).where(
                Asset.id == asset_id,
                Asset.tenant_id == tenant_id,
                Asset.archived_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: AssetCreate,
    ) -> Asset:
        asset = Asset(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            created_by=user_id,
            **payload.model_dump(),
        )
        self._db.add(asset)
        await self._db.flush()
        return asset

    async def update(self, asset: Asset, payload: AssetUpdate) -> Asset:
        _occ = frozenset({"expected_updated_at", "force_override"})
        for field, value in payload.model_dump(exclude_none=True, exclude=_occ).items():
            setattr(asset, field, value)
        asset.updated_at = datetime.now(timezone.utc)
        await self._db.flush()
        return asset

    async def archive(self, asset: Asset) -> Asset:
        asset.archived_at = datetime.now(timezone.utc)
        await self._db.flush()
        return asset

    async def duplicate(
        self, asset: Asset, new_name: str, user_id: uuid.UUID
    ) -> Asset:
        clone = Asset(
            id=uuid.uuid4(),
            tenant_id=asset.tenant_id,
            created_by=user_id,
            name=new_name,
            therapeutic_area=asset.therapeutic_area,
            modality=asset.modality,
            indication=asset.indication,
            us_list_price=asset.us_list_price,
            us_net_share=asset.us_net_share,
            launch_year=asset.launch_year,
            peak_year=asset.peak_year,
            loe_year=asset.loe_year,
            cogs_percent=asset.cogs_percent,
            discount_rate=asset.discount_rate,
            us_patient_population=asset.us_patient_population,
            ex_us_patient_population=asset.ex_us_patient_population,
            peak_capture_rate=asset.peak_capture_rate,
            part_b_share=asset.part_b_share,
            ramp_years=asset.ramp_years,
        )
        self._db.add(clone)
        await self._db.flush()
        return clone
