"""
TEST CASE V1.1 — VX-CFTR-NG (corrected PPP convention)
=======================================================

ERRATA from V1.0 (April 2026):
- V1.0 used PPP adjusters as DIVIDE (price / adjuster)
- Per CMS proposed Guard rule: PPP adjuster = US_GDP_PPP / Country_GDP_PPP (>= 1)
  and price is MULTIPLIED by the adjuster
- Source: CMS Federal Register Dec 2025; Hogan Lovells brief Dec 30, 2025

Re-running the same simulation with the correct multiply convention.
The strategic narrative is preserved, but specific anchor identification changes.
"""

GDP_PPP_ADJUSTERS = {
    "US": 1.000, "CA": 1.332, "FR": 1.385, "DE": 1.202, "IT": 1.422, "JP": 1.638,
    "UK": 1.438, "AU": 1.256, "KR": 1.498, "NL": 1.065, "ES": 1.560, "AT": 1.193,
    "BE": 1.197, "CZ": 1.573, "IE": 1.000, "NO": 1.000, "SE": 1.193, "CH": 1.000,
    "DK": 1.024, "IL": 1.596,
    "BR": 2.85, "MX": 2.60, "AR": 3.10, "CO": 2.95, "CL": 2.20,
    "CN": 2.40, "IN": 4.20,
    "PL": 1.85, "HU": 1.85, "RO": 1.85, "SK": 1.573, "BG": 1.85, "GR": 1.385, "PT": 1.385, "FI": 1.193,
    "SA": 1.90, "AE": 1.75
}

US_MODEL_BASKETS = {
    "GENEROUS": ["UK", "FR", "DE", "IT", "CA", "JP", "DK", "CH"],
    "GUARD": ["AU","AT","BE","CA","CZ","DK","FR","DE","IE","IL","IT","JP","NL","NO","KR","ES","SE","CH","UK"],
    "GLOBE": ["AU","AT","BE","CA","CZ","DK","FR","DE","IE","IL","IT","JP","NL","NO","KR","ES","SE","CH","UK"]
}

IRP_RULES = {
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
    "BR": {"basket": ["US", "CA", "FR", "DE", "IT", "ES", "UK", "PT", "GR", "AU", "JP", "CH"], "rule": "min", "discount": 0.10},
    "MX": {"basket": ["US", "CA", "FR", "DE", "IT", "ES", "UK"], "rule": "avg", "discount": 0.30},
    "CL": {"basket": ["US", "CA", "FR", "DE", "IT", "ES", "UK"], "rule": "avg", "discount": 0.30},
    "CO": {"basket": ["US", "CA", "MX", "BR", "CL"], "rule": "avg", "discount": 0.30},
    "AR": {"basket": ["US", "BR", "MX", "CL"], "rule": "avg", "discount": 0.40},
    "SA": {"basket": ["DE", "FR", "UK", "IT", "ES", "JP"], "rule": "avg", "discount": 0.20},
    "AE": {"basket": ["DE", "FR", "UK", "IT", "ES", "SA"], "rule": "avg", "discount": 0.15},
    "CN": {"basket": [], "rule": "negotiated", "discount": 0.65},
    "IN": {"basket": [], "rule": "negotiated", "discount": 0.85},
}

CONFIDENTIAL_REBATES = {
    "US": 0.50, "DE": 0.85, "FR": 0.75, "UK": 0.80, "IT": 0.70, "ES": 0.70,
    "NL": 0.85, "BE": 0.78, "AT": 0.85, "CH": 0.95, "DK": 0.80, "SE": 0.85,
    "NO": 0.80, "FI": 0.85, "GR": 0.55, "PT": 0.70, "PL": 0.80, "CZ": 0.85,
    "HU": 0.80, "RO": 0.75, "SK": 0.85, "BG": 0.85, "JP": 0.95, "KR": 0.85,
    "AU": 0.80, "BR": 0.75, "MX": 0.85, "CL": 0.85, "CO": 0.80, "AR": 0.70,
    "SA": 0.85, "AE": 0.85, "CN": 0.95, "IN": 0.95, "CA": 0.75, "IE": 0.80,
    "IL": 0.80,
}

