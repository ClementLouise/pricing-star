"""Audit log query endpoint (admin only) — per PRD §05."""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_role
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.common import Page

router = APIRouter(prefix="/audit-logs", tags=["audit"])

_admin = require_role(["admin"])


@router.get("", response_model=Page[dict])
async def list_audit_logs(
    entity_type: str | None = Query(None),
    user_id: uuid.UUID | None = Query(None),
    from_dt: datetime | None = Query(None, alias="from"),
    to_dt: datetime | None = Query(None, alias="to"),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(_admin),
    db: AsyncSession = Depends(get_db),
) -> Page[dict]:
    q = select(AuditLog).where(AuditLog.tenant_id == user.tenant_id)
    if entity_type is not None:
        q = q.where(AuditLog.action.startswith(entity_type + "."))
    if user_id is not None:
        q = q.where(AuditLog.user_id == user_id)
    if from_dt is not None:
        q = q.where(AuditLog.created_at >= from_dt)
    if to_dt is not None:
        q = q.where(AuditLog.created_at <= to_dt)
    q = q.order_by(AuditLog.created_at.desc()).limit(limit + 1)

    result = await db.execute(q)
    rows = result.scalars().all()
    next_cursor = str(rows[-1].id) if len(rows) > limit else None
    items = [
        {
            "id": str(r.id),
            "user_id": str(r.user_id) if r.user_id else None,
            "action": r.action,
            "payload": r.payload,
            "created_at": r.created_at.isoformat(),
        }
        for r in list(rows)[:limit]
    ]
    return Page(items=items, next_cursor=next_cursor)
