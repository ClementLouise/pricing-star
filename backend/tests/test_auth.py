import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_protected_route_rejects_missing_token() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/me")
    assert response.status_code in (401, 403)  # HTTPBearer raises 401/403 depending on FastAPI version


@pytest.mark.asyncio
async def test_protected_route_rejects_invalid_token() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert response.status_code == 401
