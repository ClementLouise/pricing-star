"""Heuristic optimizer — generates ranked recommendations from simulation data."""

from app.models.asset import Asset
from app.models.scenario import Scenario
from app.schemas.scenario import LeversConfig, RegulationsConfig
from app.schemas.simulation import OptimizerRecommendation, OptimizerResult, SimulationResultRead

# US-reference MIN-rule markets that benefit from post-MFN launch sequencing
_US_REF_MARKETS = {"BR", "MX", "CO", "CL", "AR"}


def generate_optimizer_result(
    simulation: SimulationResultRead | None,
    scenario: Scenario,
    asset: Asset,
) -> OptimizerResult:
    """Analyse simulation + scenario config and return ranked recommendations."""
    recs: list[OptimizerRecommendation] = []

    if simulation is None:
        return OptimizerResult(scenario_id=scenario.id, recommendations=[])

    regs = RegulationsConfig(**(scenario.regulations or {}))
    levers = LeversConfig(**(scenario.levers or {}))
    final_prices = simulation.final_prices or {}
    us_list = float(asset.us_list_price or 1)

    # Rule 1 — Method II vs Method I
    m1 = simulation.method_i_value
    m2 = simulation.method_ii_value
    if m1 and m2 and m2 < m1 and regs.guard.submit_method_ii:
        recs.append(
            OptimizerRecommendation(
                type="method_ii",
                title="Don't submit Method II — it lowers your benchmark",
                target="guard",
                rationale=(
                    f"Method II (${m2:,.0f}) < Method I (${m1:,.0f}). "
                    "Voluntary submission would replace Method I as the applicable benchmark, "
                    "increasing your rebate obligation."
                ),
                estimated_impact=abs(m1 - m2) * 0.5,  # rough benefit from not submitting
                confidence="high",
                action="guard.submit_method_ii=false",
            )
        )

    # Rule 2 — Method I anchor protection
    anchor = simulation.method_i_anchor
    if anchor and anchor not in levers.price_floors and (regs.guard.active or regs.globe.active):
        anchor_price = final_prices.get(anchor, 0)
        recs.append(
            OptimizerRecommendation(
                type="anchor_protection",
                title=f"Set price floor for {anchor} (Method I anchor)",
                target=anchor,
                rationale=(
                    f"{anchor} @ ${anchor_price:,.0f} sets your Method I benchmark at ${m1:,.0f}. "
                    "A price floor prevents IRP cascade or HTA concessions from eroding the anchor"
                    ", which would shift Method I to a cheaper country."
                ),
                estimated_impact=m1 * 0.04 if m1 else None,  # 4% NPV benefit estimate
                confidence="high",
                action=f"price_floor.{anchor}=0.65",
            )
        )

    # Rule 3 — GR withdrawal candidate
    if "GR" not in levers.withdrawals and "GR" in final_prices:
        gr_price = final_prices["GR"]
        if gr_price / us_list < 0.32:
            recs.append(
                OptimizerRecommendation(
                    type="withdrawal",
                    title="Evaluate Greece withdrawal",
                    target="GR",
                    rationale=(
                        f"GR price (${gr_price:,.0f}) is {gr_price / us_list:.0%} of US list. "
                        "Greece uses a basket-of-baskets IRP rule; its low price may cascade to "
                        "SE, DK, and other referencing markets. Withdrawal could lift the floor."
                    ),
                    estimated_impact=None,
                    confidence="medium",
                    action="withdrawal.GR",
                )
            )

    # Rule 4 — DE opt-in warning
    if levers.de_opt_in:
        recs.append(
            OptimizerRecommendation(
                type="de_opt_in",
                title="Reconsider DE opt-in (Medizinforschungsgesetz)",
                target="DE",
                rationale=(
                    "DE opt-in discloses a lower confidential price that propagates to ~12 markets "
                    "referencing Germany (AT, BE, CH, CZ, DK, FI, HU, NL, NO, PL, SE, SK). "
                    "For most assets with broad ex-US footprint, cascade harm ($2-4B) "
                    "far exceeds confidential rebate savings (~$200-400M)."
                ),
                estimated_impact=None,
                confidence="high",
                action="de_opt_in=false",
            )
        )

    # Rule 5 — Late-launch sequencing for US-reference markets
    candidates = [
        c
        for c in _US_REF_MARKETS
        if c in final_prices and c not in levers.delayed_launches and c not in levers.withdrawals
    ]
    for code in candidates[:2]:
        recs.append(
            OptimizerRecommendation(
                type="launch_sequencing",
                title=f"Delay {code} launch to post-MFN implementation",
                target=code,
                rationale=(
                    f"{code} uses US-reference pricing (MIN rule). Launching before MFN "
                    "locks in the current US list price as a reference. Launching after MFN "
                    "starts the reference at the MFN-reduced US net — permanently lower. "
                    "Delay protects long-term ex-US revenue."
                ),
                estimated_impact=None,
                confidence="medium",
                action=f"delay.{code}",
            )
        )

    # Rule 6 — Method II submission opportunity
    if m1 and m2 and m2 > m1 and not regs.guard.submit_method_ii and regs.guard.active:
        recs.append(
            OptimizerRecommendation(
                type="method_ii_opportunity",
                title="Voluntarily submit Method II (reduces rebate)",
                target="guard",
                rationale=(
                    f"Method II (${m2:,.0f}) > Method I (${m1:,.0f}). "
                    "Submitting Method II would use the lower M.I as applicable benchmark — "
                    "no change. Pre-emptive compliance builds credibility with CMS."
                ),
                estimated_impact=0.0,
                confidence="low",
                action="guard.submit_method_ii=true",
            )
        )

    # Sort by estimated_impact descending (None = low priority)
    recs.sort(key=lambda r: abs(r.estimated_impact or 0), reverse=True)
    return OptimizerResult(scenario_id=scenario.id, recommendations=recs)
