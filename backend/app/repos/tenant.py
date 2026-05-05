import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant


class TenantRepo:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_trial(self, name: str) -> Tenant:
        tenant = Tenant(
            id=uuid.uuid4(),
            name=name,
            tier="trial",
            status="active",
            trial_expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        self._db.add(tenant)
        await self._db.flush()
        return tenant

    async def get_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        result = await self._db.execute(select(Tenant).where(Tenant.id == tenant_id))
        return result.scalar_one_or_none()
