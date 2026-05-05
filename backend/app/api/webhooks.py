import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.logging import get_logger
from app.services.trial import create_trial_tenant

log = get_logger(__name__)
router = APIRouter(prefix="/internal/webhooks/auth0", tags=["webhooks"])


class PostRegistrationPayload(BaseModel):
    auth0_user_id: str
    email: str
    name: str
    registered_at: str


def _verify_secret(x_webhook_secret: str = Header(...)) -> None:
    if not hmac.compare_digest(x_webhook_secret, settings.webhook_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")


@router.post("/post-registration", status_code=status.HTTP_204_NO_CONTENT)
async def post_registration(
    payload: PostRegistrationPayload,
    _: None = Depends(_verify_secret),
    db: AsyncSession = Depends(get_db),
) -> None:
    log.info("auth0_post_registration_received", user=payload.auth0_user_id)
    await create_trial_tenant(
        db=db,
        auth0_user_id=payload.auth0_user_id,
        email=payload.email,
        name=payload.name,
    )
