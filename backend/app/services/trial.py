from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging import get_logger
from app.repos.audit import AuditRepo
from app.repos.tenant import TenantRepo
from app.repos.user import UserRepo
from app.services.auth0_mgmt import set_user_tenant_metadata

log = get_logger(__name__)


async def create_trial_tenant(
    db: AsyncSession,
    auth0_user_id: str,
    email: str,
    name: str,
) -> None:
    """Create a trial tenant for a new self-serve signup and seed sample assets."""
    tenant_repo = TenantRepo(db)
    user_repo = UserRepo(db)
    audit_repo = AuditRepo(db)

    # EC-TRIAL-08: detect duplicate signups
    existing_user = await user_repo.get_by_auth0_id(auth0_user_id)
    if existing_user is not None:
        existing_tenant = await tenant_repo.get_by_id(existing_user.tenant_id)
        if existing_tenant is not None and existing_tenant.tier == "trial" and existing_tenant.status == "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account already exists for this email. Please sign in instead.",
            )
        # Expired or non-trial tenant: skip silently — user can still sign in
        log.info("signup_duplicate_skipped", user_id=str(existing_user.id))
        return

    company_name = f"{name}'s Team"
    tenant = await tenant_repo.create_trial(name=company_name)
    user = await user_repo.create(
        tenant_id=tenant.id,
        auth0_user_id=auth0_user_id,
        email=email,
        name=name,
    )
    await audit_repo.log(
        tenant_id=tenant.id,
        user_id=user.id,
        action="trial.tenant_created",
        payload={"tier": "trial", "expires_at": tenant.trial_expires_at.isoformat()},
    )

    await db.commit()

    # Update Auth0 app_metadata so JWT claims include tenant context on next login
    await set_user_tenant_metadata(auth0_user_id, tenant.id, "trial")

    # Phase 0 stub — full seeding implemented in Phase 2 once asset table exists
    log.info("sample_asset_seeding_stub", tenant_id=str(tenant.id))

    log.info("trial_tenant_created", tenant_id=str(tenant.id), user_id=str(user.id))
