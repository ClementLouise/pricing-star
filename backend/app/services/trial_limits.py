"""Trial mode limit enforcement — per PRD §13_TRIAL_MODE."""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.asset import Asset
from app.models.scenario import Scenario
from app.models.user import User


def _is_limited(tier: str) -> bool:
    return tier == "trial"


def check_trial_expiry(tier: str, trial_expires_at: datetime | None) -> None:
    """Raise 403 if the tenant's trial has expired."""
    if tier != "trial" or trial_expires_at is None:
        return
    if datetime.now(timezone.utc) > trial_expires_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "trial_expired", "message": "Your trial has expired. Contact sales to upgrade."},
        )


async def assert_can_create_asset(
    tenant_id: object,
    tier: str,
    trial_expires_at: datetime | None,
    db: AsyncSession,
) -> None:
    """Raise 403 if trial tenant is at asset limit."""
    check_trial_expiry(tier, trial_expires_at)
    if not _is_limited(tier):
        return
    count = await db.scalar(
        select(func.count()).where(
            Asset.tenant_id == tenant_id,
            Asset.archived_at.is_(None),
        )
    )
    if (count or 0) >= settings.trial_max_assets:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "trial_limit_reached",
                "message": (
                    f"Trial accounts are limited to {settings.trial_max_assets} assets. "
                    "Upgrade to production for 100+ assets."
                ),
            },
        )


async def assert_can_create_scenario(
    asset_id: object,
    tenant_id: object,
    tier: str,
    trial_expires_at: datetime | None,
    db: AsyncSession,
) -> None:
    """Raise 403 if trial tenant is at scenario-per-asset limit."""
    check_trial_expiry(tier, trial_expires_at)
    if not _is_limited(tier):
        return
    count = await db.scalar(
        select(func.count()).where(
            Scenario.asset_id == asset_id,
            Scenario.tenant_id == tenant_id,
            Scenario.archived_at.is_(None),
        )
    )
    if (count or 0) >= settings.trial_max_scenarios_per_asset:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "trial_limit_reached",
                "message": (
                    f"Trial accounts are limited to {settings.trial_max_scenarios_per_asset} "
                    "scenarios per asset."
                ),
            },
        )


async def assert_can_invite_user(
    tenant_id: object,
    tier: str,
    trial_expires_at: datetime | None,
    db: AsyncSession,
) -> None:
    """Raise 403 if trial tenant is at user limit."""
    check_trial_expiry(tier, trial_expires_at)
    if not _is_limited(tier):
        return
    count = await db.scalar(
        select(func.count()).where(User.tenant_id == tenant_id)
    )
    if (count or 0) >= settings.trial_max_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "trial_limit_reached",
                "message": f"Trial accounts are limited to {settings.trial_max_users} users.",
            },
        )
