"""Reference data endpoints (read-only, shared) — per PRD §05."""

from fastapi import APIRouter

from app.engine.constants import (
    COUNTRY_NAMES,
    DEFAULT_G2N,
    GDP_PPP_ADJUSTERS,
    GLOBE_PHASEIN,
    GUARD_PHASEIN,
    IRP_RULES,
    US_MODEL_BASKETS,
)

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/countries")
async def list_countries() -> dict:
    items = []
    for code, name in COUNTRY_NAMES.items():
        rule = IRP_RULES.get(code)
        items.append(
            {
                "country_code": code,
                "name": name,
                "gdp_ppp_adjuster": GDP_PPP_ADJUSTERS.get(code, 1.0),
                "default_g2n_ratio": DEFAULT_G2N.get(code, 0.80),
                "in_oecd_19": code in US_MODEL_BASKETS.get("GUARD", []),
                "in_mfn_8": code in US_MODEL_BASKETS.get("GENEROUS", []),
                "irp_rule": rule,
            }
        )
    return {"items": items}


@router.get("/baskets")
async def get_baskets() -> dict:
    return dict(US_MODEL_BASKETS)


@router.get("/phase-ins")
async def get_phase_ins() -> dict:
    return {
        "GUARD": {str(k): v for k, v in GUARD_PHASEIN.items()},
        "GLOBE": {str(k): v for k, v in GLOBE_PHASEIN.items()},
    }
