import uuid

import httpx

from app.config import settings
from app.logging import get_logger

log = get_logger(__name__)

_token_cache: str | None = None


async def _get_management_token() -> str:
    global _token_cache
    if _token_cache:
        return _token_cache

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://{settings.auth0_domain}/oauth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": settings.auth0_client_id,
                "client_secret": settings.auth0_client_secret,
                "audience": f"https://{settings.auth0_domain}/api/v2/",
            },
        )
        resp.raise_for_status()
        _token_cache = resp.json()["access_token"]
        return _token_cache  # type: ignore[return-value]


async def set_user_tenant_metadata(
    auth0_user_id: str, tenant_id: uuid.UUID, tenant_tier: str
) -> None:
    """Write tenant_id and tenant_tier into Auth0 app_metadata.

    Ensures the custom claims action picks them up on next token issue.
    """
    token = await _get_management_token()
    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"https://{settings.auth0_domain}/api/v2/users/{auth0_user_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"app_metadata": {"tenant_id": str(tenant_id), "tenant_tier": tenant_tier}},
        )
        if not resp.is_success:
            log.error("auth0_metadata_update_failed", user=auth0_user_id, status=resp.status_code)
            resp.raise_for_status()
