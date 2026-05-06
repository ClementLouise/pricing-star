"""Pydantic schemas for API key CRUD."""
import uuid
from datetime import datetime

from pydantic import BaseModel


class ApiKeyRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    key_prefix: str
    permissions: dict
    created_at: datetime
    expires_at: datetime | None
    revoked_at: datetime | None
    last_used_at: datetime | None
