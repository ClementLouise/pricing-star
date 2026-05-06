import sentry_sdk
from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_keys import router as api_keys_router
from app.api.assets import router as assets_router
from app.api.audit_logs import router as audit_logs_router
from app.api.reference import router as reference_router
from app.api.scenarios import router as scenarios_router
from app.api.simulations import router as simulations_router
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
    version="0.2.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next: object) -> Response:
    response: Response = await call_next(request)  # type: ignore[operator]
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    return response

_API = "/api"
app.include_router(webhooks_router)
app.include_router(api_keys_router)
app.include_router(assets_router, prefix=_API)
app.include_router(scenarios_router, prefix=_API)
app.include_router(simulations_router, prefix=_API)
app.include_router(reference_router, prefix=_API)
app.include_router(audit_logs_router, prefix=_API)


@app.on_event("startup")
async def startup() -> None:
    log.info("pricing_star_api_starting", environment=settings.environment)


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.get("/health/ready", tags=["ops"])
async def health_ready() -> dict[str, str]:
    """Readiness probe — verifies DB connectivity before accepting traffic."""
    from app.database import engine
    from sqlalchemy import text
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        log.error("readiness_probe_failed", error=str(exc))
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database not reachable")


@app.get("/api/me", tags=["auth"])
async def me(ctx: TenantContext = Depends(require_auth)) -> dict:
    return {
        "auth0_user_id": ctx.auth0_user_id,
        "tenant_id": str(ctx.tenant_id),
        "tenant_tier": ctx.tenant_tier,
    }
