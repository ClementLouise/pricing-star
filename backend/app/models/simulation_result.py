import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SimulationResult(Base):
    """Output of running a scenario through the calculation engine — per PRD §03."""

    __tablename__ = "simulation_result"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scenario.id", ondelete="CASCADE"), nullable=False, index=True
    )
    computed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )

    engine_version: Mapped[str] = mapped_column(String(20), nullable=False)

    npv: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    peak_revenue: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    method_i_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    method_i_anchor: Mapped[str | None] = mapped_column(String(2), nullable=True)
    method_ii_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    applicable_benchmark: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    per_unit_rebate: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    effective_us_net: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    cascade_iterations: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cascade_converged: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Full price set after cascade: {"US": 180000, "DE": 90000, ...}
    final_prices: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Year-by-year revenue array
    yearly_breakdown: Mapped[list] = mapped_column(JSON, nullable=False)
    # Optional Monte Carlo result
    monte_carlo_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
