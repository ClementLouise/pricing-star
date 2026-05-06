"""API key management endpoints — per PRD §08."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_role
from app.database import get_db
from app.models.user import User
from app.repos.api_key import ApiKeyRepo
from app.repos.audit import AuditRepo
from app.schemas.api_key import ApiKeyRead

router = APIRouter(prefix="/v1/api-keys", tags=["api-keys"])

_admin = require_role(["admin"])


@router.get("", response_model=list[ApiKeyRead])
async def list_api_keys(
    user: User = Depends(_admin),
    db: AsyncSession = Depends(get_db),
) -> list[ApiKeyRead]:
    """List all API keys for the current tenant (including revoked)."""
    keys = await ApiKeyRepo(db).list(user.tenant_id)
    return [ApiKeyRead.model_validate(k) for k in keys]


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: uuid.UUID,
    user: User = Depends(_admin),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Revoke an API key by ID (soft-delete via revoked_at).

    - 204 No Content on success
    - 200 OK if already revoked (idempotent)
    - 404 if key not found or belongs to a different tenant
    """
    repo = ApiKeyRepo(db)
    key = await repo.get(key_id, user.tenant_id)

    if key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    if key.revoked_at is not None:
        return Response(status_code=status.HTTP_200_OK)

    key = await repo.revoke(key_id, user.tenant_id)

    await AuditRepo(db).log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="api_key.revoked",
        payload={"api_key_id": str(key_id), "key_prefix": key.key_prefix},
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
