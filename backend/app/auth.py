import uuid
from dataclasses import dataclass
from datetime import datetime

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings
from app.logging import get_logger

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
