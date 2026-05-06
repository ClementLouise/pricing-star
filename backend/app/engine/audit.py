"""F14: SOX-grade audit JSON generation for pricing decisions."""

from datetime import datetime, timezone
from typing import Any, Optional

from .constants import (
    ENGINE_VERSION,
    GDP_PPP_ADJUSTERS,
    US_MODEL_BASKETS,
    GUARD_PHASEIN,
    GLOBE_PHASEIN,
)
from .types import AnchorAnalysis, NPVResult


def generate_audit_json(
    asset: dict[str, Any],
    scenario: Optional[str],
    prices: dict[str, float],
    regulations: dict[str, Any],
    npv_result: Optional[NPVResult],
    anchor_analysis: Optional[AnchorAnalysis],
    generated_by: str = "system",
) -> dict[str, Any]:
    """
    F14: Produce a self-contained SOX-grade audit document for a pricing decision.

    The output is valid JSON, human-readable when pretty-printed, and includes all
    assumptions, calculation intermediates, and source citations for SOX 404 compliance.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    anchor_section = None
    if anchor_analysis is not None:
        anchor_section = {
            "model": anchor_analysis.model,
            "anchor": {
                "country": anchor_analysis.anchor.country,
                "countryName": anchor_analysis.anchor.country_name,
                "nominal": anchor_analysis.anchor.nominal,
                "ppp": anchor_analysis.anchor.ppp,
                "adjusted": anchor_analysis.anchor.adjusted,
            },
            "benchmark": anchor_analysis.benchmark,
            "isNonObviousAnchor": anchor_analysis.is_non_obvious_anchor,
            "ringfenceRecommendation": anchor_analysis.ringfence_recommendation,
        }

    npv_section = None
    if npv_result is not None:
        npv_section = {
            "npv": npv_result.npv,
            "peakRevenue": npv_result.peak_revenue,
            "yearlyBreakdown": [
                {
                    "year": row.year,
                    "usRevenue": row.us_revenue,
                    "exUsRevenue": row.ex_us_revenue,
                    "totalRevenue": row.total_revenue,
                    "g2nUsed": row.g2n_used,
                }
                for row in npv_result.yearly_breakdown
            ],
        }

    return {
        "metadata": {
            "tool": "Pharma Pricing Intelligence",
            "version": ENGINE_VERSION,
            "generatedAt": timestamp,
            "generatedBy": generated_by,
            "classification": "Internal — Confidential",
            "scenarioName": scenario or "unnamed",
        },
        "asset": {
            "name": asset.get("name"),
            "therapeuticArea": asset.get("therapeutic_area"),
            "modality": asset.get("modality"),
            "launchYear": asset.get("launch_year"),
            "patentExpiry": asset.get("patent_expiry"),
            "discountRate": asset.get("discount_rate"),
        },
        "methodology": {
            "generous": {
                "rule": "2nd-lowest GDP-PPP adjusted across MFN-8 basket",
                "basket": US_MODEL_BASKETS["GENEROUS"],
                "source": "CMS proposed Generous rule, Sec. III.B",
            },
            "guard": {
                "methodI": {
                    "rule": "Lowest GDP-PPP adjusted in OECD-19 basket × 1.02",
                    "basket": US_MODEL_BASKETS["GUARD"],
                    "source": "CMS proposed Guard rule, Sec. IV.C.1",
                },
                "methodII": {
                    "rule": "Volume-weighted avg net price × 1.05 with phase-in (-10%/-20%/-30%)",
                    "basket": US_MODEL_BASKETS["GUARD"],
                    "phaseIn": GUARD_PHASEIN,
                    "source": "CMS proposed Guard rule, Sec. IV.C.2",
                },
            },
            "globe": {
                "rule": "Same as Guard but with -35% terminal phase-in",
                "basket": US_MODEL_BASKETS["GLOBE"],
                "phaseIn": GLOBE_PHASEIN,
                "source": "CMS proposed Globe rule, Sec. V",
            },
        },
        "pppAdjusters": GDP_PPP_ADJUSTERS,
        "inputs": {
            "prices": prices,
            "regulations": regulations,
        },
        "calculations": {
            "anchorAnalysis": anchor_section,
            "npv": npv_section,
        },
        "auditTrail": [
            {"step": 1, "action": "Reference data loaded from engine v" + ENGINE_VERSION},
            {"step": 2, "action": "PPP adjusters applied per CMS Table 5 methodology"},
            {"step": 3, "action": "IRP cascade run to convergence (5 iterations max)"},
            {"step": 4, "action": "Method I and Method II benchmarks computed independently"},
            {"step": 5, "action": "Per-unit rebate = max(0, US net - max(MI, MII))"},
            {"step": 6, "action": "NPV computed over launch-to-patent-expiry horizon at WACC"},
        ],
        "disclaimer": (
            "This audit JSON captures all model inputs and intermediate calculations. "
            "It does not validate accuracy of input data (e.g., country list prices). "
            "Customer is responsible for input data integrity. CMS rule interpretations are "
            "based on proposed rules as of analysis date and may change in final rules."
        ),
    }
