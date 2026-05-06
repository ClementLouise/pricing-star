"""Simulation service — wires calc engine with persistence and audit trail."""
import uuid
from datetime import datetime, timezone
from time import monotonic

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.anchor import analyze_mfn_anchor
from app.engine.cascade import run_cascade
from app.engine.de_cascade import simulate_de_cascade
from app.engine.methods import calculate_guard_method_i, calculate_guard_method_ii, calculate_guard_rebate
from app.engine.npv import resolve_g2n as _resolve_g2n
from app.engine.monte_carlo import monte_carlo_g2n
from app.engine.npv import compute_npv
from app.engine.types import AssetConfig, CountryData as EngineCountryData, ScenarioConfig
from app.models.asset import Asset
from app.models.country_data import CountryData
from app.models.simulation_result import SimulationResult
from app.models.user import User
from app.repos.audit import AuditRepo
from app.repos.simulation_result import SimulationResultRepo
from app.schemas.simulation import (
    AnchorAnalysisResponse,
    AnchorCountryRead,
    DECascadeResponse,
    MarketImpactRead,
    MonteCarloResponse,
    SimulateResponse,
    SimulationResultRead,
    YearlyBreakdownItem,
)

ENGINE_VERSION = "1.7.0"


def _build_asset_config(asset: Asset) -> AssetConfig:
    """Map SQLAlchemy Asset to engine AssetConfig."""
    return AssetConfig(
        name=asset.name,
        us_list_price=float(asset.us_list_price or 0),
        us_net_share=float(asset.us_net_share or 0.50),
        launch_year=asset.launch_year or datetime.now(timezone.utc).year,
        patent_expiry=asset.loe_year or (asset.launch_year or 2027) + 13,
        us_patient_population=asset.us_patient_population or 0,
        ex_us_patient_population=asset.ex_us_patient_population or 0,
        patient_capture_rate_at_peak=float(asset.peak_capture_rate),
        ramp_years=asset.ramp_years,
        discount_rate=float(asset.discount_rate),
        part_b_share=float(asset.part_b_share),
    )


def _build_engine_prices(country_rows: list[CountryData]) -> dict[str, float]:
    """Extract list prices from DB rows into the engine's country→price dict."""
    return {
        row.country_code: float(row.list_price)
        for row in country_rows
        if row.launched and row.list_price is not None and not row.withdrawn
    }


def _build_scenario_config(
    country_rows: list[CountryData],
    g2n_overrides: dict[str, float] | None = None,
) -> ScenarioConfig:
    """Build ScenarioConfig from DB country rows for NPV computation."""
    country_data = {}
    for row in country_rows:
        if row.volume is not None:
            g2n_ts = None
            if row.g2n_time_series:
                g2n_ts = {int(k): float(v) for k, v in row.g2n_time_series.items()}
            base_g2n = float(row.g2n_ratio) if row.g2n_ratio is not None else 0.80
            if g2n_overrides and row.country_code in g2n_overrides:
                base_g2n = g2n_overrides[row.country_code]
            country_data[row.country_code] = EngineCountryData(
                volume_share=float(row.volume),
                g2n_ratio=base_g2n,
                g2n_time_series=g2n_ts,
            )
    return ScenarioConfig(country_data=country_data)


def _to_simulation_read(sim: SimulationResult) -> SimulationResultRead:
    return SimulationResultRead(
        simulation_id=sim.id,
        engine_version=sim.engine_version,
        computed_at=sim.computed_at,
        npv=float(sim.npv),
        peak_revenue=float(sim.peak_revenue) if sim.peak_revenue is not None else None,
        method_i_value=float(sim.method_i_value) if sim.method_i_value is not None else None,
        method_i_anchor=sim.method_i_anchor,
        method_ii_value=float(sim.method_ii_value) if sim.method_ii_value is not None else None,
        applicable_benchmark=float(sim.applicable_benchmark) if sim.applicable_benchmark is not None else None,
        per_unit_rebate=float(sim.per_unit_rebate) if sim.per_unit_rebate is not None else None,
        effective_us_net=float(sim.effective_us_net) if sim.effective_us_net is not None else None,
        cascade_iterations=sim.cascade_iterations,
        cascade_converged=sim.cascade_converged,
        final_prices=sim.final_prices,
        yearly_breakdown=[YearlyBreakdownItem(**row) for row in sim.yearly_breakdown],
        monte_carlo_result=sim.monte_carlo_result,
    )


