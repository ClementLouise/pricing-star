import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditRepo:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def log(
        self,
        tenant_id: uuid.UUID,
        action: str,
        payload: dict,
        user_id: uuid.UUID | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            payload=payload,
        )
        self._db.add(entry)
        await self._db.flush()
        return entry