GUARD_PHASEIN = {2026: -0.10, 2027: -0.20, 2028: -0.30, 2029: -0.30, 2030: -0.30}
GLOBE_PHASEIN = {2026: -0.10, 2027: -0.20, 2028: -0.30, 2029: -0.35, 2030: -0.35}

ASSET = {
    "name": "VX-CFTR-NG",
    "us_list_price": 370000,
    "us_net_share": 0.50,
    "launch_year": 2027,
    "patent_expiry": 2042,
    "us_patient_population": 30000,
    "ex_us_patient_population": 50000,
    "patient_capture_rate_at_peak": 0.60,
    "ramp_years": 5,
    "discount_rate": 0.10
}

INITIAL_EX_US_DISCOUNT = {
    "DE": 0.78, "FR": 0.72, "UK": 0.75, "IT": 0.68, "ES": 0.62, "NL": 0.78, "BE": 0.75,
    "AT": 0.74, "CH": 0.85, "DK": 0.74, "SE": 0.74, "NO": 0.78, "FI": 0.74,
    "GR": 0.55, "PT": 0.55, "PL": 0.50, "CZ": 0.55, "HU": 0.45, "RO": 0.45, "SK": 0.45, "BG": 0.40,
    "JP": 0.85, "KR": 0.65, "AU": 0.70,
    "BR": 0.50, "MX": 0.45, "CL": 0.50, "CO": 0.40, "AR": 0.35,
    "SA": 0.55, "AE": 0.65, "CN": 0.40, "IN": 0.10,
    "CA": 0.65, "IE": 0.78, "IL": 0.65,
}

VOLUMES = {
    "DE": 0.06, "FR": 0.06, "UK": 0.05, "IT": 0.05, "ES": 0.04, "NL": 0.02,
    "BE": 0.015, "AT": 0.01, "CH": 0.01, "DK": 0.01, "SE": 0.015, "NO": 0.01, "FI": 0.005,
    "GR": 0.01, "PT": 0.01, "PL": 0.025, "CZ": 0.01, "HU": 0.005, "RO": 0.01, "SK": 0.005, "BG": 0.003,
    "JP": 0.05, "KR": 0.025, "AU": 0.02,
    "BR": 0.06, "MX": 0.04, "CL": 0.005, "CO": 0.005, "AR": 0.005,
    "SA": 0.005, "AE": 0.003, "CN": 0.30, "IN": 0.05, "CA": 0.04, "IE": 0.005, "IL": 0.003,
}


# ─── CALC ENGINES (CORRECTED: multiply convention) ─────────────

def calculate_generous(prices):
    basket = US_MODEL_BASKETS["GENEROUS"]
    adj = []
    for c in basket:
        if c in prices and prices[c] is not None:
            ppp = GDP_PPP_ADJUSTERS.get(c, 1.0)
            adj.append((c, prices[c] * ppp, prices[c]))  # CORRECTED: multiply
    adj.sort(key=lambda x: x[1])
    if len(adj) >= 2:
        return {"price": adj[1][1], "country": adj[1][0], "raw": adj[1][2], "all": adj}
    return None


def calculate_guard_method_i(prices):
    basket = US_MODEL_BASKETS["GUARD"]
    adj = []
    for c in basket:
        if c in prices and prices[c] is not None:
            ppp = GDP_PPP_ADJUSTERS.get(c, 1.0)
            adj.append((c, prices[c] * ppp))  # CORRECTED: multiply
    if not adj:
        return None
    adj.sort(key=lambda x: x[1])
    return {"price": adj[0][1] * 1.02, "country": adj[0][0], "raw": adj[0][1], "all": adj}


def calculate_guard_method_ii(net_prices, volumes, year):
    basket = US_MODEL_BASKETS["GUARD"]
    weighted_sum = 0
    total_vol = 0
    for c in basket:
        if c in net_prices and c in volumes and volumes[c] > 0:
            ppp = GDP_PPP_ADJUSTERS.get(c, 1.0)
            adjusted = net_prices[c] * ppp  # CORRECTED: PPP at country level
            weighted_sum += adjusted * volumes[c]
            total_vol += volumes[c]
    if total_vol == 0:
        return None
    avg = weighted_sum / total_vol
    base = avg * 1.05
    return base * (1 + GUARD_PHASEIN.get(year, -0.30))


