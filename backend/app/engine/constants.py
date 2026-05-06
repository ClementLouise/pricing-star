"""
Reference data constants for the calculation engine.
Source: CMS proposed rules (Federal Register Dec 2025), V1.7 PharmaPricingTool.
All values are loaded as module-level constants; hot-reload is handled at the service layer.
"""

ENGINE_VERSION: str = "1.7.0"

# GDP (PPP) Adjusters — CMS Table 5 illustrative 2024
# Convention: adjuster = US_GDP_PPP / Country_GDP_PPP (lower-bound 1.000)
# Price is MULTIPLIED by adjuster to normalize to US-equivalent purchasing power.
GDP_PPP_ADJUSTERS: dict[str, float] = {
    "US": 1.000, "CA": 1.332, "FR": 1.385, "DE": 1.202, "IT": 1.422, "JP": 1.638,
    "UK": 1.438, "AU": 1.256, "KR": 1.498, "NL": 1.065, "ES": 1.560, "AT": 1.193,
    "BE": 1.197, "CZ": 1.573, "IE": 1.000, "NO": 1.000, "SE": 1.193, "CH": 1.000,
    "DK": 1.024, "IL": 1.596,
    # Non-OECD-19 markets (IRP cascade only; not MFN benchmarks)
    "BR": 2.85, "MX": 2.60, "AR": 3.10, "CO": 2.95, "CL": 2.20,
    "CN": 2.40, "IN": 4.20,
    "PL": 1.85, "HU": 1.85, "RO": 1.85, "SK": 1.573, "BG": 1.85,
    "GR": 1.385, "PT": 1.385, "FI": 1.193,
    "SA": 1.90, "AE": 1.75, "TR": 3.20,
}

# Country baskets per US regulatory model
US_MODEL_BASKETS: dict[str, list[str]] = {
    "GENEROUS": ["UK", "FR", "DE", "IT", "CA", "JP", "DK", "CH"],  # G7 minus US + DK + CH
    "GUARD": ["AU", "AT", "BE", "CA", "CZ", "DK", "FR", "DE", "IE", "IL", "IT", "JP",
              "NL", "NO", "KR", "ES", "SE", "CH", "UK"],            # OECD-19
    "GLOBE": ["AU", "AT", "BE", "CA", "CZ", "DK", "FR", "DE", "IE", "IL", "IT", "JP",
              "NL", "NO", "KR", "ES", "SE", "CH", "UK"],            # OECD-19 (same as GUARD)
}

# Method II phase-in schedules (CMS proposed rules)
GUARD_PHASEIN: dict[int, float] = {
    2026: -0.10, 2027: -0.20, 2028: -0.30, 2029: -0.30, 2030: -0.30, 2031: -0.30,
}
GLOBE_PHASEIN: dict[int, float] = {
    2026: -0.10, 2027: -0.20, 2028: -0.30, 2029: -0.35, 2030: -0.35, 2031: -0.35,
}

