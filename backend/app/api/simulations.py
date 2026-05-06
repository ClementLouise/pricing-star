"""Simulation execution endpoints — per PRD §05."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_role
from app.database import get_db
from app.models.user import User
from app.repos.asset import AssetRepo
from app.repos.scenario import CountryDataRepo, ScenarioRepo
from app.repos.simulation_result import SimulationResultRepo
from app.schemas.simulation import (
    AnchorAnalysisResponse,
    DECascadeRequest,
    DECascadeResponse,
    MonteCarloRequest,
    MonteCarloResponse,
    OptimizerResult,
    ScenarioCompareRequest,
    ScenarioCompareResult,
    ScenarioCompareItem,
    SimulateResponse,
    SimulationResultRead,
    SimulationSummary,
    YearlyBreakdownItem,
)
from app.services.optimizer import generate_optimizer_result
from app.services.simulation import (
    compute_anchor_analysis,
    compute_de_cascade,
    run_monte_carlo,
    run_simulation,
)

router = APIRouter(tags=["simulations"])

_viewer = require_role(["admin", "editor", "viewer"])
_editor = require_role(["admin", "editor"])


async def _resolve_scenario_and_asset(
    scenario_id: uuid.UUID,
    user: User,
    db: AsyncSession,
):
    """Helper: resolve scenario → asset, enforce tenant isolation."""
    scenario = await ScenarioRepo(db).get(scenario_id, user.tenant_id)
    if scenario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    asset = await AssetRepo(db).get(scenario.asset_id, user.tenant_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return scenario, asset


@router.post("/scenarios/{scenario_id}/simulate", response_model=SimulateResponse)
async def simulate(
    scenario_id: uuid.UUID,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> SimulateResponse:
    scenario, asset = await _resolve_scenario_and_asset(scenario_id, user, db)

    if asset.us_list_price is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Asset is missing us_list_price — cannot simulate",
        )

    country_rows = await CountryDataRepo(db).list_for_scenario(scenario_id)

    return await run_simulation(
        asset=asset,
        scenario_id=scenario_id,
        country_rows=country_rows,
        regulations=scenario.regulations,
        levers=scenario.levers,
        cascade_config=scenario.cascade_config,
        user=user,
        db=db,
    )


@router.get("/scenarios/{scenario_id}/simulations", response_model=list[SimulationSummary])
async def list_simulations(
    scenario_id: uuid.UUID,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> list[SimulationSummary]:
    scenario = await ScenarioRepo(db).get(scenario_id, user.tenant_id)
    if scenario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    items = await SimulationResultRepo(db).list_for_scenario(scenario_id, user.tenant_id)
    return [
        SimulationSummary(
            simulation_id=s.id,
            computed_at=s.computed_at,
            engine_version=s.engine_version,
            npv=float(s.npv),
            method_i_anchor=s.method_i_anchor,
        )
        for s in items
    ]


@router.get("/simulations/{simulation_id}", response_model=SimulationResultRead)
async def get_simulation(
    simulation_id: uuid.UUID,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> SimulationResultRead:
    from app.schemas.simulation import YearlyBreakdownItem

    sim = await SimulationResultRepo(db).get(simulation_id, user.tenant_id)
    if sim is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found")

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


@router.post("/scenarios/{scenario_id}/anchor-analysis", response_model=AnchorAnalysisResponse)
async def anchor_analysis(
    scenario_id: uuid.UUID,
    model: str = Query("GUARD", pattern="^(GUARD|GLOBE|GENEROUS)$"),
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> AnchorAnalysisResponse:
    """F11: MFN anchor analysis on the latest cascaded prices."""
    scenario, asset = await _resolve_scenario_and_asset(scenario_id, user, db)

    # Get most recent simulation for final prices, or cascade on-the-fly
    sims = await SimulationResultRepo(db).list_for_scenario(scenario_id, user.tenant_id, limit=1)
    if sims:
        final_prices = sims[0].final_prices
    else:
        from app.engine.cascade import run_cascade
        from app.repos.scenario import CountryDataRepo
        country_rows = await CountryDataRepo(db).list_for_scenario(scenario_id)
        initial = {r.country_code: float(r.list_price) for r in country_rows if r.list_price}
        if asset.us_list_price:
            initial["US"] = float(asset.us_list_price)
        final_prices = run_cascade(initial).final

    result = compute_anchor_analysis(final_prices, model=model)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot compute anchor: unknown model '{model}' or insufficient prices",
        )
    return result


@router.post("/scenarios/{scenario_id}/de-cascade", response_model=DECascadeResponse)
async def de_cascade(
    scenario_id: uuid.UUID,
    payload: DECascadeRequest,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> DECascadeResponse:
    """F12: German confidential opt-in cascade simulation."""
    scenario, asset = await _resolve_scenario_and_asset(scenario_id, user, db)

    sims = await SimulationResultRepo(db).list_for_scenario(scenario_id, user.tenant_id, limit=1)
    if sims:
        current_prices = sims[0].final_prices
    else:
        from app.engine.cascade import run_cascade
        from app.repos.scenario import CountryDataRepo
        country_rows = await CountryDataRepo(db).list_for_scenario(scenario_id)
        initial = {r.country_code: float(r.list_price) for r in country_rows if r.list_price}
        if asset.us_list_price:
            initial["US"] = float(asset.us_list_price)
        current_prices = run_cascade(initial).final

    return compute_de_cascade(current_prices, opt_in_rebate_pct=payload.opt_in_rebate_pct)


@router.post("/scenarios/{scenario_id}/monte-carlo", response_model=MonteCarloResponse)
async def monte_carlo(
    scenario_id: uuid.UUID,
    payload: MonteCarloRequest,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> MonteCarloResponse:
    """F13: Monte Carlo G2N uncertainty — returns p05/p50/p95 confidence intervals."""
    scenario, asset = await _resolve_scenario_and_asset(scenario_id, user, db)

    sims = await SimulationResultRepo(db).list_for_scenario(scenario_id, user.tenant_id, limit=1)
    if not sims:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No simulation found — run simulation first",
        )
    final_prices = sims[0].final_prices

    from app.repos.scenario import CountryDataRepo
    country_rows = await CountryDataRepo(db).list_for_scenario(scenario_id)

    result = run_monte_carlo(
        final_prices=final_prices,
        country_rows=country_rows,
        n=payload.n,
        sigma=payload.sigma,
        model=payload.model,
        seed=payload.seed,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Monte Carlo produced no valid samples — check country data configuration",
        )
    return result


@router.post("/scenarios/{scenario_id}/optimize", response_model=OptimizerResult)
async def optimize(
    scenario_id: uuid.UUID,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> OptimizerResult:
    """Heuristic recommendations based on latest simulation + scenario config."""
    scenario, asset = await _resolve_scenario_and_asset(scenario_id, user, db)
    sims = await SimulationResultRepo(db).list_for_scenario(scenario_id, user.tenant_id, limit=1)

    latest: SimulationResultRead | None = None
    if sims:
        s = sims[0]
        latest = SimulationResultRead(
            simulation_id=s.id,
            engine_version=s.engine_version,
            computed_at=s.computed_at,
            npv=float(s.npv),
            peak_revenue=float(s.peak_revenue) if s.peak_revenue is not None else None,
            method_i_value=float(s.method_i_value) if s.method_i_value is not None else None,
            method_i_anchor=s.method_i_anchor,
            method_ii_value=float(s.method_ii_value) if s.method_ii_value is not None else None,
            applicable_benchmark=float(s.applicable_benchmark) if s.applicable_benchmark is not None else None,
            per_unit_rebate=float(s.per_unit_rebate) if s.per_unit_rebate is not None else None,
            effective_us_net=float(s.effective_us_net) if s.effective_us_net is not None else None,
            cascade_iterations=s.cascade_iterations,
            cascade_converged=s.cascade_converged,
            final_prices=s.final_prices,
            yearly_breakdown=[YearlyBreakdownItem(**row) for row in s.yearly_breakdown],
            monte_carlo_result=s.monte_carlo_result,
        )

    return generate_optimizer_result(latest, scenario, asset)


@router.post("/assets/{asset_id}/compare", response_model=ScenarioCompareResult)
async def compare_scenarios(
    asset_id: uuid.UUID,
    payload: ScenarioCompareRequest,
    user: User = Depends(_viewer),
    db: AsyncSession = Depends(get_db),
) -> ScenarioCompareResult:
    """Return latest simulation for each requested scenario (same asset, same tenant)."""
    asset = await AssetRepo(db).get(asset_id, user.tenant_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    if len(payload.scenario_ids) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot compare more than 5 scenarios at once",
        )

    items: list[ScenarioCompareItem] = []
    sim_repo = SimulationResultRepo(db)

    for sid in payload.scenario_ids:
        scenario = await ScenarioRepo(db).get(sid, user.tenant_id)
        if scenario is None or scenario.asset_id != asset_id:
            continue
        sims = await sim_repo.list_for_scenario(sid, user.tenant_id, limit=1)
        sim_read: SimulationResultRead | None = None
        if sims:
            s = sims[0]
            sim_read = SimulationResultRead(
                simulation_id=s.id,
                engine_version=s.engine_version,
                computed_at=s.computed_at,
                npv=float(s.npv),
                peak_revenue=float(s.peak_revenue) if s.peak_revenue is not None else None,
                method_i_value=float(s.method_i_value) if s.method_i_value is not None else None,
                method_i_anchor=s.method_i_anchor,
                method_ii_value=float(s.method_ii_value) if s.method_ii_value is not None else None,
                applicable_benchmark=float(s.applicable_benchmark) if s.applicable_benchmark is not None else None,
                per_unit_rebate=float(s.per_unit_rebate) if s.per_unit_rebate is not None else None,
                effective_us_net=float(s.effective_us_net) if s.effective_us_net is not None else None,
                cascade_iterations=s.cascade_iterations,
                cascade_converged=s.cascade_converged,
                final_prices=s.final_prices,
                yearly_breakdown=[YearlyBreakdownItem(**row) for row in s.yearly_breakdown],
                monte_carlo_result=s.monte_carlo_result,
            )
        items.append(ScenarioCompareItem(
            scenario_id=sid,
            scenario_name=scenario.name,
            simulation=sim_read,
        ))

    return ScenarioCompareResult(items=items)
