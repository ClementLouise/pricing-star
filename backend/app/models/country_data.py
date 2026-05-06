import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy import JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CountryData(Base):
    """Per-country pricing/volume data for a scenario — per PRD §03.

    G2N resolution order (fallback chain):
    1. g2n_time_series[year]   if present
    2. g2n_ratio               if not null
    3. country_reference.default_g2n_ratio
    """

    __tablename__ = "country_data"
    __table_args__ = (
        UniqueConstraint("scenario_id", "country_code", name="uq_country_data_scenario_country"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scenario.id", ondelete="CASCADE"), nullable=False, index=True
    )

    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    list_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    net_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    volume: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    launched: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    launch_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    withdrawn: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Static G2N; used when g2n_time_series doesn't cover the year
    g2n_ratio: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    # Per-year G2N overrides: {"2027": 0.85, "2028": 0.83, ...}
    g2n_time_series: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
