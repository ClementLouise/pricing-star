"""User self-service endpoints."""
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.repos.audit import AuditRepo
from app.repos.user import UserRepo

router = APIRouter(prefix="/users", tags=["users"])


class UserMeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    role: str
    has_seen_welcome: bool


class UserMeUpdate(BaseModel):
    has_seen_welcome: bool | None = None


def _user_read(user: User) -> UserMeRead:
    return UserMeRead(
        id=str(user.id),
        name=user.name,
        role=user.role,
        has_seen_welcome=user.has_seen_welcome,
    )


@router.get("/me", response_model=UserMeRead)
async def get_me(user: User = Depends(get_current_user)) -> UserMeRead:
    return _user_read(user)


@router.patch("/me", response_model=UserMeRead)
async def update_me(
    payload: UserMeUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserMeRead:
    if payload.has_seen_welcome is True and not user.has_seen_welcome:
        await UserRepo(db).mark_welcome_seen(user.id)
        await AuditRepo(db).log(
            tenant_id=user.tenant_id,
            action="user.welcome_dismissed",
            payload={},
            user_id=user.id,
        )
        await db.commit()
        await db.refresh(user)
    return _user_read(user)