def calculate_globe_method_ii(net_prices, volumes, year):
    basket = US_MODEL_BASKETS["GLOBE"]
    weighted_sum = 0
    total_vol = 0
    for c in basket:
        if c in net_prices and c in volumes and volumes[c] > 0:
            ppp = GDP_PPP_ADJUSTERS.get(c, 1.0)
            adjusted = net_prices[c] * ppp
            weighted_sum += adjusted * volumes[c]
            total_vol += volumes[c]
    if total_vol == 0:
        return None
    avg = weighted_sum / total_vol
    base = avg * 1.05
    return base * (1 + GLOBE_PHASEIN.get(year, -0.35))


def apply_country_irp(country, current_prices):
    if country not in IRP_RULES:
        return current_prices.get(country)
    rule = IRP_RULES[country]
    if rule["rule"] == "negotiated":
        return current_prices.get("US", 0) * (1 - rule["discount"])
    basket_prices = [current_prices[c] for c in rule["basket"]
                     if c in current_prices and current_prices[c] is not None]
    if not basket_prices:
        return current_prices.get(country)
    if rule["rule"] == "min":
        ref = min(basket_prices)
    elif rule["rule"] == "avg_top3":
        ref = sum(sorted(basket_prices, reverse=True)[:3]) / 3
    else:
        ref = sum(basket_prices) / len(basket_prices)
    return ref * (1 - rule["discount"])


def run_cascade(initial_prices, max_iter=5):
    current = dict(initial_prices)
    for _ in range(max_iter):
        new_prices = dict(current)
        for c in IRP_RULES:
            if c == "US":
                continue
            np = apply_country_irp(c, current)
            if np is not None:
                new_prices[c] = min(current.get(c, np), np)
        max_change = max(
            (abs((new_prices[c] or 0) - (current.get(c) or 0)) / (current.get(c) or 1)
             for c in new_prices if current.get(c, 0) > 0),
            default=0
        )
        current = new_prices
        if max_change < 0.001:
            break
    return current


def project_volume(base, year, launch, peak, loe):
    if year < launch:
        return 0
    if year < peak:
        return base * (year - launch + 1) / (peak - launch + 1)
    if year < loe:
        return base
    if year >= loe + 5:
        return base * 0.10
    return base * (1 - 0.20 * (year - loe))


def compute_npv(country_prices):
    launch = ASSET["launch_year"]
    peak = launch + ASSET["ramp_years"]
    loe = ASSET["patent_expiry"]
    rate = ASSET["discount_rate"]
    total_ex_us = ASSET["ex_us_patient_population"] * ASSET["patient_capture_rate_at_peak"]
    npv = 0
    peak_rev = 0
    for year in range(launch, launch + 15):
        rev = 0
        us_vol = project_volume(ASSET["us_patient_population"] * ASSET["patient_capture_rate_at_peak"],
                                 year, launch, peak, loe)
        us_net = country_prices.get("US", ASSET["us_list_price"]) * ASSET["us_net_share"]
        rev += us_vol * us_net
        for c, vs in VOLUMES.items():
            cv = project_volume(total_ex_us * vs, year, launch, peak, loe)
            lp = country_prices.get(c)
            if lp is None:
                continue
            ns = CONFIDENTIAL_REBATES.get(c, 0.80)
            rev += cv * lp * ns
        if year == peak:
            peak_rev = rev
        npv += rev / ((1 + rate) ** (year - launch))
    return {"npv": npv, "peak_revenue": peak_rev}


def build_initial_prices(us_price):
    prices = {"US": us_price}
    for c, d in INITIAL_EX_US_DISCOUNT.items():
        prices[c] = us_price * d
    return prices


# ─── RUN SCENARIOS ──────────────────────────────────────────

def scenario_baseline():
    initial = build_initial_prices(ASSET["us_list_price"])
    prices = run_cascade(initial)
    return {"name": "BASELINE (Pre-MFN)", "prices": prices, "us_price": ASSET["us_list_price"]}