async def run_simulation(
    asset: Asset,
    scenario_id: uuid.UUID,
    country_rows: list[CountryData],
    regulations: dict,
    user: User,
    db: AsyncSession,
    levers: dict | None = None,
    cascade_config: dict | None = None,
) -> SimulateResponse:
    """Full pipeline: cascade → Method I → NPV → persist → audit."""
    start = monotonic()
    levers = levers or {}

    asset_config = _build_asset_config(asset)
    initial_prices = _build_engine_prices(country_rows)
    if not initial_prices:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No launched countries with list prices — cannot simulate",
        )

    # Include US price
    if asset.us_list_price:
        initial_prices["US"] = float(asset.us_list_price)

    # F7-F8: IRP cascade
    cascade_cfg = cascade_config or {}
    cascade_max_iterations = int(cascade_cfg.get("max_iterations", 5))
    cascade_result = run_cascade(initial_prices, max_iterations=cascade_max_iterations, options=cascade_cfg)

    # EC-CALC-01: only enforce strict convergence when explicitly requested via cascade_config.
    # Default behavior matches V1.7: run up to max_iterations and use the result regardless.
    if not cascade_result.converged and cascade_cfg.get("require_convergence", False):
        audit_repo = AuditRepo(db)
        await audit_repo.log(
            tenant_id=asset.tenant_id,
            user_id=user.id,
            action="simulation.cascade_failed",
            payload={
                "scenario_id": str(scenario_id),
                "iterations_run": cascade_result.iterations,
                "max_iterations": cascade_max_iterations,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "cascade_did_not_converge",
                "message": (
                    f"IRP cascade did not converge after {cascade_result.iterations} iterations. "
                    "Increase max_iterations in cascade_config or review market price data."
                ),
            },
        )

    cascaded_prices = cascade_result.final

    # F1/F3: Method I
    method_i_result = calculate_guard_method_i(cascaded_prices)
    method_i_value = method_i_result.price if method_i_result else None
    method_i_anchor = method_i_result.country if method_i_result else None

    guard_config = regulations.get("guard", {})
    submit_method_ii = guard_config.get("submit_method_ii", False)
    guard_active = guard_config.get("active", False)
    us_net_price = float(asset.us_list_price or 0) * float(asset.us_net_share or 0.5)

    # F9-F10: build scenario config (with optional GR clawback stress)
    g2n_overrides = {"GR": 0.55} if levers.get("gr_clawback_stress", False) else None
    scenario_cfg = _build_scenario_config(country_rows, g2n_overrides=g2n_overrides)
    vol_dict = {c: cd.volume_share for c, cd in scenario_cfg.country_data.items()}

    # F2/F5: EC-CALC-17 — Method II and rebate computed per year using time-variant G2N.
    # Per PRD §04 F3: caller resolves net_prices[country] = list_price × resolve_g2n(country, year)
    # before passing to calculate_guard_method_ii.
    launch_year = asset_config.launch_year
    horizon = min(asset_config.patent_expiry - launch_year + 1, 15)

    method_ii_value: float | None = None   # representative value for persisted summary (year 1)
    applicable_benchmark: float | None = None
    effective_us_net: float = us_net_price  # summary value for persisted record (year 1)

    us_net_schedule: dict[int, float] | None = None

    if guard_active:
        us_net_schedule = {}
        for year in range(launch_year, launch_year + horizon):
            if submit_method_ii:
                net_prices_year = {}
                for c, lp in cascaded_prices.items():
                    if c not in scenario_cfg.country_data:
                        continue
                    try:
                        g2n_y = _resolve_g2n(c, year, scenario_cfg, {})
                    except ValueError:
                        g2n_y = scenario_cfg.country_data[c].g2n_ratio or 0.80
                    net_prices_year[c] = lp * g2n_y
                method_ii_year = calculate_guard_method_ii(net_prices_year, vol_dict, year=year)
            else:
                method_ii_year = None

            rebate_year = calculate_guard_rebate(
                us_net_price=us_net_price,
                method_i=method_i_value,
                method_ii=method_ii_year,
                use_method_ii=submit_method_ii,
            )
            us_net_schedule[year] = max(us_net_price - rebate_year.rebate_per_unit, 0)

            # Keep year-1 values for the persisted simulation summary columns
            if year == launch_year + 1:
                method_ii_value = method_ii_year
                applicable_benchmark = rebate_year.benchmark
                effective_us_net = us_net_schedule[year]

    npv_result = compute_npv(
        cascaded_prices,
        asset_config,
        scenario_cfg,
        us_net_schedule=us_net_schedule,
    )

    elapsed_ms = int((monotonic() - start) * 1000)

    # Persist
    sim_record = SimulationResult(
        id=uuid.uuid4(),
        tenant_id=asset.tenant_id,
        scenario_id=scenario_id,
        computed_by=user.id,
        engine_version=ENGINE_VERSION,
        npv=npv_result.npv,
        peak_revenue=npv_result.peak_revenue,
        method_i_value=method_i_value,
        method_i_anchor=method_i_anchor,
        method_ii_value=method_ii_value,
        applicable_benchmark=applicable_benchmark,
        per_unit_rebate=round(us_net_price - effective_us_net, 6),
        effective_us_net=effective_us_net,
        cascade_iterations=cascade_result.iterations,
        cascade_converged=cascade_result.converged,
        final_prices={k: float(v) for k, v in cascaded_prices.items()},
        yearly_breakdown=[
            {
                "year": row.year,
                "us_revenue": row.us_revenue,
                "ex_us_revenue": row.ex_us_revenue,
                "total_net": row.us_revenue + row.ex_us_revenue,
                "discounted": row.us_revenue + row.ex_us_revenue,
                "rebate_per_unit": row.rebate_per_unit,
                "effective_us_net": row.effective_us_net,
            }
            for row in npv_result.yearly_breakdown
        ],
    )
    sim_repo = SimulationResultRepo(db)
    await sim_repo.create(sim_record)

    # Audit
    audit_repo = AuditRepo(db)
    await audit_repo.log(
        tenant_id=asset.tenant_id,
        user_id=user.id,
        action="scenario.simulate",
        payload={
            "scenario_id": str(scenario_id),
            "engine_version": ENGINE_VERSION,
            "npv": npv_result.npv,
            "cascade_iterations": cascade_result.iterations,
        },
    )

    return SimulateResponse(
        simulation_id=sim_record.id,
        engine_version=ENGINE_VERSION,
        computed_at=sim_record.computed_at or datetime.now(timezone.utc),
        computed_in_ms=elapsed_ms,
        results=_to_simulation_read(sim_record),
    )


