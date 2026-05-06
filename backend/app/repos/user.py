import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


def _mask_email(email: str) -> str:
    """Mask email for logs — no PII per PRD non-functional requirements."""
    local, _, domain = email.partition("@")
    return f"{local[0]}***@{domain}" if local else "***@" + domain


class UserRepo:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_auth0_id(self, auth0_user_id: str) -> User | None:
        result = await self._db.execute(
            select(User).where(User.auth0_user_id == auth0_user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        tenant_id: uuid.UUID,
        auth0_user_id: str,
        email: str,
        name: str,
    ) -> User:
        user = User(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            auth0_user_id=auth0_user_id,
            email_masked=_mask_email(email),
            name=name,
            role="admin",  # first user of a trial tenant is admin
        )
        self._db.add(user)
        await self._db.flush()
        return user
