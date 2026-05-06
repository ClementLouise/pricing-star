"""Phase 2 entities: asset, scenario, country_data, simulation_result, api_key

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-06
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "asset",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("therapeutic_area", sa.String(100), nullable=True),
        sa.Column("modality", sa.String(100), nullable=True),
        sa.Column("indication", sa.String(255), nullable=True),
        sa.Column("us_list_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("us_net_share", sa.Numeric(5, 4), nullable=True),
        sa.Column("launch_year", sa.Integer, nullable=True),
        sa.Column("peak_year", sa.Integer, nullable=True),
        sa.Column("loe_year", sa.Integer, nullable=True),
        sa.Column("cogs_percent", sa.Numeric(5, 4), nullable=False, server_default="0.15"),
        sa.Column("discount_rate", sa.Numeric(5, 4), nullable=False, server_default="0.10"),
        sa.Column("us_patient_population", sa.Integer, nullable=True),
        sa.Column("ex_us_patient_population", sa.Integer, nullable=True),
        sa.Column("peak_capture_rate", sa.Numeric(5, 4), nullable=False, server_default="0.5"),
        sa.Column("part_b_share", sa.Numeric(5, 4), nullable=False, server_default="0.5"),
        sa.Column("ramp_years", sa.Integer, nullable=False, server_default="4"),
        sa.Column("is_sample", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("sample_origin", sa.String(50), nullable=True),
        sa.Column("sample_edited", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_asset_tenant_id", "asset", ["tenant_id"])
    op.create_index("ix_asset_tenant_archived", "asset", ["tenant_id", "archived_at"])

    op.create_table(
        "scenario",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_id", UUID(as_uuid=True), sa.ForeignKey("asset.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_baseline", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("regulations", JSONB, nullable=False, server_default="{}"),
        sa.Column("levers", JSONB, nullable=False, server_default="{}"),
        sa.Column("cascade_config", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_scenario_tenant_id", "scenario", ["tenant_id"])
    op.create_index("ix_scenario_asset_id", "scenario", ["asset_id"])
    op.create_index("ix_scenario_tenant_asset", "scenario", ["tenant_id", "asset_id", "archived_at"])

    op.create_table(
        "country_data",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scenario_id", UUID(as_uuid=True), sa.ForeignKey("scenario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("country_code", sa.String(2), nullable=False),
        sa.Column("list_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("net_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("volume", sa.Numeric(8, 4), nullable=True),
        sa.Column("launched", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("launch_year", sa.Integer, nullable=True),
        sa.Column("withdrawn", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("g2n_ratio", sa.Numeric(5, 4), nullable=True),
        sa.Column("g2n_time_series", JSONB, nullable=True),
        sa.UniqueConstraint("scenario_id", "country_code", name="uq_country_data_scenario_country"),
    )
    op.create_index("ix_country_data_scenario_id", "country_data", ["scenario_id"])
    op.create_index("ix_country_data_tenant_id", "country_data", ["tenant_id"])

    op.create_table(
        "simulation_result",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scenario_id", UUID(as_uuid=True), sa.ForeignKey("scenario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("computed_by", UUID(as_uuid=True), sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
        sa.Column("engine_version", sa.String(20), nullable=False),
        sa.Column("npv", sa.Numeric(15, 2), nullable=False),
        sa.Column("peak_revenue", sa.Numeric(15, 2), nullable=True),
        sa.Column("method_i_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("method_i_anchor", sa.String(2), nullable=True),
        sa.Column("method_ii_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("applicable_benchmark", sa.Numeric(12, 2), nullable=True),
        sa.Column("per_unit_rebate", sa.Numeric(12, 2), nullable=True),
        sa.Column("effective_us_net", sa.Numeric(12, 2), nullable=True),
        sa.Column("cascade_iterations", sa.Integer, nullable=True),
        sa.Column("cascade_converged", sa.Boolean, nullable=True),
        sa.Column("final_prices", JSONB, nullable=False),
        sa.Column("yearly_breakdown", JSONB, nullable=False),
        sa.Column("monte_carlo_result", JSONB, nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_simulation_result_tenant_id", "simulation_result", ["tenant_id"])
    op.create_index("ix_simulation_result_scenario_id", "simulation_result", ["scenario_id"])
    op.create_index(
        "ix_simulation_result_tenant_scenario_date",
        "simulation_result",
        ["tenant_id", "scenario_id", "computed_at"],
    )

    op.create_table(
        "api_key",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("key_prefix", sa.String(16), nullable=False),
        sa.Column("permissions", JSONB, nullable=False, server_default="{}"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_api_key_tenant_id", "api_key", ["tenant_id"])
    op.create_index("ix_api_key_key_hash", "api_key", ["key_hash"], unique=True)


def downgrade() -> None:
    op.drop_table("api_key")
    op.drop_table("simulation_result")
    op.drop_table("country_data")
    op.drop_table("scenario")
    op.drop_table("asset")
