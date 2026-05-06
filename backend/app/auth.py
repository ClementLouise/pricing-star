import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.logging import get_logger
from app.models.user import User

log = get_logger(__name__)
bearer_scheme = HTTPBearer()

CLAIMS_NS = "https://pricingstar.io"

_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(settings.auth0_jwks_url)
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


@dataclass
class TenantContext:
    tenant_id: uuid.UUID
    tenant_tier: str
    trial_expires_at: datetime | None
    auth0_user_id: str


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> TenantContext:
    """Validate JWT and extract tenant context — does NOT hit the database."""
    token = credentials.credentials
    try:
        jwks = await _get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.auth0_audience,
            issuer=settings.auth0_issuer,
        )
    except JWTError as exc:
        log.warning("jwt_validation_failed", error=str(exc))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    tenant_id_raw = payload.get(f"{CLAIMS_NS}/tenant_id")
    if not tenant_id_raw:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tenant context in token")

    trial_expires_raw = payload.get(f"{CLAIMS_NS}/trial_expires_at")

    return TenantContext(
        tenant_id=uuid.UUID(tenant_id_raw),
        tenant_tier=payload.get(f"{CLAIMS_NS}/tenant_tier", "trial"),
        trial_expires_at=datetime.fromisoformat(trial_expires_raw) if trial_expires_raw else None,
        auth0_user_id=payload["sub"],
    )


async def get_current_user(
    ctx: TenantContext = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve User record from DB. Raises 401 if not found (e.g. webhook-created tenant not yet synced)."""
    result = await db.execute(
        select(User).where(
            User.auth0_user_id == ctx.auth0_user_id,
            User.tenant_id == ctx.tenant_id,
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        log.warning("user_not_found_in_db", auth0_user_id=ctx.auth0_user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not provisioned")
    return user


def require_role(allowed_roles: list[str]) -> Callable:
    """FastAPI dependency factory for RBAC — per PRD §08 permission matrix."""
    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' is not permitted for this action",
            )
        return user

    return _check