# IRP rules per country — simplified for deterministic cascade calculation.
# Format: {basket: list[str], rule: str, discount: float}
# rule values: "avg" | "min" | "negotiated" (CN/IN only)
# discount: fraction deducted from basket reference (0.0 = no discount)
# Source: run_oncmab_test_v20.py (V2.0 reference, validated against fixtures)
IRP_RULES: dict[str, dict] = {
    "DE": {"basket": ["UK", "FR", "IT", "ES", "NL", "BE", "AT", "DK", "SE", "FI"], "rule": "avg", "discount": 0.05},
    "FR": {"basket": ["UK", "DE", "IT", "ES"], "rule": "avg", "discount": 0.10},
    "UK": {"basket": ["DE", "FR", "IT", "ES", "NL"], "rule": "avg", "discount": 0.08},
    "IT": {"basket": ["DE", "FR", "ES", "UK"], "rule": "avg", "discount": 0.12},
    "ES": {"basket": ["DE", "FR", "IT", "UK"], "rule": "avg", "discount": 0.10},
    "NL": {"basket": ["DE", "FR", "UK", "BE"], "rule": "avg", "discount": 0.05},
    "BE": {"basket": ["DE", "FR", "NL", "IT"], "rule": "avg", "discount": 0.05},
    "AT": {"basket": ["DE", "FR", "IT", "BE", "NL"], "rule": "avg", "discount": 0.05},
    "CH": {"basket": ["DE", "FR", "IT", "AT", "NL", "UK", "DK", "SE", "JP"], "rule": "avg", "discount": 0.10},
    "DK": {"basket": ["DE", "FR", "UK", "SE", "NO", "FI"], "rule": "avg", "discount": 0.05},
    "SE": {"basket": ["DE", "DK", "NO", "FI"], "rule": "avg", "discount": 0.05},
    "NO": {"basket": ["DE", "DK", "SE", "FI"], "rule": "avg", "discount": 0.05},
    "FI": {"basket": ["DE", "DK", "SE", "NO"], "rule": "avg", "discount": 0.05},
    "GR": {"basket": ["DE", "FR", "IT", "ES", "PT"], "rule": "min", "discount": 0.0},
    "PT": {"basket": ["ES", "FR", "IT"], "rule": "avg", "discount": 0.0},
    "PL": {"basket": ["DE", "FR", "IT", "ES", "UK", "CZ", "SK", "HU"], "rule": "avg", "discount": 0.10},
    "CZ": {"basket": ["DE", "AT", "IT", "ES", "UK", "FR", "PL", "SK", "HU"], "rule": "avg", "discount": 0.10},
    "HU": {"basket": ["DE", "AT", "PL", "CZ", "SK"], "rule": "avg", "discount": 0.15},
    "RO": {"basket": ["DE", "FR", "IT", "ES", "PL", "CZ"], "rule": "min", "discount": 0.05},
    "SK": {"basket": ["DE", "AT", "PL", "CZ", "HU"], "rule": "avg", "discount": 0.10},
    "BG": {"basket": ["DE", "FR", "IT", "ES", "GR", "RO"], "rule": "min", "discount": 0.10},
    "JP": {"basket": ["US", "UK", "DE", "FR"], "rule": "avg", "discount": 0.0},
    "KR": {"basket": ["US", "UK", "DE", "FR", "IT", "JP", "CH"], "rule": "avg", "discount": 0.05},
    "AU": {"basket": ["UK", "DE", "FR", "IT", "ES", "CA"], "rule": "avg", "discount": 0.0},
    "BR": {"basket": ["US", "CA", "FR", "DE", "IT", "ES", "UK", "PT", "GR", "AU", "JP", "CH"],
           "rule": "min", "discount": 0.10},
    "MX": {"basket": ["US", "CA", "FR", "DE", "IT", "ES", "UK"], "rule": "avg", "discount": 0.30},
    "CL": {"basket": ["US", "CA", "FR", "DE", "IT", "ES", "UK"], "rule": "avg", "discount": 0.30},
    "CO": {"basket": ["US", "CA", "MX", "BR", "CL"], "rule": "avg", "discount": 0.30},
    "AR": {"basket": ["US", "BR", "MX", "CL"], "rule": "avg", "discount": 0.40},
    "SA": {"basket": ["DE", "FR", "UK", "IT", "ES", "JP"], "rule": "avg", "discount": 0.20},
    "AE": {"basket": ["DE", "FR", "UK", "IT", "ES", "SA"], "rule": "avg", "discount": 0.15},
    "CN": {"basket": [], "rule": "negotiated", "discount": 0.65},
    "IN": {"basket": [], "rule": "negotiated", "discount": 0.85},
}

# Default G2N (gross-to-net) ratios per country.
# Used as fallback in resolve_g2n when no scenario-specific value is provided.
# Source: run_oncmab_test_v20.py CONFIDENTIAL_REBATES (validated against fixtures)
DEFAULT_G2N: dict[str, float] = {
    "US": 0.50, "DE": 0.85, "FR": 0.75, "UK": 0.80, "IT": 0.70, "ES": 0.70,
    "NL": 0.85, "BE": 0.78, "AT": 0.85, "CH": 0.95, "DK": 0.80, "SE": 0.85,
    "NO": 0.80, "FI": 0.85, "GR": 0.55, "PT": 0.70, "PL": 0.80, "CZ": 0.85,
    "HU": 0.80, "RO": 0.75, "SK": 0.85, "BG": 0.85, "JP": 0.95, "KR": 0.85,
    "AU": 0.80, "BR": 0.75, "MX": 0.85, "CL": 0.85, "CO": 0.80, "AR": 0.70,
    "SA": 0.85, "AE": 0.85, "CN": 0.95, "IN": 0.95, "CA": 0.75, "IE": 0.80,
    "IL": 0.80, "TR": 0.70,
}

COUNTRY_NAMES: dict[str, str] = {
    "US": "United States", "CA": "Canada", "MX": "Mexico",
    "BR": "Brazil", "AR": "Argentina", "CO": "Colombia", "CL": "Chile",
    "UK": "United Kingdom", "FR": "France", "DE": "Germany", "IT": "Italy",
    "ES": "Spain", "NL": "Netherlands", "CH": "Switzerland", "AT": "Austria",
    "BE": "Belgium", "SE": "Sweden", "NO": "Norway", "DK": "Denmark",
    "IE": "Ireland", "PL": "Poland", "CZ": "Czechia", "TR": "Turkey",
    "JP": "Japan", "KR": "South Korea", "CN": "China", "IN": "India",
    "AU": "Australia", "IL": "Israel", "SA": "Saudi Arabia", "AE": "UAE",
    "EG": "Egypt", "ZA": "South Africa", "GR": "Greece", "PT": "Portugal",
    "HU": "Hungary", "RO": "Romania", "SK": "Slovakia", "BG": "Bulgaria",
    "FI": "Finland",
}

# Markets that reference Germany in their IRP basket — derived dynamically.
# Any country in IRP_RULES whose basket contains "DE".
DE_REFERENCING_MARKETS: list[str] = [
    c for c, rule in IRP_RULES.items()
    if "DE" in rule.get("basket", [])
]
