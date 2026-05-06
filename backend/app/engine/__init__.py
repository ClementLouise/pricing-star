"""Pharma Pricing Intelligence calculation engine — V1.7.0."""

from .constants import ENGINE_VERSION
from .methods import (
    calculate_generous_price,
    calculate_guard_method_i,
    calculate_guard_method_ii,
    calculate_globe_method_i,
    calculate_globe_method_ii,
    calculate_guard_rebate,
    calculate_globe_rebate,
)
from .cascade import apply_country_irp, run_cascade
from .npv import project_volume, resolve_g2n, compute_npv
from .anchor import analyze_mfn_anchor
from .de_cascade import simulate_de_cascade
from .monte_carlo import monte_carlo_g2n
from .audit import generate_audit_json
from .types import (
    GenerousResult,
    MethodIResult,
    RebateResult,
    CascadeResult,
    AssetConfig,
    CountryData,
    ScenarioConfig,
    NPVResult,
    YearlyBreakdown,
    AnchorAnalysis,
    AnchorCountry,
    DECascadeResult,
    MarketImpact,
    MonteCarloResult,
)

__all__ = [
    "ENGINE_VERSION",
    # F1-F6
    "calculate_generous_price",
    "calculate_guard_method_i",
    "calculate_guard_method_ii",
    "calculate_globe_method_i",
    "calculate_globe_method_ii",
    "calculate_guard_rebate",
    "calculate_globe_rebate",
    # F7-F8
    "apply_country_irp",
    "run_cascade",
    # F9-F10
    "project_volume",
    "resolve_g2n",
    "compute_npv",
    # F11
    "analyze_mfn_anchor",
    # F12
    "simulate_de_cascade",
    # F13
    "monte_carlo_g2n",
    # F14
    "generate_audit_json",
    # Types
    "GenerousResult",
    "MethodIResult",
    "RebateResult",
    "CascadeResult",
    "AssetConfig",
    "CountryData",
    "ScenarioConfig",
    "NPVResult",
    "YearlyBreakdown",
    "AnchorAnalysis",
    "AnchorCountry",
    "DECascadeResult",
    "MarketImpact",
    "MonteCarloResult",
]
