"""Dashboard endpoints — lightweight aggregations for the home page."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_role
from app.database import get_db
from app.models.user import User
from app.repos.audit import AuditRepo

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Available to all authenticated roles, including viewer
_any_role = require_role(["admin", "editor", "viewer"])


class RecentActivityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str | None
    action: str
    payload: dict
    created_at: str


class RecentActivityResponse(BaseModel):
    items: list[RecentActivityItem]


@router.get("/recent-activity", response_model=RecentActivityResponse)
async def recent_activity(
    limit: int = Query(20, ge=1, le=50),
    user: User = Depends(_any_role),
    db: AsyncSession = Depends(get_db),
) -> RecentActivityResponse:
    """Return the most recent audit log entries for the current tenant.

    Accessible to all roles (not admin-only). Cross-tenant isolation is
    enforced by filtering on user.tenant_id.
    """
    rows = await AuditRepo(db).list_recent_for_dashboard(
        tenant_id=user.tenant_id,
        limit=limit,
    )
    return RecentActivityResponse(
        items=[
            RecentActivityItem(
                id=str(r.id),
                user_id=str(r.user_id) if r.user_id else None,
                action=r.action,
                payload=r.payload or {},
                created_at=r.created_at.isoformat(),
            )
            for r in rows
        ]
    )