def scenario_generous():
    initial = build_initial_prices(ASSET["us_list_price"])
    prices = run_cascade(initial)
    g = calculate_generous(prices)
    return {
        "name": "GENEROUS only (Medicaid MFN, 2027)",
        "prices": prices, "us_price": ASSET["us_list_price"],
        "us_medicaid_price": g["price"] if g else None,
        "generous": g
    }


def scenario_generous_guard(year=2028):
    initial = build_initial_prices(ASSET["us_list_price"])
    prices = run_cascade(initial)
    g = calculate_generous(prices)
    m1 = calculate_guard_method_i(prices)
    net_prices = {c: p * CONFIDENTIAL_REBATES.get(c, 0.80) for c, p in prices.items()}
    m2 = calculate_guard_method_ii(net_prices, VOLUMES, year)
    benchmark = max(m1["price"] if m1 else 0, m2 or 0)
    us_net_baseline = ASSET["us_list_price"] * ASSET["us_net_share"]
    rebate = max(0, us_net_baseline - benchmark)
    return {
        "name": f"GENEROUS + GUARD (Medicaid + Part D, {year})",
        "prices": prices, "us_price": ASSET["us_list_price"],
        "us_medicaid_price": g["price"] if g else None,
        "method_i": m1, "method_ii": m2, "benchmark": benchmark,
        "rebate": rebate, "effective_us_net": us_net_baseline - rebate,
    }


def scenario_full(year=2029):
    initial = build_initial_prices(ASSET["us_list_price"])
    prices = run_cascade(initial)
    g = calculate_generous(prices)
    m1 = calculate_guard_method_i(prices)
    net_prices = {c: p * CONFIDENTIAL_REBATES.get(c, 0.80) for c, p in prices.items()}
    m2 = calculate_guard_method_ii(net_prices, VOLUMES, year)
    g2 = calculate_globe_method_ii(net_prices, VOLUMES, year)
    bench_d = max(m1["price"] if m1 else 0, m2 or 0)
    bench_b = max(m1["price"] if m1 else 0, g2 or 0)
    us_net_baseline = ASSET["us_list_price"] * ASSET["us_net_share"]
    rebate_d = max(0, us_net_baseline - bench_d)
    rebate_b = max(0, us_net_baseline - bench_b)
    weighted_rebate = 0.90 * rebate_d + 0.10 * rebate_b
    return {
        "name": f"FULL MFN (G+G+G, {year})",
        "prices": prices, "us_price": ASSET["us_list_price"],
        "us_medicaid_price": g["price"] if g else None,
        "method_i": m1, "method_ii": m2, "globe_method_ii": g2,
        "benchmark_d": bench_d, "benchmark_b": bench_b,
        "weighted_rebate": weighted_rebate,
        "effective_us_net": us_net_baseline - weighted_rebate,
    }


# ─── EXECUTE ───────────────────────────────────────────────

print("=" * 80)
print("VX-CFTR-NG TEST V1.1 (CORRECTED PPP CONVENTION)")
print("=" * 80)
print(f"Asset: {ASSET['name']}")
print(f"US list: ${ASSET['us_list_price']:,}")
print(f"PPP convention: MULTIPLY (per CMS Federal Register Dec 2025)")
print()

scenarios = [
    scenario_baseline(),
    scenario_generous(),
    scenario_generous_guard(2028),
    scenario_full(2029)
]

results = []
for s in scenarios:
    npv_calc = compute_npv(s["prices"])
    if "effective_us_net" in s:
        ratio = s["effective_us_net"] / (ASSET["us_list_price"] * ASSET["us_net_share"])
        adjusted_npv = npv_calc["npv"] * 0.60 * ratio + npv_calc["npv"] * 0.40
        npv_calc["npv"] = adjusted_npv
    elif s.get("us_medicaid_price"):
        commercial_net = ASSET["us_list_price"] * ASSET["us_net_share"]
        blended = 0.9 * commercial_net + 0.1 * s["us_medicaid_price"]
        ratio = blended / commercial_net
        adjusted_npv = npv_calc["npv"] * 0.60 * ratio + npv_calc["npv"] * 0.40
        npv_calc["npv"] = adjusted_npv
    results.append({**s, **npv_calc})


