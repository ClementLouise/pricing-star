"""API key repository — tenant-scoped queries, soft-delete via revoked_at."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey


class ApiKeyRepo:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list(self, tenant_id: uuid.UUID) -> list[ApiKey]:
        result = await self._db.execute(
            select(ApiKey)
            .where(ApiKey.tenant_id == tenant_id)
            .order_by(ApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, key_id: uuid.UUID, tenant_id: uuid.UUID) -> ApiKey | None:
        result = await self._db.execute(
            select(ApiKey).where(
                ApiKey.id == key_id,
                ApiKey.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_prefix(self, prefix: str) -> list[ApiKey]:
        """Fetch all non-expired keys with this prefix for bcrypt verification."""
        result = await self._db.execute(
            select(ApiKey).where(ApiKey.key_prefix == prefix)
        )
        return list(result.scalars().all())

    async def revoke(self, key_id: uuid.UUID, tenant_id: uuid.UUID) -> ApiKey | None:
        """Soft-delete: set revoked_at. Idempotent — no-op if already revoked."""
        key = await self.get(key_id, tenant_id)
        if key is None:
            return None
        if key.revoked_at is None:
            key.revoked_at = datetime.now(timezone.utc)
            await self._db.flush()
        return key

    async def create(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        name: str,
        key_hash: str,
        key_prefix: str,
        permissions: dict,
        expires_at: datetime | None = None,
    ) -> ApiKey:
        api_key = ApiKey(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            created_by=user_id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            permissions=permissions,
            expires_at=expires_at,
        )
        self._db.add(api_key)
        await self._db.flush()
        return api_key
