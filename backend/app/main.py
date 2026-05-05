import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.webhooks import router as webhooks_router
from app.auth import TenantContext, require_auth
from app.config import settings
from app.logging import configure_logging, get_logger

configure_logging(settings.environment)
log = get_logger(__name__)

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment, traces_sample_rate=0.1)

app = FastAPI(
    title="Pricing Star API",
    version="0.1.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.include_router(webhooks_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    log.info("pricing_star_api_starting", environment=settings.environment)


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.get("/api/me", tags=["auth"])
async def me(ctx: TenantContext = Depends(require_auth)) -> dict:
    return {
        "auth0_user_id": ctx.auth0_user_id,
        "tenant_id": str(ctx.tenant_id),
        "tenant_tier": ctx.tenant_tier,
    }