for i, r in enumerate(results):
    print(f"\n{'─' * 80}")
    print(f"SCENARIO {i+1}: {r['name']}")
    print(f"{'─' * 80}")

    if i == 0:
        print(f"  US LIST: ${r['us_price']:,}")
        print(f"  US NET: ${r['us_price'] * 0.5:,.0f}")
    else:
        if r.get("us_medicaid_price"):
            print(f"  US MEDICAID (Generous 2nd-lowest PPP-adjusted): ${r['us_medicaid_price']:,.0f}")
            saving = (r['us_price'] - r['us_medicaid_price']) / r['us_price'] * 100
            print(f"     -> {saving:.1f}% below US list ({r['generous']['country']} sets ref)" if r.get('generous') else "")
        if "effective_us_net" in r:
            print(f"  US EFFECTIVE NET: ${r['effective_us_net']:,.0f}")
            base = r['us_price'] * 0.5
            erosion = (base - r['effective_us_net']) / base * 100
            print(f"     -> {erosion:.1f}% erosion vs Pre-MFN")
        if r.get("method_i"):
            print(f"  Method I: ${r['method_i']['price']:,.0f} (anchor: {r['method_i']['country']})")
        if r.get("method_ii"):
            print(f"  Method II: ${r['method_ii']:,.0f}")
        if "benchmark" in r:
            print(f"  Benchmark: ${r['benchmark']:,.0f}")
        elif "benchmark_d" in r:
            print(f"  Part D benchmark: ${r['benchmark_d']:,.0f}")
            print(f"  Part B benchmark: ${r['benchmark_b']:,.0f}")

    print(f"\n  -> 15-Y NPV: ${r['npv']/1e9:.2f}B")
    print(f"  -> Peak revenue: ${r['peak_revenue']/1e9:.2f}B")


print(f"\n\n{'=' * 80}")
print("NPV COMPARISON (V1.1 corrected)")
print(f"{'=' * 80}")
baseline_npv = results[0]["npv"]
for r in results:
    delta = r["npv"] - baseline_npv
    pct = (delta / baseline_npv * 100) if baseline_npv else 0
    print(f"  {r['name']:<55} ${r['npv']/1e9:>6.2f}B  ({pct:+.1f}%)")


print(f"\n{'=' * 80}")
print("METHOD I ANCHOR ANALYSIS — TOP 5 CANDIDATES")
print(f"{'=' * 80}")
m1 = results[2]["method_i"]
if m1 and m1.get("all"):
    print(f"\n  {'Rank':<6} {'Country':<6} {'Nominal':<14} {'PPP':<6} {'PPP-adjusted':<16} {'Status'}")
    initial_test = build_initial_prices(ASSET["us_list_price"])
    prices_after = run_cascade(initial_test)
    for idx, (c, adj) in enumerate(m1["all"][:7]):
        nom = prices_after.get(c, 0)
        ppp = GDP_PPP_ADJUSTERS.get(c, 1.0)
        status = "<- ANCHOR" if idx == 0 else f"#{idx+1}"
        print(f"  #{idx+1:<5} {c:<6} ${nom:>10,.0f}   {ppp:<6.3f} ${adj:>12,.0f}   {status}")


# Save
import json
with open("/home/claude/test_results_v11.json", "w") as f:
    json.dump({
        "version": "1.1",
        "errata_note": "PPP convention corrected to multiply (CMS Federal Register Dec 2025)",
        "asset": ASSET,
        "scenarios": [{
            "name": r["name"],
            "us_price": r["us_price"],
            "us_medicaid_price": r.get("us_medicaid_price"),
            "effective_us_net": r.get("effective_us_net"),
            "method_i_price": r["method_i"]["price"] if r.get("method_i") else None,
            "method_i_anchor": r["method_i"]["country"] if r.get("method_i") else None,
            "method_ii": r.get("method_ii"),
            "benchmark": r.get("benchmark") or r.get("benchmark_d"),
            "weighted_rebate": r.get("weighted_rebate"),
            "npv": r["npv"],
            "peak_revenue": r["peak_revenue"],
        } for r in results]
    }, f, indent=2, default=str)
print(f"\n  -> Saved /home/claude/test_results_v11.json")
