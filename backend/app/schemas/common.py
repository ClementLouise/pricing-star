"""Shared Pydantic schemas: pagination, errors — per PRD §05."""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details — per PRD §05 error format."""
    type: str = "https://api.pricingstar.example.com/errors/generic"
    title: str
    status: int
    detail: str
    instance: str | None = None