def compute_anchor_analysis(
    final_prices: dict[str, float],
    model: str = "GUARD",
) -> AnchorAnalysisResponse | None:
    """F11: MFN anchor analysis — stateless, no DB needed."""
    result = analyze_mfn_anchor(final_prices, model=model)
    if result is None:
        return None

    def _to_read(c) -> AnchorCountryRead:  # type: ignore[no-untyped-def]
        return AnchorCountryRead(
            country=c.country,
            country_name=c.country_name,
            nominal=c.nominal,
            ppp=c.ppp,
            adjusted=c.adjusted,
        )

    return AnchorAnalysisResponse(
        model=result.model,
        anchor=_to_read(result.anchor),
        second=_to_read(result.second) if result.second else None,
        benchmark=result.benchmark,
        anchor_gap=result.anchor_gap,
        anchor_gap_pct=result.anchor_gap_pct,
        is_non_obvious_anchor=result.is_non_obvious_anchor,
        nominal_lowest=_to_read(result.nominal_lowest) if result.nominal_lowest else None,
        ringfence_recommendation=result.ringfence_recommendation,
        all_ranked=[_to_read(c) for c in result.all_ranked],
    )


def run_monte_carlo(
    final_prices: dict[str, float],
    country_rows: list[CountryData],
    n: int = 500,
    sigma: float = 0.05,
    model: str = "GUARD",
    seed: int | None = None,
) -> MonteCarloResponse | None:
    """F13: Monte Carlo G2N — confidence intervals on Method II benchmark."""
    base_g2n = {
        row.country_code: float(row.g2n_ratio) if row.g2n_ratio is not None else 0.80
        for row in country_rows
    }
    launch_year = min(
        (int(k) for row in country_rows if row.g2n_time_series for k in row.g2n_time_series),
        default=2027,
    )
    result = monte_carlo_g2n(
        base_prices=final_prices,
        base_g2n=base_g2n,
        year=launch_year + 1,
        model=model,
        n=n,
        sigma=sigma,
        seed=seed,
    )
    if result is None:
        return None
    return MonteCarloResponse(
        samples_n=result.samples_n,
        mean=result.mean,
        p05=result.p05,
        p50=result.p50,
        p95=result.p95,
        range=result.range,
        sigma_input=result.sigma_input,
    )


def compute_de_cascade(
    current_prices: dict[str, float],
    opt_in_rebate_pct: float = 0.09,
) -> DECascadeResponse:
    """F12: German confidential opt-in cascade simulator — stateless."""
    result = simulate_de_cascade(current_prices, opt_in_rebate_pct=opt_in_rebate_pct)
    return DECascadeResponse(
        opt_in_rebate_pct=result.opt_in_rebate_pct,
        de_price_before=result.de_price_before,
        de_price_after=result.de_price_after,
        de_disclosed_delta=result.de_disclosed_delta,
        market_impacts=[
            MarketImpactRead(
                country=m.country,
                country_name=m.country_name,
                before=m.before,
                after=m.after,
                delta=m.delta,
                delta_pct=m.delta_pct,
            )
            for m in result.market_impacts
        ],
        referencing_markets_count=result.referencing_markets_count,
        actually_impacted_count=result.actually_impacted_count,
        cascade_iterations=result.cascade_iterations,
    )
