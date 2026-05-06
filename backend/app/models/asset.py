import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Asset(Base):
    """A pharmaceutical asset being modeled — per PRD §03."""

    __tablename__ = "asset"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    therapeutic_area: Mapped[str | None] = mapped_column(String(100), nullable=True)
    modality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    indication: Mapped[str | None] = mapped_column(String(255), nullable=True)

    us_list_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    us_net_share: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    launch_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    peak_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    loe_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cogs_percent: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False, default=0.15)
    discount_rate: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False, default=0.10)
    us_patient_population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ex_us_patient_population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    peak_capture_rate: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False, default=0.5)
    part_b_share: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False, default=0.5)
    ramp_years: Mapped[int] = mapped_column(Integer, nullable=False, default=4)

    is_sample: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sample_origin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sample_edited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
