"""Pydantic schemas for SimulationResult — per PRD §05."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class YearlyBreakdownItem(BaseModel):
    year: int
    us_revenue: float
    ex_us_revenue: float
    total_net: float
    discounted: float


class SimulationResultRead(BaseModel):
    model_config = {"from_attributes": True}

    simulation_id: uuid.UUID
    engine_version: str
    computed_at: datetime
    npv: float
    peak_revenue: float | None
    method_i_value: float | None
    method_i_anchor: str | None
    method_ii_value: float | None
    applicable_benchmark: float | None
    per_unit_rebate: float | None
    effective_us_net: float | None
    cascade_iterations: int | None
    cascade_converged: bool | None
    final_prices: dict[str, float]
    yearly_breakdown: list[YearlyBreakdownItem]
    monte_carlo_result: dict | None


class SimulationSummary(BaseModel):
    model_config = {"from_attributes": True}

    simulation_id: uuid.UUID
    computed_at: datetime
    engine_version: str
    npv: float
    method_i_anchor: str | None


class SimulateResponse(BaseModel):
    simulation_id: uuid.UUID
    engine_version: str
    computed_at: datetime
    computed_in_ms: int
    results: SimulationResultRead


class MonteCarloJobResponse(BaseModel):
    job_id: uuid.UUID
    status: str
    polling_url: str


class AnchorCountryRead(BaseModel):
    country: str
    country_name: str
    nominal: float
    ppp: float
    adjusted: float


class AnchorAnalysisResponse(BaseModel):
    model: str
    anchor: AnchorCountryRead
    second: AnchorCountryRead | None
    benchmark: float
    anchor_gap: float
    anchor_gap_pct: float
    is_non_obvious_anchor: bool
    nominal_lowest: AnchorCountryRead | None
    ringfence_recommendation: str
    all_ranked: list[AnchorCountryRead]


class DECascadeRequest(BaseModel):
    opt_in_rebate_pct: float = 0.09


class MarketImpactRead(BaseModel):
    country: str
    country_name: str
    before: float
    after: float
    delta: float
    delta_pct: float


class DECascadeResponse(BaseModel):
    opt_in_rebate_pct: float
    de_price_before: float
    de_price_after: float
    de_disclosed_delta: float
    market_impacts: list[MarketImpactRead]
    referencing_markets_count: int
    actually_impacted_count: int
    cascade_iterations: int


# ─── Monte Carlo ─────────────────────────────────────────────────────────────


class MonteCarloRequest(BaseModel):
    n: int = 500
    sigma: float = 0.05
    model: str = "GUARD"
    seed: int | None = None


class MonteCarloResponse(BaseModel):
    samples_n: int
    mean: float
    p05: float
    p50: float
    p95: float
    range: float
    sigma_input: float


# ─── Optimizer ────────────────────────────────────────────────────────────────


class OptimizerRecommendation(BaseModel):
    type: str
    title: str
    target: str
    rationale: str
    estimated_impact: float | None
    confidence: str  # "high" | "medium" | "low"
    action: str | None


class OptimizerResult(BaseModel):
    scenario_id: uuid.UUID
    recommendations: list[OptimizerRecommendation]


# ─── Comparison ───────────────────────────────────────────────────────────────


class ScenarioCompareRequest(BaseModel):
    scenario_ids: list[uuid.UUID]


class ScenarioCompareItem(BaseModel):
    scenario_id: uuid.UUID
    scenario_name: str
    simulation: SimulationResultRead | None


class ScenarioCompareResult(BaseModel):
    items: list[ScenarioCompareItem]
