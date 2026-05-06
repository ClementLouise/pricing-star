"""Optimistic concurrency control helper (EC-UI-02)."""
from datetime import datetime, timezone

from fastapi import HTTPException, status


def check_occ(
    db_updated_at: datetime,
    expected_updated_at: datetime | None,
    force_override: bool,
) -> bool:
    """Compare DB timestamp against client expectation.

    Returns True when a force-override conflict was accepted — the caller
    must then write a 'force_overwrite_conflict' audit log entry.
    Raises HTTP 409 when timestamps differ and force_override is False.
    """
    if expected_updated_at is None:
        return False

    def _utc(ts: datetime) -> datetime:
        return ts.astimezone(timezone.utc) if ts.tzinfo else ts.replace(tzinfo=timezone.utc)

    if _utc(db_updated_at) == _utc(expected_updated_at):
        return False

    if not force_override:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict: resource was modified by another user since you last loaded it",
        )
    return True
