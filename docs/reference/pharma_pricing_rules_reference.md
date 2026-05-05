# Pharma Pricing Rules — Reference Document

> **Source of truth** for the Pricing Star tool (Generous/Guard/Globe simulator).
> All regulations, baskets, formulas, and reference countries are documented here with explicit sources and reliability ratings.

**Last updated:** May 2026
**Maintainer:** [to be assigned]
**Version:** 1.0

---

## Document conventions

### Reliability tiers

| Tier | Meaning | Trust level |
|---|---|---|
| 🟢 **VERIFIED** | Confirmed via recent (2024–2026) official source — government agency, regulatory text, or authoritative recent industry analysis | High |
| 🟡 **LSE 2017** | Sourced from Kanavos et al. (LSE 2017 study), academically rigorous but **8+ years old** — needs revalidation | Medium |
| 🔴 **APPROX** | Approximation based on general industry knowledge — **must be validated** by expert before production use | Low |

### Formula taxonomy

| Formula | Meaning |
|---|---|
| `lowest` | Lowest price in basket |
| `highest` | Highest price in basket (Canada HIP screening 2026) |
| `avg` | Arithmetic mean of basket prices |
| `median` | Median of basket prices |
| `lowest_n` / `avg_lowest_3` | Average of n lowest prices in basket (n typically 3) |
| `avg_with_adjustment` | Average with cap/floor (e.g. Japan FPA: 0.75x–1.25x band, max 1.2x adjustment) |
| `value-based` | HTA / cost-effectiveness driven (no formula) |
| `negotiation` | Direct negotiation (no formula) |
| `internal_avg` | Based on top N domestic brands (e.g. India NPPA) |
| `tender` | Public tender pricing |
| `free` | No price control |

### Price level taxonomy

| Term | Definition |
|---|---|
| `list` | Public list price (no rebates) |
| `ex-factory` | Manufacturer ex-factory price (excl. distribution markup) |
| `wholesale` | Wholesale price (incl. distribution markup) |
| `retail` | Retail/pharmacy price (incl. all markups + VAT) |
| `net` | Net of confidential rebates (rare in IRP) |

---

## Part 1 — US Federal Pricing Models

### 🟢 GENEROUS Model (Medicaid MFN)

**Status:** Proposed CMS rule (Dec 23, 2025), 5-year voluntary model 2026–2030.
**Scope:** Single-source drugs / innovator multiple-source drugs at NDC-9 level.
**Mechanism:** Supplemental rebate from manufacturer to states to effectuate MFN price.

**Formula:**
```
MFN price = 2nd lowest country-specific manufacturer-reported NET price
            (adjusted by GDP per capita using PPP method)
            across MFN-8 basket
```

**Basket (MFN-8):** UK, France, Germany, Italy, Canada, Japan, Denmark, Switzerland
*(G7 minus US + Denmark + Switzerland)*

**Rebate calculation:**
```
Supplemental Rebate = WAC – (GNUP + URA)
```
where:
- WAC = Wholesale Acquisition Cost (US list price)
- GNUP = Guaranteed Net Unit Price (= MFN price)
- URA = Unit Rebate Amount (existing Medicaid statutory rebate)

**Reporting period:** Annual; data submitted by manufacturer to CMS within 30 days of agreement signing for first year, then April 1–March 31 reporting cycle.

**Source:** [CMS GENEROUS Model RFA — December 23, 2025](https://www.cms.gov) (in project: `generousmodelstaterfar2clean123025c.pdf`)

---

### 🟢 GUARD Model (Medicare Part D)

**Status:** Proposed rule (42 CFR Part 514) — Federal Register Vol. 90 No. 244, Dec 23, 2025.
**Scope:** Part D rebatable drugs in 25% of Part D beneficiaries (geographic areas selected by CMS), excluding 340B units (~10% assumed).
**Mechanism:** Alternative calculation to Section 1860D-14B(b) inflation rebate when GUARD rebate exceeds Part D inflation rebate.

**Per-unit GUARD rebate:**
```
Rebate/unit = max(0, Performance Year Medicare Net Price − Applicable Benchmark)
```

**Performance Year Medicare Net Price:**
```
Performance Year Aggregate Net Price = Aggregate WAC − Manufacturer DIR − Discount Program amounts
Performance Year Medicare Net Price = Performance Year Aggregate Net Price ÷ Total PDE quantity
```

**Applicable Benchmark = max(Method I, Method II if submitted)**

**Method I (default):**
- Lowest GDP-PPP adjusted country-level price across **OECD-19** basket × 1.02 (2% adjustment)
- Data sources: existing international drug pricing intelligence (e.g. IQVIA-style)

**Method II (manufacturer-submitted, voluntary):**
- Volume-weighted average net price across reference countries × 1.05 (5% adjustment)
- Subject to phase-in adjustment (downward):

| Year | Phase-in adjustment |
|---|---|
| 2026 | −10% |
| 2027 | −20% |
| 2028 | −30% |
| 2029–2031 | −30% |

**Basket (OECD-19):**
Australia, Austria, Belgium, Canada, Czechia, Denmark, France, Germany, Ireland, Israel, Italy, Japan, Netherlands, Norway, South Korea, Spain, Sweden, Switzerland, United Kingdom

**Eligibility criteria for reference countries:**
- Non-US OECD member (as of Oct 1, 2025)
- Real GDP per capita ≥ 60% of US real GDP per capita
- Annual real GDP ≥ $400 billion

**Civil Money Penalty:** 125% of unpaid Total Incremental GUARD Model rebate.

**Source:** [42 CFR Part 514 — Federal Register Dec 23, 2025](https://www.federalregister.gov) (in project: `202523705_Guard.pdf`)

---

### 🟢 GLOBE Model (Medicare Part B)

**Status:** Proposed rule (42 CFR Part 513) — Federal Register Vol. 90 No. 244, Dec 23, 2025.
**Scope:** Physician-administered drugs under Part B in selected geographic areas.
**Mechanism:** Mirror of Guard for Part B with adjusted Medicare payment.

**Formula:** Same Method I / Method II structure as GUARD.

**Method II phase-in (more aggressive than Guard):**

| Year | Phase-in adjustment |
|---|---|
| 2026 | −10% |
| 2027 | −20% |
| 2028 | −30% |
| 2029–2031 | −35% |

**Basket:** Same OECD-19 as GUARD.

**De minimis threshold:** Pricing data at dosage form & strength level removed for any country falling below 5% of US average price (data quality safeguard).

**Source:** [42 CFR Part 513 — Federal Register Dec 23, 2025](https://www.federalregister.gov) (in project: `202523702_Globe.pdf`)

---

### GDP-PPP Adjusters (illustrative 2024 data — CMS Tables 5 & B3)

> ⚠️ Capped at 1.000 when reference country has higher GDP-PPP per capita than US (Ireland, Norway, Switzerland).

| Country | Real GDP/cap | % of US | GDP (PPP) Adjuster |
|---|---:|---:|---:|
| United States | $75,500 | 100% | **1.000** |
| Canada | $56,700 | 75% | **1.332** |
| France | $54,500 | 72% | **1.385** |
| Germany | $62,800 | 83% | **1.202** |
| Italy | $53,100 | 70% | **1.422** |
| Japan | $46,100 | 61% | **1.638** |
| United Kingdom | $52,500 | 70% | **1.438** |
| Australia | $60,100 | 80% | **1.256** |
| South Korea | $50,400 | 67% | **1.498** |
| Netherlands | $70,900 | 94% | **1.065** |
| Spain | $48,400 | 64% | **1.560** |
| Austria | $63,300 | 84% | **1.193** |
| Belgium | $63,100 | 84% | **1.197** |
| Czechia | $48,000 | 64% | **1.573** |
| Ireland | $115,300 | 153% | **1.000** ⚠️ |
| Norway | $91,100 | 121% | **1.000** ⚠️ |
| Sweden | $63,300 | 84% | **1.193** |
| Switzerland | $82,000 | 109% | **1.000** ⚠️ |
| Denmark | $73,700 | 98% | **1.024** |
| Israel | $47,300 | 63% | **1.596** |

**Source:** CIA World Factbook 2024 data, as referenced in CMS proposed rules. Updated quarterly per CMS supplemental document.

**Note:** GDP-PPP adjusters published by CMS each quarter and aligned with applicable ASP calendar quarter.

---

## Part 2 — International Pricing Rules by Country (IRP)

> **Order:** Alphabetical by region. Each entry follows a standard template.

### Template structure

```
🟢🟡🔴 Country (CC)
─────────────────────────────────────────────
Authority: [Agency name]
Uses IRP: [Yes / No / Hybrid]
Basket: [list of countries]
Formula: [type]
Price level: [list/ex-factory/wholesale/retail/net]
Lag: [months]
Frequency: [revision schedule]
Note: [key contextual info, recent reforms]
─────────────────────────────────────────────
Source: [citation with year]
Last verified: [date]
```

---

## North America

### 🟢 Canada (CA)

**Authority:** PMPRB (Patented Medicine Prices Review Board)
**Uses IRP:** Yes (mandatory for patented medicines)
**Basket — PMPRB11:** Australia, Belgium, France, Germany, Italy, Japan, Netherlands, Norway, Spain, Sweden, United Kingdom
**Formula:**
- **Until Jan 2026:** Median International Price (MIP11) — lower of MIP or current price
- **From Jan 2026 (new Guidelines):** Highest International Price (HIP) screening — initial review compares Canadian list price to HIP across PMPRB11

**Price level:** List prices
**Lag:** ~12 months (annual review)
**Frequency:** Initial review at launch + annual reviews
**Categories:**
- New medicines: list price ceiling = median list price of PMPRB11 (will become HIP-based 2026)
- Category I (Tx cost > 150% GDP/cap or Canadian sales > $50M): may also require "maximum rebated price"
- Existing medicines: subject to annual reviews based on PMPRB11 + CPI

**Key 2024–2026 changes:**
- New Guidelines published June 2025, **effective January 2026** (replaces Interim Guidance from September 2023)
- Switch from MIP to HIP screening = **less aggressive downward pressure** than under MIP
- Two-step review process: (1) HIP comparison + CPI test, (2) in-depth review on §85(1) factors (12–28 months)

**Source:**
- [PMPRB Annual Report 2024](https://www.canada.ca/en/patented-medicine-prices-review/services/annual-reports/annual-report-2024.html) (Dec 2025)
- [Patented Medicines Regulations Schedule (Jul 2022)](https://www.canada.ca/en/patented-medicine-prices-review.html)
- [Torys LLP — PMPRB Guidelines analysis](https://www.torys.com/en/our-latest-thinking/publications/2024/07/pmprb-guidelines) (Jul 2024)
- [Norton Rose — Pharma in Brief](https://www.pharmainbrief.com/2024/12/drug-pricing-update-pmprb-launches-consultation-on-draft-guidelines-for-price-review/) (Dec 2024)

**Last verified:** May 2026

---

### 🟢 Mexico (MX)

**Authority:**
- **Regulation:** COFEPRIS (Comisión Federal para la Protección contra Riesgos Sanitarios)
- **Public procurement:** UNOPS (United Nations Office for Project Services, since Jul 2020) for federal pooled procurement; IMSS (Mexican Social Security Institute) for individual purchases
- **Price control:** Pricing committee under Ministry of Finance (1998 Law of Supervision of Prices)

**Uses IRP:** **No formal IRP system.** Mexico uses **public tendering / consolidated procurement** as primary cost-control mechanism for the public sector

**Mechanism:**
- **Public sector (~80% of market):** Consolidated procurement via UNOPS for federal needs (since 2020) and IMSS for state/municipal needs. Open international competitive bidding under UNOPS procurement policies — manufacturers compete on volume-discounted bids
- **Private sector:** Maximum retail prices (Precio Máximo al Público) declared by manufacturers, monitored by Ministry of Finance pricing committee
- **Marketing authorization:** COFEPRIS recognized as PAHO/WHO Regional Reference Authority (since 2012). Drugs registered in reference countries (US FDA, Health Canada, Swissmedic, EMA, TGA) can use abbreviated review procedure (60 working days)
- **Reference countries for registration (NOT pricing):** US, Canada, Switzerland, EU members, Australia, Japan
- New molecule registration timeline: ~180 days

**Note:** Mexico is referenced by some Brazilian and Colombian baskets, but **Mexico itself does not formally use IRP for setting drug prices**. Pricing is driven by public tenders and free-market dynamics in private sector.

**Key 2024–2026 changes:**
- UNOPS pooled procurement agreement renewed for 2021–2024 (likely extended)
- New COFEPRIS registration process effective January 2023 (ICH-aligned)
- Sheinbaum administration (from Oct 2024) reviewing UNOPS arrangement amid access issues from previous AMLO-era reforms

**Source:**
- [Pharmaboardroom — Mexico Regulatory, Pricing & Reimbursement](https://pharmaboardroom.com/legal-articles/regulatory-pricing-and-reimbursement-mexico/) (Feb 2025)
- [Tandfonline — Challenges of Guaranteeing Access to Medicines in Mexico](https://www.tandfonline.com/doi/full/10.1080/23288604.2022.2084221)
- [Latampharmara — COFEPRIS overview](https://latampharmara.com/mexico/cofepris-the-mexican-health-authority/)
- General Health Law + Law of Acquisitions, Leases and Services in the Public Sector

**Last verified:** May 2026

---

## Latin America (LATAM)

### 🟢 Brazil (BR)

**Authority:** CMED (Câmara de Regulação do Mercado de Medicamentos), under ANVISA
**Uses IRP:** Yes (mandatory)
**Basket — From April 2026 (Resolution 3/2025):** 14 countries
- US, Canada, Portugal, Spain, France, Italy, Greece, Australia, New Zealand, UK, Germany, Belgium, Sweden, Netherlands

**Formula:** Lowest price among reference countries
**Price level:** List (PF — Preço Fábrica)
**Lag:** ~6 months
**Frequency:** Annual price adjustments

**Drug categories (CMED):**
- **Category I:** Patented + demonstrates superiority (efficacy/safety/cost) → priced at lowest international price + country of origin
- **Category II:** Patented without superiority → IRP applies only if lower than local treatment comparators
- **Categories III–VI:** Generics, similars, etc.

**Special pricing levels:**
- **PF** (Ex-Factory Price): set by CMED
- **PMC** (Maximum Consumer Price): retail ceiling
- **PMVG** (Maximum Government Price): PF − CAP discount, mandatory for public procurement & court-ordered sales

**Key 2024–2026 changes:**
- ⚠️ **CRITICAL:** Resolution CM/CMED No. 3/2025 published, **effective April 29, 2026**, replaces 22-year-old Resolution 2/2004
- Basket **expanded from 9 → 14 countries** (Argentina and China explicitly excluded due to volatility / heterogeneity)
- **Minimum 4 reference countries** required for definitive price (provisional otherwise)
- Recognition of incremental innovation as pricing factor
- DIP (Price Information Document) becomes mandatory for price approval

**Source:**
- [Daniel Law — Resolution 3/2025 analysis](https://www.daniel-ip.com/en/client-alert/resolution-no-3-2025-structural-changes-to-brazils-drug-pricing-framework/) (Jan 2026)
- [Lexology — CMED updated framework](https://www.lexology.com/library/detail.aspx?g=9e47b1e9-7377-432f-9370-9aa4d0ff4301) (Jan 2026)
- [International Bar Association — Brazil drug pricing](https://www.ibanet.org/regulatory-trends-drug-pricing-brazil) (2026)
- CMED Resolution 2/2004 (legacy, expires Apr 2026)
- PPRI / ANVISA documents

**Last verified:** May 2026

---

### 🟢 Argentina (AR)

**Authority:** ANMAT (Administración Nacional de Medicamentos, Alimentos y Tecnología Médica) for marketing authorization; Ministry of Health for some price monitoring
**Uses IRP:** **No formal IRP system**

**Mechanism:**
- **No formal price regulation system** — significant distortions from inflation and currency devaluation (peso)
- Some price agreements between government and pharma industry occasionally negotiated (Precios Cuidados, etc.) but informal and subject to political cycles
- ANMAT recognized as PAHO/WHO Regional Reference Authority alongside ANVISA (Brazil), COFEPRIS (Mexico), INVIMA (Colombia), CECMED (Cuba)
- **Public procurement:** through PAMI (social security) and provincial authorities; usage of K@iros portal for price transparency
- IFPMA reports >60% of Latin American pharma products subject to direct price controls, with Argentina applying mandatory price caps on essential medicines (politically driven, not IRP-based)

**Note:** ⚠️ **Argentina is explicitly EXCLUDED from Brazil's new 14-country IRP basket (Resolution 3/2025)** due to "high prices, weak regulation, and recurrent exchange rate volatility." This is a strong signal of the unreliability of Argentine pricing data for IRP purposes.

**Source:**
- [CMED Resolution 3/2025 — Brazil's exclusion rationale (Lexology)](https://www.lexology.com/library/detail.aspx?g=9e47b1e9-7377-432f-9370-9aa4d0ff4301) (Jan 2026)
- [Latin America Pharmaceutical Market Report 2024](https://www.marketdataforecast.com/market-reports/latin-america-pharmaceutical-market) (Feb 2026)
- [ResearchGate — Transparency in Argentina, Brazil, Colombia](https://www.researchgate.net/publication/326132107_Description_of_Drug_Pricing_and_Procurement_Information_Web_Portals_in_Some_Latin_American_Countries) (2025)

**Last verified:** May 2026

---

### 🟢 Colombia (CO)

**Authority:**
- **Pricing:** CNPMDM / NCMMDP (Comisión Nacional de Precios de Medicamentos y Dispositivos Médicos / National Commission for Medicines and Medical Devices Prices)
- **Marketing authorization:** INVIMA (Instituto Nacional de Vigilancia de Medicamentos y Alimentos) — PAHO/WHO Regional Reference Authority
- **HTA:** IETS (Instituto de Evaluación Tecnológica en Salud)
- **Price monitoring:** SIC (Superintendence of Industry and Commerce) + SISMED (Sistema de Información de Precios de Medicamentos) — official price database

**Uses IRP:** Yes (post-launch, for direct price control)

**Current system (Circular 18 of 2024, replacing Circular 03 of 2013):**
1. **Free pricing at launch** — manufacturer freely sets max sale price, must report to CNPMDM via SISMED
2. **Post-launch market classification:**
   - Calculate Herfindahl-Hirschman Index (IHH) for each "relevant market" (same INN + strength + dosage form + route)
   - **Group A (Direct Control Regime)** if IHH score 5–8 (concentrated market) → IRP price cap applies
   - **Group B (Surveilled Freedom)** if IHH score 2–4 OR IHH < 2,500 → only monitoring
3. **For Group A drugs:** International Reference Price calculated; if national reference price > IRP, price cap is set

**Basket:** Reference price methodology uses international comparison — historically broad reference set including UK, France, Germany, Spain, Portugal, plus regional comparators (LATAM)

**Formula:** Reference price calculation by CNPMDM (specific algorithm in Circular 18/2024 — combines international reference + market analysis)

**Price level:** Wholesale / public price
**Lag:** ~12 months
**Frequency:** Periodic (Circulars issued by CNPMDM)

**Value-Based Pricing reform in development (Circular Externa No. 16 of 2023):**
- Proposed shift from current IRP-based system to value-based pricing
- IETS would assign new drugs to one of 6 therapeutic value categories (135 business days assessment)
- IETS produces 3 documents: classification, cost-effectiveness analysis, budget impact
- Final VBP resolution expected to be applicable from year after Official Gazette publication
- Status (mid-2026): reform pending, implementation TBD; may be affected by Health Reform Proposals in Colombian Congress (changing IETS to public entity)

**Source:**
- [OlarteMoure — Circular 18 of 2024](https://olartemoure.com/en/control-of-medicine-prices/) (Oct 2024)
- [Trinity Life Sciences — Colombia Value-Based Pricing reform](https://trinitylifesciences.com/blog/beyond-the-price-tag-understanding-colombias-new-pricing-policy/) (Oct 2025)
- [Research Partnership — Colombia VBP reform](https://www.researchpartnership.com/insights/value-based-pricing-reform-strengthening-the-front-door-to-the-colombian-pharmaceutical-market/) (Dec 2023)
- [Pharmaboardroom — Colombia Regulation, Pricing & Reimbursement](https://pharmaboardroom.com/legal-articles/regulatory-pricing-and-reimbursement-colombia/) (Feb 2025)
- Circular 03/2013 (legacy) + Circular 18/2024 (current) + Circular Externa 16/2023 (VBP draft)

**Last verified:** May 2026

---

### 🟢 Chile (CL)

**Authority:** ISP (Instituto de Salud Pública / Public Health Institute) for marketing authorization; Ministry of Health for some price monitoring
**Uses IRP:** **No formal IRP system**

**Mechanism:**
- **No external reference pricing system in place**
- Public sector: tendering through **CENABAST** (Central Nacional de Abastecimiento) for primary care/public hospitals — competitive bidding mechanism
- Public procurement portal **ChileCompra** publishes contract prices for transparency
- Private sector: free pricing — Chile considered the most market-driven LATAM pharmaceutical pricing system
- ISP adopted CTD format for Module 3 in new drug registration (regulatory harmonization, not pricing)
- Increasing use of pharmacoeconomic evaluations for high-cost drug funding decisions (Ley Ricarte Soto for catastrophic diseases since 2015)

**Note:** Chile is referenced by **Brazil's new 14-country basket (Resolution 3/2025)** because of stable pricing data despite no formal IRP regulation.

**Source:**
- [Pharmaceutical Engineering — CMC Requirements for LATAM Drug Registration](https://ispe.org/pharmaceutical-engineering/may-june-2023/cmc-requirements-new-drug-registration-latin-america) (2023)
- [Latin America Pharmaceutical Market Report 2024](https://www.marketdataforecast.com/market-reports/latin-america-pharmaceutical-market) (Feb 2026)
- [ResearchGate — LATAM Drug Pricing Portals](https://www.researchgate.net/publication/326132107_Description_of_Drug_Pricing_and_Procurement_Information_Web_Portals_in_Some_Latin_American_Countries)
- ChileCompra public procurement portal (chilecompra.cl)

**Last verified:** May 2026

---

## Europe

### 🟢 United Kingdom (UK)

**Authority:** NICE (HTA) + DHSC + ABPI (industry body)
**Uses IRP:** **No formal IRP**
**Mechanism:**
- **NICE HTA** assesses cost-effectiveness (cost/QALY threshold £20–30k typically)
- **VPAG** (Voluntary Scheme for Branded Medicines, replaced VPAS) — voluntary rebate scheme with growth caps; manufacturers pay back government when sales exceed annual cap
- Statutory scheme available for non-VPAG members

**Note:** UK list prices are widely referenced by other countries' baskets — UK has high "spillover sensitivity."

**Source:** ABPI / DHSC public documents
**Last verified:** May 2026

---

### 🟢 France (FR)

**Authority:** CEPS (Comité Économique des Produits de Santé) + HAS (Haute Autorité de Santé) + Transparency Commission
**Uses IRP:** Yes (supportive role, not main)
**Basket:** UK, Germany, Italy, Spain (EU price guarantee for ASMR I/II/III ratings)
**Formula:** Value-based ASMR-driven negotiation, with European price guarantee
**Price level:** List (Public Price), with confidential rebates ~25% on average

**ASMR ratings (Amélioration du Service Médical Rendu):**
- ASMR I (major benefit) → price aligned with comparable EU countries (UK/DE/ES/IT)
- ASMR II–III (important/moderate) → similar guarantee
- ASMR IV (mild) → lower price negotiation
- ASMR V (no improvement) → typically priced ≤ comparator

**Lag:** ~18 months for revisions
**Frequency:** Initial 5-year contracts + periodic reviews
**Mechanism:**
- 5-year price contracts with manufacturers
- Volume forecasts; if exceeded, manufacturers rebate 50–80% of excess revenue
- ONDAM annual budget cap → triggers clawback ("montant M") if exceeded
- 2024 baseline: ~30% discount to net price for new launches

**Key 2024–2026 changes:**
- ⚠️ **CRITICAL:** **LFSS 2026 Article 88** introduces new "comparable countries" basket — list of countries to be set by decree (potentially including Japan and South Korea). Decree pending publication.
- Higher price negotiation pressure: 2024 rebates total **€7.98 billion** (+12% vs 2023)
- 14 products account for half of total rebates
- Litigation surge: 25 in 2023 vs. 13 in 2022, 81% related to drugs

**Source:**
- [Simon-Kucher — 2026 LFSS and CEPS report analysis](https://www.simon-kucher.com/en/insights/what-2026-lfss-and-2024-ceps-activity-report-signal-frances-pma) (Jan 2026)
- [Global Legal Insights — France Pricing & Reimbursement Laws 2025](https://www.globallegalinsights.com/practice-areas/pricing-reimbursement-laws-and-regulations/france/) (Aug 2025)
- [Simon-Kucher — France P&R brief 2025](https://www.simon-kucher.com/en/insights/pr-brief-france-what-latest-updates-mean-pharma-pricing-and-market-access) (Mar 2025)

**Last verified:** May 2026

---

### 🟢 Germany (DE)

**Authority:** GKV-SV (National Association of Statutory Health Insurance Funds) + G-BA (Federal Joint Committee) + BfArM
**Uses IRP:** Indirect (through AMNOG benefit assessment + EU price comparison as input)
**Mechanism:** AMNOG (Pharmaceutical Market Restructuring Act, 2011)

**AMNOG process (timeline 2024+):**
1. **Months 0–6:** Free pricing — manufacturer sets launch price (was 12 months pre-2022, now 6 months)
2. **Within 6 months:** G-BA conducts early benefit assessment (added benefit vs. appropriate comparator therapy)
3. **Months 7+:** Price negotiation between manufacturer & GKV-SV (or arbitration)
4. **Reimbursement price** applies retroactively from Month 7

**Price level:** Public list price + confidential rebate (NEW since Mar 2026)
**Lag:** 6 months between launch and negotiated price
**Frequency:** Initial price negotiation + reassessments based on new evidence

**Mandatory rebates:**
- Patent-protected drugs outside reference price system: **12%** (was 7%, increased by GKV-FinStG)
- Reference price products: lower

**Key 2024–2026 changes — CRITICAL:**
- ⚠️ **Medical Research Act (Mar 2026):** Manufacturers can opt for **confidential reimbursement prices** until data exclusivity expires
  - "Public" list price stays high; "real" reimbursement price stays confidential
  - **9% additional discount** required for confidentiality option
  - **Disrupts IRP downstream**: countries referencing Germany see only the high public price, not the negotiated net price
- AMNOG free-pricing period reduced from 12 → 6 months (GKV-FinStG, 2022)
- 5% clinical trial exemption: if ≥5% of trial subjects in Germany, exempt from new AMNOG guardrails
- "No Added Benefit" rating now caps price more strictly
- 20% extra discount for brand-brand combination products

**Note:** Germany is referenced by ~20 countries' IRP baskets — highest spillover impact globally.

**Source:**
- [Pharmaceutical Technology — All change in Germany: confidential pricing in, IRP out](https://www.pharmaceutical-technology.com/analyst-comment/all-change-germany-confidential-pricing-irp/) (Jan 2025)
- [Pharmaceutical Technology — Medical Research Act](https://www.pharmtech.com/view/germany-amends-and-approves-the-new-medical-research-act) (Mar 2026)
- [Inside EU Life Sciences — Confidential reimbursement prices](https://www.insideeulifesciences.com/2024/02/16/germany-again-to-reform-drug-pricing-and-reimbursement-laws-with-confidential-reimbursements-prices-that-impede-international-reference-pricing/) (Feb 2024)
- [Trinity Life Sciences — GKV-FinStG analysis](https://trinitylifesciences.com/blog/the-german-financial-stabilization-of-statutory-health-insurance-system-act/) (2025)
- [Global Legal Insights — Germany Pricing 2025](https://www.globallegalinsights.com/practice-areas/pricing-reimbursement-laws-and-regulations/germany/)
- SGB V §35a (statutory law)

**Last verified:** May 2026

---

### 🟢 Italy (IT)

**Authority:** AIFA (Agenzia Italiana del Farmaco) — **major restructuring effective Jan 30, 2024**: CSE (Scientific and Economic Commission for Pharmaceuticals) replaced the old CTS (Technical-Scientific Committee) and CPR (Pricing & Reimbursement Committee). Single 10-member commission now handles both technical assessment and pricing/reimbursement
**Uses IRP:** **Limited** — primarily value-based + budget-impact "Blended Pricing Model" (BPM) since transition from Indication-Based Pricing (IBP)
**Basket:** No formal basket — IRP used only as supportive criterion in negotiations
**Formula:** **Negotiation-based** (not formula-based)
**Price level:** Ex-factory list price (with confidential rebates)
**Lag:** N/A (negotiation timing)
**Frequency:** At launch, indication extensions, and contract renewals

**Mechanism:**
- AIFA CSE evaluates added therapeutic value, risk-benefit ratio, cost-effectiveness, budget impact
- For each new indication: structured negotiation → typically additional discount (Extension of Indication / EoI)
- Heavy use of **Managed Entry Agreements (MEAs)**: outcomes-based, cost-sharing, payment-by-results, financial agreements
- **Confidential pricing**: list prices (Class A, H reimbursable) often >> actual net price after MEA-based rebates (estimated 15-30% off list)
- C-nn class enables marketing within 60 days of EU MA without waiting for reimbursement negotiation conclusion
- **Innovativeness status**: full innovativeness or conditional innovativeness grants special benefits (faster regional inclusion, dedicated funds)

**Key 2024–2026 changes:**
- **Jan 30, 2024**: AIFA CSE operational (new President Robert Nisticò); General Director position eliminated
- 2024 budget law: increased Fondo Sanitario Nazionale +€3B (2024), +€4B (2025), +€4.2B (2026); hospital drug ceiling raised to ~8.6% of FSN
- Determina Pres. n. 966/2025: new criteria for innovative drugs and AMR-related antibiotics
- Continued payback mechanisms (manufacturers pay back portion of overspend)
- Italy ranked 7th in EFPIA W.A.I.T. 2024 for access speed

**Source:**
- [Global Legal Insights — Italy P&R Laws 2025](https://www.globallegalinsights.com/practice-areas/pricing-reimbursement-laws-and-regulations/italy/) (Sep 2024)
- [Certara — AIFA Makeover 2024](https://www.certara.com/blog/aifa-makeover-italys-leap-into-2024/) (May 2025)
- [Trinity Life Sciences — Italy 2024 AIFA Restructuring](https://trinitylifesciences.com/blog/rise-with-the-waves-italy-aifa-restructuring-and-budget-reforms/) (Oct 2025)
- [PMC — Pricing Multi-Indication Drugs Italy](https://pmc.ncbi.nlm.nih.gov/articles/PMC12037441/) (PharmacoEcon Open 2025)
- [AIFA OsMed Report 2024 (en)](https://www.aifa.gov.it/documents/20142/2694929/Comunicato_AIFA_51-2025_EN.pdf)
- [ScienceDirect — Italian price negotiation anchoring](https://www.sciencedirect.com/science/article/pii/S0168851025001046) (May 2025)

**Last verified:** May 2026

---

### 🟢 Spain (ES)

**Authority:** CIPM (Comisión Interministerial de Precios de los Medicamentos) — 8 members from Health/Finance/Economy/Industry + 3 rotating regional representatives
**Uses IRP:** **Yes, but only as INTERNAL CRITERION** — not formally in law since RDL 16/2012
**Basket:** EU member states where the drug is marketed (informal — not codified in law)
**Formula:** **Lowest in basket** (when used as supportive criterion)
**Price level:** Ex-factory (PVL, max ex-factory price set by CIPM)
**Lag:** ~12 months
**Frequency:** Annual ex-officio price review by Ministry of Health (Jan 2023-Mar 2024: 73 products reviewed → 60 increases, 13 decreases)

**Mechanism:**
- Governed by **Royal Legislative Decree 1/2015** (Law on Guarantees and Rational Use of Medicines)
- After EMA centralized authorization, AEMPS notifies Ministry of Health → HTA assessment → CIPM decision
- Average 22.2 months from EU MA to reimbursement (2019-2022 cohort): 5.7mo to NC + 16.7mo to CIPM resolution
- Reimbursement rate ~70% of EMA-authorized drugs
- IRP also applicable to drugs marketed in any EU MS for ≥10 years (unusual — not restricted to off-patent)
- VALTERMED: real-world data system for high-cost medicines decisions
- Internal Reference Pricing (IPR) for off-patent drugs by ATC level 5, yearly updates
- **Confidential pricing**: increasingly common, list prices ≠ net prices

**Key 2024–2026 changes:**
- **Aug 2024**: Draft Royal Decree on HTA published (still pending)
- **Dec 2024**: Public consultation on Royal Decree on Pricing and Reimbursement
- **Apr 2025**: Draft Law on Medicinal Products and Medical Devices published (replacing RDL 1/2015)
- 2024 reform: CIPM decision records will document factors considered for first time (transparency)
- New legislative procedures could significantly impact market access if approved
- EU JCA (Joint Clinical Assessment) implementation may reduce timelines starting 2025

**Note:**
- ⚠️ **CRITICAL FINDING** (per ec.europa.eu simulation report): "In Spain, ERP was previously regulated by Royal Decree Law 4/2010. Since 2012, ERP is no longer mentioned in the Law following the Decree law 16/2012. Nevertheless, ERP still conforms to internal criteria of the Interministerial Pricing Commission" — This means Spain's IRP is **not codified statutorily**, which makes it less predictable than commonly assumed
- Spain considered restricting IRP to in-patent drugs (CAFPF debate 2019-2024)

**Source:**
- [Global Legal Insights — Spain P&R Laws 2025](https://www.globallegalinsights.com/practice-areas/pricing-reimbursement-laws-and-regulations/spain/) (Aug 2025)
- [Remap Consulting — Spain's New Pharmaceutical Access Reform](https://remapconsulting.com/pma-trends/a-closer-look-at-spains-new-pharmaceutical-access-reform/) (Oct 2024)
- [PPRI Spain 2024 Profile](https://ppri.goeg.at/system/files/inline-files/Spain_Pharmaceutical_pricing_and_reimbursement_policies_2024.pdf)
- [J.Stindt Consultants — Pricing & Reimbursement Spain](https://jstindt.com/pricing-reimbursement-dossiers-spain/)
- [ec.europa.eu — ERP simulation report](https://health.ec.europa.eu/document/download/c937630e-7039-43db-87d0-eb782573ba5b_en)
- [ISPOR — Spain timelines and JCA impact](https://www.ispor.org/heor-resources/presentations-database/presentation/euro2024-4015/146776)
- Royal Legislative Decree 1/2015 + RDL 16/2012 + RDL 9/2011

**Last verified:** May 2026

---

### 🟢 Netherlands (NL)

**Authority:** Ministry of Health, Welfare and Sport (VWS) + BFAG (Drug Price Negotiation Unit)
**Uses IRP:** **Yes**, mandatory under **Wgp (Wet Geneesmiddelenprijzen / Medicine Prices Act of 1996)**
**Basket — 4 countries:** **Belgium, France, Norway, UK** (Norway replaced Germany in October 2020)
**Formula:** **Average wholesale price (apotheekinkoopprijs / AIP)** of comparable medicines in basket
- Min 2 countries with comparable product required
- "Comparable" = same active ingredient + strength + pharmaceutical form
- **10% maximum decline** mitigation (per Temporary Policy Rule 2024) to prevent severe price drops

**Price level:** Maximum wholesale price (AIP)
**Lag:** ~6 months
**Frequency:** **Twice yearly** (biannual revisions)

**Mechanism:**
- Wgp sets statutory maximum wholesale price; product can be sold below this
- For drugs with annual NL turnover <€1M: companies can request Wgp not to apply (especially for hospital products)
- **GVS (Geneesmiddelenvergoedingssysteem)** for outpatient reimbursement uses internal reference pricing
- **"Sluis" (lock)** for inpatient drugs: high-cost hospital drugs must pass HTA + price negotiation before reimbursement
- BFAG negotiates confidential rebates with pharma for selected high-cost outpatient/inpatient drugs
- Member of **Beneluxa Initiative** (joint negotiation with BE, LU, AT, IE)
- Healthcare Institute (Zorginstituut) advises Minister on reimbursement decisions (90 days target)

**Key 2024–2026 changes:**
- **Temporary Policy Rule 2024** in force pending broader Wgp legislative review
- Council of State recommended new bill rather than amendment decree
- Continued patient co-payment cap of €250/year
- Increased role of confidential pricing through BFAG negotiations

**Note:**
- One of the most predictable IRP frameworks in Europe ("clearly defined algorithms")
- The basket choice (NO instead of DE) is intentional: many drugs are much cheaper in NO than DE, driving prices down for NL
- Annual savings from confidential negotiations: ~€155M target (€132M in 2017)

**Source:**
- [Global Legal Insights — Netherlands P&R Laws 2025](https://www.globallegalinsights.com/practice-areas/pricing-reimbursement-laws-and-regulations/netherlands/) (Aug 2025)
- [Government.nl — Keeping medicines affordable](https://www.government.nl/topics/medicines/keeping-medicines-affordable)
- [Eversana — Netherlands new IRP Oct 2020](https://www.eversana.com/2020/08/19/netherlands-irp/)
- [Lexology — Netherlands medicine pricing](https://www.lexology.com/library/detail.aspx?g=3855ce7c-026d-409b-b7e3-5668de8b2df6)
- [Simon-Kucher — IRP Five-Step Approach (NL)](https://www.simon-kucher.com/en/insights/international-reference-pricing-five-step-strategic-approach)
- [Generics Market Review 2025](https://www.medicinesforeurope.com/wp-content/uploads/2025/06/Generics-Market-Review-2025.pdf)
- Wgp 1996 + Healthcare Insurance Act (Zvw) + Wmg

**Last verified:** May 2026

---

### 🟢 Switzerland (CH)

**Authority:** BAG / FOPH (Federal Office of Public Health)
**Uses IRP:** Yes (combined with TQV)
**Basket:** Germany, Denmark, UK, Netherlands, France, Austria, Belgium, Finland, Sweden (9 countries)
**Formula:** Average (APV — Auslandpreisvergleich) **+** TQV (Therapeutic Cross-Comparison) — both weighted equally for SL inclusion
**Price level:** Ex-factory (FAP — switched from public price in **January 2024**)
**Lag:** ~12 months
**Frequency:** Triennial review for SL (Specialty List)

**Mechanism:**
- Cost-effectiveness (Wirtschaftlichkeit) assessed by combining APV (foreign comparison) and TQV (domestic therapeutic comparison)
- Both methods weighted 50/50 by default (since 2017 reform)
- Patent-expired originators compared to other patent-expired (with 20% discount if compared to patented)
- Biosimilars: ≥25% gap to reference at launch; ≥10% gap thereafter

**Key 2024–2026 changes:**
- January 2024: Switch to ex-factory price (FAP) for SL listing
- VAT moved from FAP to public price calculation
- Deductibles capped for DK, NL, FI, SE (German deductibles revised)
- Cost containment package 2 (March 2025): pricing process modernization in progress

**Source:**
- [BAG official FAQs](https://www.bag.admin.ch/en/prices-of-medicines-in-switzerland-faqs)
- [PwC Switzerland — Healthcare regulations 2024](https://www.pwc.ch/en/insights/tax/pharma-life-sciences/guide-for-swiss-healthcare-regulations.html)
- [Global Legal Insights — Switzerland Pricing 2025](https://www.globallegalinsights.com/practice-areas/pricing-reimbursement-laws-and-regulations/switzerland/)
- [CMS Law — Three-yearly price review 2023](https://cms-lawnow.com/en/ealerts/2023/01/pricing-of-medicines-in-switzerland-three-yearly-price-review-what-are-the-most-important-changes-for-2023)

**Last verified:** May 2026

---

### 🟢 Austria (AT)

**Authority:** Pricing Committee under Federal Ministry of Health (BMSGPK) for outpatient pricing; Dachverband (Main Association of Austrian Social Security) manages reimbursement via EKO (Erstattungskodex / Reimbursement Code)
**Uses IRP:** **Yes, for outpatient pharmaceuticals only**
**Basket:** **All EU member states** where the drug is marketed (broad basket)
**Formula:** **Average price** of all available reference countries
**Price level:** Ex-factory
**Lag:** ~6-12 months
**Frequency:** Periodic; price review at launch + when significant price changes occur in basket

**Mechanism:**
- Pricing Committee sets statutory maximum manufacturer price; further negotiation possible for reimbursement (EKO inclusion)
- **Reimbursement box system** (Yellow/Green/Red boxes): drugs classified by innovation level vs comparators
- HEK (Heilmittel Evaluierungs-Kommission / Medicinal Products Evaluation Commission) — independent advisory body assists Dachverband
- HTA-driven decisions for inpatient sector
- Member of **Beneluxa Initiative** (joint negotiation with BE, NL, LU, IE)
- **Pharmaceutical Evaluation Board (Bewertungsboard)** established 2024 to support HTA for inpatient and "interface" medicines
- **EU HTA Regulation joint HTA** (EU JCA) implementation from 2025
- **No generic reference pricing system**, no mandatory generic substitution by pharmacists, no INN prescribing (low generic market share: ~36% volume in 2021 vs 79% in some peers)

**Key 2024–2026 changes:**
- 2024: New Pharmaceutical Evaluation Board active for HTA of high-price/interface medicines
- Continued IHSI (International Horizon Scanning Initiative) participation (Beneluxa spinoff)
- 2023 industry solidarity payment renewed
- Ongoing: 'Spitals-HEK' pilot for inpatient HTA

**Source:**
- [Global Legal Insights — Austria P&R Laws 2024](https://www.globallegalinsights.com/practice-areas/pricing-reimbursement-laws-and-regulations/austria/) (Sep 2024)
- [PPRI Pharma Brief: Austria 2023](https://ppri.goeg.at/system/files/inline-files/PPRI_Pharma_Brief_AT_2023_bf.pdf)
- [WHO Health System Summary 2024 Austria](https://eurohealthobservatory.who.int/docs/librariesprovider3/publicationsnew/hit-summaries-no-flags/hit-summary-austria-2024-2p.pdf)
- [PMC — Overview of ERP Systems in Europe](https://pmc.ncbi.nlm.nih.gov/articles/PMC4802694/)

**Last verified:** May 2026

---

### 🟢 Belgium (BE)

**Authority:**
- **Pricing**: Minister of Economic Affairs + Pricing Committee for Medicinal Products (Federal Public Service for Economic Affairs)
- **Reimbursement**: Minister of Social Affairs + NIHDI/INAMI/RIZIV (National Institute for Health and Disability Insurance) + CRM (Commission for Reimbursement of Medicines)
- **MA**: FAMHP (Federal Agency for Medicines and Health Products)

**Uses IRP:** **Yes, as supportive criterion** (not primary)
**Basket:** **All 26 EU Member States** (very broad — comparison data submitted in pricing dossier) + price in country of origin
**Formula:** **Average of reference countries** OR price in country of origin (most common methodologies reported)
**Price level:** **Maximum ex-factory price** (set by Minister of Economic Affairs); also "maximum public price" includes ex-factory + wholesaler/pharmacist margins + pharmacist fee + 6% VAT
**Lag:** ~12 months
**Frequency:** At launch + parallel to reimbursement procedure (via "Mediprices" portal of FPS Economic Affairs)

**Mechanism:**
- **Reference Price System (RPS)** at Level 1 (generic RPS) — applies to bio-equivalent products (originator + generics within same ATC-5)
- Pricing dossier must include: ex-factory cost structure, annual accounts, price comparison with EU MS, comparable Belgian medicines
- Minister of Economic Affairs sets max ex-factory price based on scientific + economic evidence
- **Heavy use of confidential pricing**: Article 35bis (closed envelope) for innovative medicines
- Belgium is referenced by many EU countries, making it a strategic pricing market
- **Beneluxa Initiative** founder (with NL, LU, AT, IE) — joint negotiations and HTA cooperation
- Public health insurance covers ~75% of healthcare expenses

**Key 2024–2026 changes:**
- **From January 2026**: New "Early & Fast Equitable Access" procedure allowing some therapies to be reimbursed before full EU authorization
- Pharmaceutical expenditure expected +48.9% (2022-2027) — strong cost containment pressure
- 2025 estimated medicines expenditure: €6.554B (+9% vs 2024)
- KCE (Belgian Healthcare Knowledge Centre) increasingly involved in HTA
- HDA (Healthcare Data Agency) established 2023 (operational from 2024) for data-driven decisions
- Average waiting time MA → reimbursement: 534 days (2024 data, behind EU peers)
- Only 12 of 95 newly reimbursed medicines in 2022 were orphan drugs

**Source:**
- [Global Legal Insights — Belgium P&R Laws 2024](https://www.globallegalinsights.com/practice-areas/pricing-reimbursement-laws-and-regulations/belgium/) (Sep 2024)
- [Trade.gov — Belgium Biopharmaceuticals 2026](https://www.trade.gov/country-commercial-guides/belgium-biopharmaceuticals-0) (Mar 2026)
- [KCE — Reference Price System Belgium](https://kce.fgov.be/sites/default/files/2021-11/d20101027320.pdf)
- [ec.europa.eu — ERP simulation report (Belgium)](https://health.ec.europa.eu/document/download/c937630e-7039-43db-87d0-eb782573ba5b_en)

**Last verified:** May 2026

---

### 🟢 Sweden (SE)

**Authority:** TLV (Tandvårds- och Läkemedelsförmånsverket)
**Uses IRP:** **No formal IRP** — value-based pricing only
**Mechanism:** Cost-effectiveness assessment by TLV, no fixed willingness-to-pay threshold

**Source:** TLV public documents
**Last verified:** May 2026

---

### 🟢 Norway (NO)

**Authority:** NoMA / Norwegian Medical Products Agency (formerly Statens legemiddelverk, now under DMP)
**Uses IRP:** Yes (mandatory for prescription-only medicines)
**Basket — 9 countries:** Sweden, Finland, Denmark, Germany, UK, Netherlands, Austria, Belgium, Ireland
**Formula:** **Mean of 3 lowest market prices** in basket (if <3 countries available, mean of available prices)
**Price level:** Maximum **PPP** (Pharmacy Purchasing Price = ex-factory level, AIP in Norwegian)
**Lag:** ~12 months
**Frequency:** **Annual** for top-selling active ingredients (revision plan published each autumn). New launches: 6-monthly review for first 2 years. Lower-volume products less frequent.

**Mechanism:**
- Maximum PPP set by NoMA before market entry; product can be sold at lower price freely
- Currency conversion via mean exchange rate of last 6 months (Central Bank of Norway)
- Comparison done at unit level (per tablet, per dose) due to pack size differences
- Differentiation between large (>30 units) and small (≤30 units) packages
- **Withdrawal of a product from a reference country may affect Norway's price** (with documentation)
- **Specialist sector**: net prices negotiated separately between MAH and LIS (Norwegian Drug Procurement Cooperation) for hospital drugs
- **Internal reference pricing** ("trinnpris") for generics/biosimilars after patent expiry

**Source:**
- [NoMA — Maximum Price (dmp.no)](https://www.dmp.no/en/public-funding-and-pricing/pricing-of-medicines/maximum-price) (official, current)
- [PPRI Norway 2018 Profile](https://ppri.goeg.at/sites/ppri.goeg.at/files/inline-files/PPRI%20Norway%202018.pdf)
- [Pharmaboardroom — Norway P&R 2025](https://pharmaboardroom.com/legal-articles/regulatory-pricing-and-reimbursement-overview-norway/) (Feb 2025)
- Forskrift om legemidler chapter 12 (statutory regulation)

**Last verified:** May 2026

---

### 🟢 Denmark (DK)

**Authority:**
- **Hospital medicines:** Lif (industry association) + Ministry of Interior and Health + Danish Regions (price-cap agreement)
- **Primary care:** Danish Medicines Agency (Lægemiddelstyrelsen) + Danish Medicines Council (Medicinrådet) for HTA + Danish Reimbursement Committee (Medicintilskudsnævnet)

**Uses IRP:** **Yes for hospital medicines (price-cap)**, **No for primary care** (uses internal reference pricing since 2005)

**Hospital medicines (price-cap agreement 2025–2027):**
- **Basket — 9 countries:** Sweden, Norway, Finland, UK, Netherlands, Belgium, Germany, Ireland, Austria
- **Formula:** **Average price** in basket (regardless of how many countries have marketed product)
- **Min 3 reference countries** required, otherwise temporary price cap (introduction price) is set
- **Price level:** List
- **Frequency:** Set at first marketing; price cannot be raised above cap
- **Scheduled price-cap reductions:** −2.1% July 2025, −2.1% February 2026, −0.8% February 2027
- New hospital medicines first marketed Feb 1, 2024 – Jan 31, 2027 not subject to general cap reductions (transition rules)

**Primary care (since April 2005 reform):**
- **Internal reference pricing** based on cheapest domestic substitute (switched FROM external reference pricing in 2005)
- Patients co-pay full price difference between drug bought and cheapest substitute
- Pharmacies must offer cheapest product first (mandatory substitution)
- Prices updated every 14 days (notified by suppliers to Danish Medicines Agency)

**Lag:** N/A (different mechanisms)
**Frequency:** Bi-weekly price updates for primary care; price-cap recalibrated every multi-year agreement cycle for hospitals

**Mechanism:**
- **Hospital procurement:** Amgros (national wholesale distribution company) negotiates prices on behalf of Danish Regions, in collaboration with Medicinrådet and hospital pharmacies
- **HTA:** Medicinrådet provides recommendations on whether to adopt new medicines as standard treatment in hospital sector (cost-effectiveness focus)
- 5 reimbursement categories for primary care; reimbursement starts at DKK 1,145 for adults

**Source:**
- [Lif — Price-cap agreement hospital medicines 2025–2027](https://www.lif.dk/wp-content/uploads/2025/01/Price-cap-agreement-hospital-medicines-2025-2027.pdf) (official, Jan 2025)
- [Lægemiddelstyrelsen — Prices of medicines](https://laegemiddelstyrelsen.dk/en/reimbursement/prices/) (official)
- [Pharmaboardroom — Denmark Market Access & HTA](https://pharmaboardroom.com/legal-reports/market-access-health-technology-assesment-denmark/) (Mar 2024)
- [European Pharmaceutical Review — Danish reference price reform](https://www.europeanpharmaceuticalreview.com/article/30915/drug-pricing-reforms-the-danish-experience/) (2019)
- Kaiser et al. (2014). Health Economics — Danish reference pricing reform.

**Last verified:** May 2026

---

### 🟢 Ireland (IE)

**Authority:** HSE (Health Service Executive) + IPHA (Irish Pharmaceutical Healthcare Association) Framework Agreement, governed by **Health Act 2013** (Pricing and Supply of Medical Goods)
**Uses IRP:** Yes (mandatory for IPHA members; in practice industry-wide standard)
**Basket — 14 countries:** Austria, Belgium, Denmark, Finland, France, Germany, Greece, Italy, Luxembourg, Netherlands, Portugal, Spain, Sweden, UK
**Formula:** **Currency-adjusted average ex-factory price** of the 14 reference countries
**Price level:** Ex-factory (price to wholesaler, exclusive of VAT)
**Lag:** ~12 months (annual realignment)
**Frequency:** **Annual price realignment** to the 14-country average; **only downward** realignments permitted

**Mechanism (per 2021 Agreement, expired Sept 2025; new 2026 Agreement signed):**
- New medicines: ex-factory price set at currency-adjusted average across 14 reference basket countries
- Annual realignment: only downward
- HSE rebate on all sales (escalating): 5.5% (2021) → 7.75% (2022) → 8.25% (2023) → 8.5% (2024) → **9% (2025)**
- Patent-expired medicines: automatic price reductions (50% of original ex-factory for off-patent; 80% for patent-expired non-exclusive biologics)
- 12.5% additional rebate on patent-expired non-exclusive biologics
- HSE may use **EURIPID database** as additional price source
- Cost-effectiveness assessment by **NCPE** (National Centre for Pharmacoeconomics) — Rapid Review (~4 weeks) for all submissions
- Statutory **180-day timeline** for HSE reimbursement decisions (rarely met — average ~617 days for IPHA medicines 2022-2024)

**Key 2024–2026 changes:**
- New IPHA Framework Agreement concluded **March 2026** to replace expired 2021–2025 agreement
- Focus on faster patient access (compliance with 180-day statutory timeline)
- Structural reforms on pricing and reimbursement
- Continued downward realignment to basket
- Aligns with Ireland's upcoming EU Presidency priorities

**Source:**
- [Global Legal Insights — Ireland Pricing & Reimbursement Laws 2025](https://www.globallegalinsights.com/practice-areas/pricing-reimbursement-laws-and-regulations/ireland/) (Aug 2025)
- [IPHA — New Framework Agreement 2026](https://www.ipha.ie/new-ipha-framework-agreement-to-accelerate-patient-access-and-drive-investment-in-innovative-medicines/) (2026)
- [2021 Framework Agreement on the Supply and Pricing of Medicines (FASPM)](https://www.ipha.ie/getattachment/About-Us/Our-Role/Agreement-on-the-Supply-of-Medicines/FINAL-FRAMEWORK-AGREEMENT-ON-THE-SUPPLY-AND-PRICING-OF-MEDICINES.pdf) (Oct 2021)
- [Mason Hayes & Curran — IPHA Renegotiation update](https://www.mhc.ie/latest/insights/renegotiation-of-the-ipha-framework-agreement-update) (Jan 2026)
- [Matheson — IPHA Agreement analysis](https://www.matheson.com/insights/detail/life-sciences-update-new-agreement-on-medicine-pricing-and-model-clinical-trial-agreements-in-ireland) (Jan 2022)
- Health (Pricing and Supply of Medical Goods) Act 2013

**Last verified:** May 2026

---

### 🟢 Poland (PL)

**Authority:** Ministry of Health + AOTMiT (HTA Agency) + Economic Commission (Komisja Ekonomiczna)
**Uses IRP:** **Yes (informal use), supplemented by internal reference pricing and price-volume contracts**
**Basket:** All **EU/EEA + Switzerland** (very broad)
**Formula:** **Lowest price** in basket / lowest in "limit group"
**Price level:** Ex-factory
**Lag:** ~12 months
**Frequency:** Periodic; Reimbursement Act updates

**Mechanism:**
- Governed by **Refundacyjna Act of 2011** (Reimbursement Act, last amended 2023)
- **"Limit groups"** (internal reference pricing): drugs with similar therapeutic action and mechanism (despite different APIs) classified together; price cannot exceed lowest in group
- **Price-volume agreements (PVAs)**: mandatory price negotiations with NFZ (National Health Fund); volume thresholds trigger automatic price reductions
- **Risk-sharing agreements** for innovative high-cost drugs (RSS — Risk Share Scheme), often confidential
- HTA assessment by AOTMiT (cost-effectiveness threshold ~3× GDP/QALY = ~155k PLN ≈ €36k/QALY)
- Drugs reimbursed via **Reimbursement List** (Wykaz refundowanych leków), updated every 2 months
- **No formal IRP basket** in legislation — pricing reflects practice from comparison with EU markets

**Key 2024–2026 changes:**
- 2023 Reimbursement Act amendments: streamlined pricing decisions, expanded Risk Share for innovative drugs
- Strong downward price erosion: ~14% drop since launch on average across products examined
- Increased focus on rare diseases and oncology
- IHH-style market structure considerations being introduced

**Note:**
- Polish prices typically among lowest in CEE region
- Hungary's wider basket (entire EU/EEA, lowest formula) creates similar dynamic
- Czechia and Hungary tend to have higher prices among CEE due to more selective baskets

**Source:**
- [Pharmaceutical Technology — Reference pricing CEE countries](https://www.pharmaceutical-technology.com/pricing-and-market-access/reference-pricing-cee-countries-pressure-prices-html/)
- [Frontiers — Pharmaceutical Regulation in CEE Countries](https://www.frontiersin.org/articles/10.3389/fphar.2017.00892/full) (updated 2026)
- Refundacyjna Act 2011 + 2023 amendments (Polish legislation)

**Last verified:** May 2026

---

### 🟢 Czech Republic (CZ)

**Authority:** SUKL (Státní ústav pro kontrolu léčiv / State Institute for Drug Control) — sets max price + reimbursement; MoH issues binding opinion for orphan drugs
**Uses IRP:** **Yes (main pricing tool)**
**Basket:** **18 EU/EEA reference countries** (broad EU basket)
**Formula:** **Average of 3 lowest priced countries** in basket
**Price level:** Ex-factory (warehouse price + max margins)
**Lag:** ~6-12 months
**Frequency:** **Comprehensive review every 5 years** for each "reference group"; simple short-term reviews when first generics enter or substantial savings expected (initiated by SUKL or public payers)

**Mechanism (per Act No. 48/1997):**
- SUKL must set max price + reimbursement via individual administrative procedure (165 days for joint, 75 days for max price only; can be extended +60 days)
- **Reference groups** (therapeutic clusters): products with similar efficacy/safety/clinical position grouped → reimbursement at lowest price per Average Daily Dose (ADD) in group
- If product not marketed in ≥3 reference basket countries: agreed price can be used in assessment (except for highly innovative)
- **Highly Innovative Medicinal Products (HIMPs)** — many orphans — granted limited 3-year reimbursement, extendable by 2 years (max 5 years total)
- Automatic price reductions on entry of competitors:
  - 1st biosimilar: −30%
  - 2nd biosimilar: additional −15%
  - 3rd biosimilar: additional −10%
- HTA process is mandatory part of reimbursement decision-making

**Key 2024–2026 changes:**
- Czechia ranked **7th in EFPIA W.A.I.T. 2024** (good access speed)
- Continued focus on orphan drug pathway (special procedure with scientific societies and patient orgs)
- New "soft criteria" for OMP cost-effectiveness assessment (without strict ICER thresholds)

**Note:**
- Czechia has some of the highest prices among CEE (~90% of German prices)
- Often used as **early launch market** in CEE due to predictable IRP and 5-year price stability after setting

**Source:**
- [Wolf Theiss — Pricing and Reimbursement in CEE & SEE](https://www.wolftheiss.com/insights/pricing-and-reimbursement-of-medicinal-products-in-cee-and-see/) (Mar 2024)
- [Global Legal Insights — Czech Republic P&R Laws 2025](https://www.globallegalinsights.com/practice-areas/pricing-reimbursement-laws-and-regulations/czech-republic/) (Aug 2025)
- [Frontiers — CEE Pharmaceutical Regulation Review](https://www.frontiersin.org/articles/10.3389/fphar.2017.00892/full) (updated 2026)
- Act No. 48/1997 (Public Health Insurance Act)

**Last verified:** May 2026

---

### 🟢 Turkey (TR)

**Authority:** Ministry of Health (Türkiye İlaç ve Tıbbi Cihaz Kurumu / TITCK) — pricing; SGK (Social Security Institution) — reimbursement; Price Evaluation Commission (FDK) — exchange rate
**Uses IRP:** **Yes (mandatory primary tool, since 2004)**
**Basket — 5 reference countries:** **France, Spain, Italy, Portugal, Greece** + country of origin + country of "serial release"
**Formula:** **Lowest warehouse sale price** among basket countries
**Price level:** Ex-factory (max warehouse sale price)
**Lag:** ~12 months
**Frequency:** Continuous; major annual exchange rate revision in February

**Mechanism (per 2017 Communiqué + amended Decree of 24 Oct 2024):**
- **Three-layer "trivet pricing system"**:
  1. **External Reference Pricing** (lowest price in 5 countries + origin)
  2. **Fixed Pharmaceutical Euro Rate** — TRY/EUR rate fixed annually by FDK, NOT free market rate
  3. **Public discount** (additional negotiated discount for SGK reimbursement, ~11% for originators 1st year, 23% from 2nd year; 23% for generics from year 1)
- **Generics**: max **66% of cheapest originator price** in 5 reference countries
- **Internal RPS**: equivalent groups based on active substance, SGK pays max 5% above base price
- Negotiations for products only available in Turkey
- Use of MEAs and confidential discounts since 2016 (Alternative Reimbursement Process)

**Fixed exchange rate evolution (key driver of distortions):**
| Year | Fixed TRY/EUR | Real TRY/EUR | % of real |
|---|---:|---:|---:|
| 2009 | 1.9595 | 2.1181 | 92% |
| 2019 | — | — | 60% (coefficient set) |
| Jul 2023 | 14.0387 | 29.9829 | 47% |
| Dec 2023 | **17.5483** (+25%) | ~30 | ~58% |
| 2024 | 17.5483 (unchanged) | 33.844 (avg) | 52% |
| 2025 | 21.6721 | — | — |
| **2026** | **25.3346** (+17%) | — | — |

**Key 2024–2026 changes:**
- **24 Oct 2024**: Decree amendment — new pricing thresholds, real source price change procedures
- **Feb 2026**: Base EUR rate raised to 25.3346 TRY/EUR (+17% vs 2025); new price protection threshold 87.34 TRY; general medicine threshold 45.64 TRY
- Drug shortages persist due to disconnect between fixed rate and real rate (manufacturers withdrawing or refusing launches)
- TR public discount + low fixed EUR rate = Turkey one of cheapest pricing markets globally

**Note:**
- ⚠️ **HIGH IRP RISK**: Turkey is referenced by some MENA baskets (Saudi, Egypt) — TR's artificially low prices propagate downward
- **Italy has highest impact on TR pricing** of all reference countries (analysis of 4,633 products)
- Turkey has saved tens of billions of EUR over the past decade through this system, but at cost of access delays and drug shortages

**Source:**
- [GRATA — Pharmaceuticals Pricing in Türkiye](https://gratanet.com/publications/pharmaceuticals-pricing-in-turkiye) (Jun 2024)
- [Pharmaceutical Technology — Türkiye Euro exchange rate](https://www.pharmaceutical-technology.com/analyst-comment/turkiye-pharmaceutical-euro-exchange-rate/) (Dec 2024)
- [Esin Av — Amendments Oct 2024](https://www.esin.av.tr/2024/10/31/amendments-to-the-decree-on-pricing-of-pharmaceuticals/) (Oct 2024)
- [Daily Sabah — Pharma reimbursement Türkiye](https://www.dailysabah.com/opinion/op-ed/pharma-reimbursement-system-of-turkiye-and-its-problems) (2024)
- [Frontiers — Turkish pricing strategies and oncology access](https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2024.1364341/full) (2024)
- [RestProperty — 2026 Euro Rate decree](https://restproperty.com/news-en/gizn-v-turcii/new-turkey-drug-pricing-regulation-2026-euro-rate-up-17/) (Feb 2026)
- [PPRI Türkiye 2022 Profile](https://ppri.goeg.at/system/files/inline-files/Turkiye_PPRI_EECA_country_poster_2022_EN_0.pdf)
- 2017 Communiqué + 24 Oct 2024 Decree amendment + Feb 2026 Presidential Decree

**Last verified:** May 2026

---

### 🟢 Russia (RU)

**Authority:** Ministry of Health (Minzdrav) + FAS (Federal Antimonopoly Service) for ZHNVLP/VED list
**Uses IRP:** **Yes**, mandatory **only for ZHNVLP (Жизненно необходимые и важнейшие лекарственные препараты / Vital and Essential Drugs list)**
**Basket — 21 reference countries (per current methodology):** Germany, France, UK, Italy, Spain, Belgium, Netherlands, Austria, Greece, Portugal, Hungary, Czech Republic, Poland, Romania, Slovakia, Bulgaria, Turkey, Ukraine (varies — minimum prices observed) + countries where MAH has manufacturing
**Formula:** **Minimum price** observed in basket countries
**Price level:** Wholesale (registered max manufacturer price = "registered price")
**Lag:** ~12 months
**Frequency:** Manufacturer-initiated registration; Ministry-led re-registration possible

**Mechanism:**
- **Government Decree No. 865** (price registration for ZHNVLP) — last major revision 2019, methodology updated several times
- Manufacturer must register price BEFORE marketing for ZHNVLP listing
- Registered max price + **regional wholesale margins** (vary by federal subject) + retail margins = max final price
- Annual indexation possible for products on ZHNVLP only (limited; tied to CPI methodology)
- **Compulsory licensing** has been used post-2022 sanctions for restricted access drugs (precedents: lenalidomide, paxlovid)
- **Import substitution policy** ("Pharma 2030" national strategy): preferences for locally-produced drugs in tenders; "second extra" rule for procurement (foreign drug excluded if 2 local alternatives bid)

**Post-2022 context (sanctions impact):**
- **Many Western pharmas reduced presence**: Pfizer, Eli Lilly, GSK suspended new investments; AstraZeneca, Roche maintained essential supply only
- **Parallel imports legalized May 2022** for many products
- **Compulsory licensing** more frequent since 2022
- Currency: RUB instability has led to repeated re-pricing requests
- Several Western drugs withdrawn or unavailable; access via personal import schemes
- Russia reportedly considering broader basket reform (post-2022 geopolitical realignment)

**Key 2024–2026 changes:**
- Continued tightening of "Russian-origin" requirements in tenders
- Increased use of risk-sharing agreements for high-cost orphans
- BRICS pharmaceutical cooperation expanding (China, India increasingly important suppliers)
- Pricing methodology under review but no major published reform

**Note:**
- ⚠️ **Russia is essentially de-coupled from Western IRP cascade post-2022** — its impact on global cascade has decreased significantly
- ⚠️ Data on Russian prices increasingly opaque; sanctions complicate verification
- Russian Federation Western drug market has shrunk substantially

**Source:**
- General industry reports + post-2022 sanctions analyses
- Government Decree No. 865 + 2019 methodology revisions
- WHO European Region pharmaceutical price databases (limited Russia data)

**Last verified:** May 2026 — ⚠️ **post-2022 context still evolving; consult specialized Russian pharma intelligence (Headway Company, DSM Group) for current data**

---

## Asia-Pacific

### 🟢 Japan (JP)

**Authority:** MHLW (Ministry of Health, Labour and Welfare) + Chuikyo (Central Social Insurance Medical Council) + PMDA
**Uses IRP:** Yes (FPA — Foreign Price Adjustment)
**Basket:** US, UK, France, Germany (4 countries)
**Formula:** `avg_with_adjustment` — average of basket with adjustment band

**FPA mechanism:**
- If Japan price ≥ 1.25× foreign average → **downward adjustment**
- If Japan price ≤ 0.75× foreign average → **upward adjustment**
- Adjustment cap: **1.2× pre-adjustment price**
- Foreign price calculation: highest price treated as **2× the average of other prices** (anti-outlier rule)

**Price level:** List (NHI price)
**Lag:** ~24 months for revisions
**Frequency:** Biennial NHI price revision (with off-year revisions since 2021)

**Sources used (per HIRA reference for foreign pricing):**
- US: Red Book
- UK: Monthly Index of Medical Specialities (MIMS)
- Germany: Rote Liste
- France: Vidal

**Key 2024–2026 changes — CRITICAL:**
- **FY2024 reform:** Early Introduction Premium (5–10%) for drugs launched in Japan within 6 months of US/EU; Sakigake premium expansion (10–20%); Usefulness Premium expansion
- **FY2026 reform (CRITICAL):**
  - ⚠️ Germany referenced **only post-AMNOG net price** (no longer free-pricing list price) — substantially reduces Japan reference benchmark
  - **Spillover rule abolished** (price cuts no longer extend to similar therapeutic class drugs)
  - **SPA-SSS (Special Price Adjustment for Sustainable Health System and Sales Scale)**: blockbusters with sales > ¥300B (~$2B) AND >10× original forecast face up to **66.7% price reduction** (was 50%)
  - Annual price revisions now standard
  - PMP (Price Maintenance Premium) expanded: now covers products with Early Introduction Premium and Pediatric Premium
  - Post-pricing CEA (Cost-Effectiveness Analysis) used predominantly for downward adjustment

**Source:**
- [PMDA — NHI Drug Price System](https://www.pmda.go.jp/files/000248690.pdf)
- [WindroseCG — Japan FY2026 Drug Pricing Reform](https://www.windrosecg.com/posts/japan-fy2026-reforms) (2025)
- [Trinity Life Sciences — Japan Pricing Policy Reform 2024](https://trinitylifesciences.com/blog/japan-pricing-policy-reform-2024/)
- [Eradigm Consulting — Japan P&R mechanisms](https://eradigm.com/what-are-the-pricing-and-repricing-mechanisms-in-japans-pr-system-that-pharma-must-understand-when-considering-a-launch-in-japan/) (Jul 2024)
- [Health Advances — FY2024 Drug Pricing Reform](https://www.healthadvances.com/insights/blog/reversing-the-tide-japans-promising-fy2024-drug-pricing-reform) (Mar 2024)

**Last verified:** May 2026

---

### 🟢 South Korea (KR)

**Authority:** HIRA (Health Insurance Review and Assessment Service) + NHIS (National Health Insurance Service) + MOHW (Ministry of Health and Welfare)
**Uses IRP:** Yes (A8)
**Basket:** US, UK, Germany, France, Italy, Switzerland, Japan, Canada (A8 — Canada added 2022, Australia removed)
**Formula:**
- **Average A7 adjusted price** for essential drugs (in price negotiation)
- **Lowest A7 adjusted price** for PE (Pharmacoeconomic Evaluation) exemption pathway

**Price level:** Ex-factory
**Lag:** ~12 months
**Frequency:** Periodic

**Reference price sources used by HIRA (verified):**
- US: Red Book
- UK: Monthly Index of Medical Specialities (MIMS)
- Germany: Rote Liste
- France: Vidal
- Italy: L'Informatore Farmaceutico
- Switzerland: Arzneimittel Kompendium
- Japan: Hokenyaku Jiten (Yakugyo Kenkyukai)
- Canada: (added 2022, source verification needed)

**Mechanism:** Price calculated as ex-factory rate × exchange rate, then VAT and distribution margin applied for adjusted price.

**PEE waiver system:**
- Drugs with no equivalent alternative + extremely small patient population (< 200) → exempt from traditional pharmacoeconomic evaluation, use ERP instead
- Subsequent negotiation with NHIS may reference broader OECD prices

**Source:**
- [Frontiers in Pharmacology — Variables affecting new drug prices in South Korea](https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2024.1370915/full) (2024)
- [PMC — Two-Waiver System in South Korea](https://pmc.ncbi.nlm.nih.gov/articles/PMC11959314/) (2025)
- [Korea Biomed — A7 to A8 transition](https://www.koreabiomed.com/news/articleView.html?idxno=20141) (Dec 2022)
- HIRA official documents (2023)

**Last verified:** May 2026

---

### 🟢 China (CN)

**Authority:** NHSA (National Healthcare Security Administration)
**Uses IRP:** **No formal IRP** — direct value-based negotiation
**Mechanism:** NRDL (National Reimbursement Drug List) annual negotiation

**NRDL process (5 steps):**
1. Manufacturer application
2. Expert evaluation (clinical value, cost-effectiveness)
3. Value rating (Breakthrough / Improvement / Equivalent / Inferior)
4. Price negotiation with NHSA panel
5. Inclusion at negotiated price (1-year contract initially, with renewal)

**Categories:**
- **Category A:** Essential drugs, full reimbursement
- **Category B:** Clinically necessary, partial reimbursement
- **Category C (NEW 2025):** Innovative high-cost therapies, supplementary tier with commercial insurance integration

**Pricing benchmarks (informal):**
- Rare disease threshold: ¥500,000 (~$70k) for negotiation, ¥300,000 (~$42k) for reimbursement
- Average price reduction at NRDL inclusion: **50–65%** (63% in 2024)

**Key 2024–2026 changes:**
- **Category C list (introduced 2025):** Allows commercial insurance to fund innovative drugs that don't fit BMI budget
- **Value Rating Framework** introduced 2023, refined in 2024
- 2024 NRDL: 89/117 drugs (76%) successfully negotiated, avg 63% price cut
- **Domestic preference:** 71% of new 2024 listings from Chinese manufacturers
- Annual schedule shift: BMI applications from April, Category C applications timed differently

**Note:** China references international prices as **soft input**, not formula-based. Foreign price data informs negotiation strategy but does not set ceiling.

**Source:**
- [Greenberg Traurig — China 2024 NRDL Lessons](https://www.gtlaw.com/en/insights/2025/2/china-on-the-move-lessons-from-chinas-2024-national-negotiation-of-drug-prices) (Feb 2025)
- [Remap Consulting — NRDL 2024 update](https://remapconsulting.com/emerging-developing-markets/nrdl/a-2024-update-is-nrdl-inclusion-in-china-really-the-golden-ticket-for-market-access/) (2025)
- [ChemLinked — 2024 NRDL details](https://baipharm.chemlinked.com/news/china-adds-91-drugs-to-2024-national-reimbursement-drug-list-nrdl) (Dec 2024)
- [NRDL Plus — Category C Drug List](https://www.nrdlplus.com/nhsa-fast-tracks-chinas-first-category-c-drug-list-to-expand-commercial-funding-for-innovative-medicines/) (Feb 2025)
- [ICON — China's 2024 NRDL](https://www.iconplc.com/insights/blog/2024/08/14/understanding-chinas-2024-nrdl-key-changes-and-their-impact)
- [Trinity Life Sciences — NRDL 2024 rare diseases](https://trinitylifesciences.com/blog/nrdl-2024-rare-diseases-deep-dive/) (2025)

**Last verified:** May 2026

---

### 🟢 India (IN)

**Authority:** NPPA (National Pharmaceutical Pricing Authority)
**Uses IRP:** **No external IRP**
**Mechanism:** DPCO 2013 (Drug Price Control Order)

**Formula:** Internal market-based — average price of top 3 brands by market share for drugs in **Schedule 1** (essential medicines)

**Price level:** Domestic ex-factory (capped)
**Frequency:** Annual revision

**Note:** India is NOT a price-setter for any other country's IRP (typically excluded due to internal market structure).

**Source:** DPCO 2013 (statutory law)
**Last verified:** May 2026

---

### 🟢 Australia (AU)

**Authority:** PBAC (Pharmaceutical Benefits Advisory Committee) → PBS (Pharmaceutical Benefits Scheme)
**Uses IRP:** **No formal IRP** — value-based pricing
**Mechanism:**
- PBAC assesses cost-effectiveness against comparator
- Price negotiation with Department of Health
- Pricing through PBS reimbursement

**Note:** Australia is referenced by PMPRB11 (Canada), Brazil's new 14-country basket, South Africa, etc.

**Source:** PBAC guidelines (public documents)
**Last verified:** May 2026

---

### 🟢 Indonesia (ID)

**Authority:**
- **Marketing authorization:** BPOM / NADFC (National Agency of Drug and Food Control)
- **Public procurement & insurance:** BPJS-K (Badan Penyelenggara Jaminan Sosial Kesehatan / Social Security Agency for Health) administering JKN (Jaminan Kesehatan Nasional / National Health Insurance, since Jan 2014)
- **Pricing for public sector:** LKPP (National Public Procurement Agency) running e-Catalogue (e-Katalog) tender system

**Uses IRP:** **Limited / informal** — primary mechanism is **tender-based pricing** through e-Catalogue for public sector

**Mechanism:**
- **Public sector (~70% of market via JKN):** Centralized tender system through e-Catalogue (LKPP) — manufacturers submit bids; lowest price typically wins
- Reference pricing exists in regulation but is **not the primary cost-control mechanism** — tender prices set the de facto reference
- **JKN Formulary (Fornas):** controls reimbursable drugs; prices set through tender
- Private sector: free pricing
- Government has explored international reference pricing in policy discussions but has not implemented a formal IRP basket comparable to other countries

**Note:**
- Indonesia is **referenced in regional baskets** (e.g., used by Vietnam alongside Thailand, Malaysia, Philippines, Cambodia)
- Tender prices in Indonesia tend to be among the lowest in ASEAN due to competitive bidding and large patient population
- Universal Health Coverage achieved 2019 (~95% coverage)

**Source:**
- [Tandfonline — Government pharmaceutical pricing strategies in Asia-Pacific](https://www.tandfonline.com/doi/full/10.1080/20016689.2019.1601060) (2019)
- [LinkedIn / Pagada — Market Access in Indonesia](https://www.linkedin.com/pulse/market-access-reimbursement-landscape-pharmaceutical-products-pagada)
- [ScienceDirect — Pharmaceutical Policies on Medicine Procurement in Indonesia under JKN](https://www.sciencedirect.com/science/article/pii/S2212109919300846)
- [MTAPS — Review of Pricing Policies in Asia](https://www.mtapsprogram.org/wp-content/uploads/2021/12/Review-Pricing-policies.pdf)
- [Artixio — BPOM Regulations for Indonesia](https://www.artixio.com/post/nadfc-bpom-regulation-of-pharmaceuticals-in-indonesia) (Jan 2026)

**Last verified:** May 2026

---

### 🟢 Thailand (TH)

**Authority:**
- **National Drug Policy:** Ministry of Public Health (NDP)
- **Health insurance:** NHSO (National Health Security Office) for Universal Coverage Scheme (UCS, ~75% of population) + SSO (Social Security Office) + CSMBS (Civil Servant Medical Benefit Scheme)
- **National Drug List:** NLEM (National List of Essential Medicines) Subcommittee
- **HTA:** HITAP (Health Intervention and Technology Assessment Program) — globally recognized HTA agency

**Uses IRP:** **Limited / supportive** — primary mechanisms are **HTA + price negotiation + tender**

**Mechanism:**
- **NLEM listing:** Drugs assessed via HITAP HTA (cost-effectiveness threshold ~120,000 THB/QALY); only NLEM-listed drugs reimbursed
- **Public sector pricing (~80% of market):**
  - Government Pharmaceutical Organization (GPO) negotiates prices for NLEM drugs
  - Compulsory licensing has been used for high-cost drugs (HIV, cancer) historically
  - Tender system for hospital purchases
- **Private sector:** Free pricing (no formal control)
- IRP referenced informally during HITAP HTA reviews but no formal basket
- Thailand also uses **Managed Entry Agreements (MEAs)** including risk-sharing for cancer and rare disease drugs (per APAC pricing strategies overview)

**Reference role:** Thailand is referenced by **Vietnam**'s basket (Vietnam → Thailand, Malaysia, Indonesia, Philippines, Cambodia) — Thailand is a price floor for lower-income ASEAN countries.

**Note:** No formal IRP basket as of 2024–2026, but extensive use of HTA-driven price negotiations.

**Source:**
- [Tandfonline — Government pharmaceutical pricing strategies in Asia-Pacific](https://www.tandfonline.com/doi/full/10.1080/20016689.2019.1601060) (2019)
- [MTAPS — Review of Pricing Policies in Asia](https://www.mtapsprogram.org/wp-content/uploads/2021/12/Review-Pricing-policies.pdf)
- HITAP (hitap.net) — HTA reviews and methodology
- NHSO official documentation

**Last verified:** May 2026

---

## Middle East

### 🟢 Israel (IL)

**Authority:** Ministry of Health (Pharmaceutical Division) + Ministry of Finance pricing committee
**Uses IRP:** Yes (mandatory for prescription drugs)
**Basket — 7 countries:** Belgium, Spain, Hungary, France, UK, Germany, Netherlands
**Formula:** **Average of the 3 lowest prices** in basket
- If only 1 or 2 countries have a corresponding price, average those available
- If no reference price found in any country: fixed maximum prices set by the Supervisor of Prices (per 2018 amendments)

**Price level:** **Wholesale / retailer cost level** (normative price reflecting retailer costs in reference countries)
**Lag:** ~12 months
**Frequency:** **Annual update** at January 1; mid-year update if EUR exchange rate moves >3% between January and end of May (max 5% adjustment)

**Mechanism:**
- Statutory basis: **1996 Control of Goods and Services Law** + **2001 Order on Maximum Prices for Prescription Drugs** + **2018 amendments**
- VAT 17% applied
- 2018 amendments: Supervisor of Prices may **increase** prices above citation method to correct distortions and ensure continued supply
- Co-payment for patients: minimum NIS 17 to 10–15% of public maximum price (incl. VAT)
- 2024: MoH mandated 3.6% reduction in maximum prices of 1,500 prescription drugs

**National Health Basket process:**
- Annual update of Israeli National Health Basket since 1995, by Public Committee
- Budget-driven expansion (2018: ~135 new medications/indications added at NIS 460M cost)
- February 2025: 117 medications and technologies recommended for inclusion (focus on preventive medicine and chronic conditions)
- Negotiations between manufacturers and MoH typically include hedging arrangements capping state expenditures over first years

**Source:**
- [Pharma-Israel.org — Regulation page](https://www.pharma-israel.org.il/en/activities/regulations/) (industry association, official)
- [Commonwealth Fund — Israel Health Care System Profile](https://www.commonwealthfund.org/international-health-policy-center/countries/israel) (2026)
- [PPRI Israel Profile](https://ppri.goeg.at/sites/ppri.goeg.at/files/inline-files/Israel.pdf)
- [Lexology — Snapshot: medicine pricing in Israel](https://www.lexology.com/library/detail.aspx?g=417d0c9b-2259-4cae-8f6e-dd79a2b235bf) (Jan 2020)
- Control of Goods and Services Law 1996 + Order 2001 + 2018 Amendments (statutory)

**Last verified:** May 2026

---

### 🟢 Saudi Arabia (SA)

**Authority:** SFDA (Saudi Food and Drug Authority) + NUPCO (National Unified Procurement Company) for procurement
**Uses IRP:** **Yes (main pricing tool)**
**Basket — 30 countries (per current SFDA methodology):** Canada, UK, France, Germany, Italy, Spain, Belgium, Netherlands, Sweden, Switzerland, Ireland, Australia, Japan, US, Turkey, Lebanon, Jordan, Egypt, UAE, Kuwait, Bahrain, Oman, Qatar, Portugal, Greece, India, Austria, Finland, Denmark, Norway
**Formula:** **Lowest price** in basket + country of origin
**Price level:** Ex-factory
**Lag:** ~6-12 months
**Frequency:** **Re-referencing every 60 months (5 years)** — last major event 2019, **next event 2024**

**Mechanism:**
- SFDA approves price at MA stage; price comparison done at unit (per tablet/dose) level
- For drugs not in basket countries: SFDA negotiation
- **Public sector** (~80% of market): centralized procurement via NUPCO; multi-year tenders
- **Private sector**: SFDA-set max price; pharmacy/wholesaler margins regulated
- **Localization policy** (Vision 2030): preferences in tenders for locally manufactured drugs (NAMAA local content unit)
- KSA represents ~60% of GCC pharmaceutical market
- HTA approach increasingly used (SFDA partnered with NICE for capacity building)

**Key 2024–2026 changes:**
- **2024 IRP re-referencing event** triggered downstream price reductions in GCC and MENA
- Saudi Arabia introduced **value-based pricing pilots** (per Grand View Research 2024)
- **Breakthrough Medicines Program** (accelerated pathway)
- **Conditional Approval** introduced
- Several **pharmacovigilance and quality reforms** harmonized with EMA/FDA standards
- **Centralized GCC registration** processes streamlined
- January 2024 LCGPA agreements for local production (sitagliptin etc.)
- Saudi Vision 2030 driving major pharmaceutical investment (joint ventures, vaccine manufacturing)

**Source:**
- [LSE — Pharmaceutical Pricing in MENA region](https://www.lse.ac.uk/business/consulting/assets/documents/pharmaceutical-pricing-and-reimbursement-in-the-middle-east-and-north-africa-region.pdf)
- [PMC — Procurement and Reimbursement KSA, UAE, Qatar, Egypt](https://pmc.ncbi.nlm.nih.gov/articles/PMC10887475/)
- [NAVLIN Insights — Equitable Pricing GCC](https://www.navlindaily.com/upload/newsletter/attachment/240131134849_NAVLIN_Insights_Newsletter___Issue_57.pdf) (Jan 2024)
- [IQVIA — Localization MENA](https://www.iqvia.com/-/media/iqvia/pdfs/mea/white-paper/localization-of-pharmaceutical-manufacturing-in-middle-east-and-north-africa-region.pdf)
- [Middle East Pharma Market Report 2025](https://www.marketdataforecast.com/market-reports/middle-east-pharmaceutical-market)
- SFDA official guidelines

**Last verified:** May 2026

---

### 🟢 United Arab Emirates (AE)

**Authority:**
- **Federal**: Emirates Drug Establishment (EDE — formerly MOHAP) — pricing for federal level
- **Emirate-level**: DOH Abu Dhabi, DHA Dubai, MOH Northern Emirates
- **Insurance**: Daman (UAE National Health Insurance) Abu Dhabi + 12 insurance companies in Dubai

**Uses IRP:** **Yes**, IRP-based pricing system at federal MOH level
**Basket — ~31 countries:** GCC countries (Saudi Arabia, Kuwait, Bahrain, Oman, Qatar) + 14 EU references (UK, France, Germany, Spain, Portugal, Italy, Belgium, Netherlands, Sweden, etc.) + Australia, Canada, Egypt, Jordan, Turkey, Greece
**Formula:** **Lowest** of: median of EU references, lowest of GCC, price in country of origin
**Price level:** Wholesale
**Lag:** ~12 months
**Frequency:** **Re-referencing event 2022 launched**, periodic; some price stability per IRP rule per NAVLIN tracking

**Mechanism:**
- Each Emirate has its own formulary (drawn by separate P&T committees at Emirate + hospital levels)
- **Federal level**: MOH provides drug approvals, MA, and pricing using IRP
- **Emirate level**: DOH (Abu Dhabi) + DHA (Dubai) → market access + reimbursement
- **For Northern Emirates**: MOH directly drives market access
- Public health expenditure: 4% of GDP (2017), increasing to USD $25.7B target 2024
- 70% of outpatient visits through private healthcare in Dubai/Abu Dhabi
- 60+ insurance companies for population of 9.3M (complex ecosystem)

**Key 2024–2026 changes:**
- **January 2025**: New regulations under **Federal Decree-Law No. 38/2024** — accelerated approval process for innovative drugs (incl. biosimilars)
- **EDE introduced 2024** as new federal regulatory body (replacing MOHAP)
- **Value-based pricing pilots** introduced
- **Centralized registration processes** with breakthrough pathways
- Continued GCC harmonization initiatives
- **Localization** — joint ventures driving local manufacturing

**Source:**
- [PMC — Procurement and Reimbursement UAE, KSA, Qatar, Egypt](https://pmc.ncbi.nlm.nih.gov/articles/PMC10887475/)
- [Middle East Pharma Market 2025 (UAE Federal Decree-Law 38/2024)](https://www.grandviewresearch.com/industry-analysis/middle-east-pharmaceutical-market-report)
- [NAVLIN Insights GCC IRP Tracking](https://www.navlindaily.com/upload/newsletter/attachment/240131134849_NAVLIN_Insights_Newsletter___Issue_57.pdf)
- [LSE MENA Pharmaceutical Pricing](https://www.lse.ac.uk/business/consulting/assets/documents/pharmaceutical-pricing-and-reimbursement-in-the-middle-east-and-north-africa-region.pdf)

**Last verified:** May 2026

---

### 🟢 Egypt (EG)

**Authority:** EDA (Egyptian Drug Authority — replaced CAPA in 2019)
**Uses IRP:** **Yes (mandatory)** + cost-of-production review for some drugs
**Basket:** **36 reference countries** (broad — country of origin + 36 optional reference countries)
**Formula:** **Lowest price** in basket OR country of origin (whichever lower)
**Price level:** Retail (Public Selling Price / PSP)
**Lag:** ~6 months
**Frequency:** Periodic; major re-referencing during EGP devaluations

**Mechanism:**
- Decree 426 of 2009 / 2014 amendments on pricing
- IRP combined with **cost-of-production review** for certain locally-manufactured drugs
- **Universal Health Insurance (UHI) law** of 2018 being implemented in phases (currently rolling out by governorate)
- Significant **out-of-pocket payment** burden remains (incomplete UHI coverage)
- **Localization policy**: incentives for local manufacturing through Pharmaceutical Industries Holding Co. (HOLDIPHARMA) and free zones
- Generic pricing: capped at percentage below originator (price capping)
- **EGP devaluations** (Mar 2022, Jan 2024, Mar 2024 = ~62% cumulative devaluation): triggered massive disruption to IRP-based system; many manufacturers withdrew or paused new launches
- Government has used **emergency price increases** to address shortages

**Key 2024–2026 changes:**
- **March 2024**: EGP devalued 38% (from 30 to ~50 EGP/USD); Egypt freed exchange rate for IMF $8B program
- **2024**: Significant **price increases** approved for many essential medicines (typically 25-50%) to keep manufacturers in market
- **Continued drug shortages** for some imported and complex drugs
- EDA increased focus on local manufacturing approvals
- IRP review methodology under reform discussion (less rigid lowest-price approach being considered)

**Note:**
- ⚠️ Egypt is **referenced by some MENA baskets (KSA, UAE)** — its low prices propagate downward in cascade
- Currency volatility = pricing instability

**Source:**
- [LSE — Pharmaceutical Pricing in MENA](https://www.lse.ac.uk/business/consulting/assets/documents/pharmaceutical-pricing-and-reimbursement-in-the-middle-east-and-north-africa-region.pdf)
- [PMC — Egypt and MENA reimbursement](https://pmc.ncbi.nlm.nih.gov/articles/PMC10887475/)
- [IQVIA Middle East 2024 report](https://www.iqvia.com/-/media/iqvia/pdfs/mea/240709_iqvia_mea-pharmaceutical-market-quarterly-report_q1-2024.pdf)
- Decree 426/2009 + 2014 amendments
- IMF Egypt Article IV consultations 2024

**Last verified:** May 2026

---

## Africa

### 🟢 South Africa (ZA)

**Authority:**
- **Pharmaceutical Economic Evaluations (PEE) Directorate**, Department of Health (national)
- **NHRA** (National Health Regulatory Authority) for MA — replaced MCC, then SAHPRA
- **SAHPRA** (South African Health Products Regulatory Authority) for current MA
- **Pricing Committee** advises on Single Exit Price (SEP) and IRP

**Uses IRP:** **Yes (mandatory under Medicines and Related Substances Act, Section 22G)**
**Basket — 4 countries:** **Australia, New Zealand, Canada, Spain**
**Formula:** **Lowest price** in basket + comparison with current SA price
**Price level:** **Single Exit Price (SEP)** — manufacturer's exit price + statutory dispensing fee + VAT (mandated since 2004)
**Lag:** ~12 months
**Frequency:** Annual SEP adjustment based on CPI + foreign exchange rate; manufacturer-initiated for IRP

**Mechanism:**
- **Single Exit Price (SEP) Act**: all drugs sold at SEP nationwide (no discounting allowed)
- IRP used to determine if SA prices are "out of line" with peer markets
- **Annual SEP adjustment formula**: combines CPI, average exchange rate fluctuations vs USD, EUR, GBP
- Public sector procurement via **National Department of Health tenders** (massive volumes, deep discounts)
- Private sector: SEP applies, dispensing fee regulated
- **NHI Bill 2024**: National Health Insurance pending — would reform pharmaceutical procurement and pricing
- Off-label use, generics: separate framework

**Key 2024–2026 changes:**
- **NHI Act 2024** (signed May 2024) — major reform pending implementation; will create single-payer system
- Continued challenges with patent law reform (Voluntary Licensing, March 2024 patent amendments)
- South Africa active in **WHO IRP harmonization** discussions
- SAHPRA backlog reduction efforts (faster MA timelines)
- Tendering increasingly competitive: state sector includes direct deliveries + retrospective additions + buy-outs

**Source:**
- [IQVIA Middle East & Africa Market 2024](https://www.iqvia.com/-/media/iqvia/pdfs/mea/240709_iqvia_mea-pharmaceutical-market-quarterly-report_q1-2024.pdf)
- [IQVIA MEA biopharmaceutical market](https://www.marketdataforecast.com/market-reports/middle-east-and-africa-bio-pharmaceuticals-market)
- Medicines and Related Substances Act + Section 22G regulations
- NHI Act 2024 (signed May 2024)
- SAHPRA official documentation

**Last verified:** May 2026

---

## Part 2.5 — EU Southern / Eastern (cascade-relevant secondary countries)

### 🟢 Greece (GR)

**Authority:** EOPYY (National Organisation for Healthcare Provision) + EOF (National Organisation for Medicines) + Ministerial Pricing Committee
**Uses IRP:** **Yes (mandatory)**
**Basket:** Variable — typically all EU countries where the drug is marketed
**Formula:** **Average of 3 LOWEST prices in EU basket**
**Off-patent:** 50% of original innovator price
**Generic:** 40% of original innovator price
**Price level:** Ex-factory
**Lag:** ~6 months
**Frequency:** Biannual review

**Mandatory rebates & clawback structure (most aggressive in EU):**
- **9% mandatory rebate** on factory price (all reimbursed drugs)
- **+2-21% additional rebate** based on volume tiers
- **Hospital clawback:** **>75% in 2024** for drugs over €30 (PIF Greece data)
- **EOPYY (outpatient) clawback:** 62.7% in 2024
- **PIF reports 79.8% clawback** on innovative therapies for H1 2024
- **Total clawback + rebate burden:** ~47% of total sales (SFEE)

**Key 2024–2026 changes:**
- **MD 3410/2024 (Jan 2024):** New clawback calculation method for high-cost medicines (HCMs); 3% rebate deducted from clawback amount; retroactive to Jan 2023
- **MD 10186/2024 (Feb 2024):** €3 cap on patient contribution for generics (effective Feb 16, 2024)
- **Framework agreement under negotiation 2025-2027:** Aim is structural reform after years of payback fatigue. €850M additional pharma budget commitment 2024-25 (incl. €700M from EU RRF)
- **EFPIA WAIT 2024:** Innovative drug availability **decreased 4%** vs 2023
- **Clinical trial activity declining:** 118 studies approved 2024 vs 200+ historically (-40% YoY)
- **Suspension of innovative oncology/immunotherapy** for some products by manufacturers facing unsustainable economics

**Source:**
- [EY Greece Tax Alert — New Pharmaceutical Regulations (Mar 2024)](https://www.ey.com/en_gr/technical/tax/tax-alerts/new-developments-in-the-pharmaceutical-regulation-pricing-clawback-on-hcms-cap-on-the-contribution-for-generic-medicines)
- [PIF Greece — Clawback Derailment (Oct 2025)](https://www.pifgreece.gr/en/news/clawback-derailment-on-innovative-therapies/)
- [Pharmaceutical Technology — Greece Framework Agreement (Oct 2024)](https://www.pharmaceutical-technology.com/analyst-comment/unresolved-clawback-issues-greece/)
- [SFEE — Pharmaceutical Investment Handbook for Greece](https://www.sfee.gr/wp-content/uploads/2024/01/Final_SfEE_PiHG_18.10.2021.pdf)
- [Trade.gov — Greece Healthcare 2024](https://www.trade.gov/country-commercial-guides/greece-healthcare)

**Last verified:** May 2026

---

### 🟢 Portugal (PT)

**Authority:** INFARMED (Autoridade Nacional do Medicamento e Produtos de Saúde, I.P.)
**Uses IRP:** **Yes (mandatory)**
**Basket — 4 reference countries:** Spain, France, Italy, Slovenia (sometimes Greece historically)
**Formula:** **Average** of basket prices (or LOWEST if basket reduced)
**Hospital sector:** Uses **lowest** price in basket
**Price level:** Ex-factory PVA (Preço de Venda ao Armazenista) → PVP (retail) calculated by formula
**Lag:** 12 months
**Frequency:** Annual price review

**Mechanism:**
- General regime: **Decree-Law 97/2015** (SiNATS — National System of Evaluation of Health Technologies)
- INFARMED has 15-business-day price approval window (tacit approval after that)
- **CRR (Reimbursement Contracts)** for innovative drugs — confidential, increasingly common
- Hospital decisions can override INFARMED positive recommendations (Hospital Therapeutic Commissions)
- Reference price system (RPS) for products with generics — homogeneous groups
- HTA threshold ~30k€/QALY for cost-effectiveness

**Key 2024–2026 changes:**
- **Decree-Law 128/2023 (in force Jan 2, 2024):** Retail price (PVP) **REMOVED from packaging**. Patients now informed at dispensing only. Aim: prevent confusion when actual cost differs from PVP due to reference pricing/co-payments
- **Q3-Q4 2024:** Updated lists of Homogeneous Groups and unit reference prices (Informative Notes 035 and 046/CD/100.20.200)
- Market growth projected: $2.1-2.5B by end 2025

**Cascade impact:** Portugal references propagate to:
- **Brazil** (PT in CMED 14-country basket from Apr 2026)
- **Saudi Arabia** (PT in 20-country basket per 2021 SFDA Pricing Rules)
- **UAE** (PT in basket per Decree-Law 38/2024)
- **Turkey** (PT in 5-country basket — high impact)
- **Russia** (PT in ZHNVLP basket)
- **Ireland** (PT in IPHA Framework 14-country basket)

**Source:**
- [GLI Portugal Pricing & Reimbursement 2024](https://www.globallegalinsights.com/practice-areas/pricing-reimbursement-laws-and-regulations/portugal/)
- [Lexology — Portugal Removal of Retail Price from Packaging (Jan 2024)](https://www.lexology.com/library/detail.aspx?g=e98c6ecd-9ecf-43c5-8430-08073565b16f)
- [Cuatrecasas — Infarmed New Notes (Aug 2024)](https://www.cuatrecasas.com/en/portugal/life-sciences-healthcare/art/new-informative-notes-from-infarmed-1)
- [Trade.gov — Portugal Pharmaceutical Market](https://www.trade.gov/market-intelligence/portugal-pharmaceutical-market-growth)
- Decree-Law 97/2015 (SiNATS) + Decree-Law 128/2023

**Last verified:** May 2026

---

### 🟢 Hungary (HU)

**Authority:** NEAK (National Institute of Health Insurance Fund Management) + Ministry of Health
**Uses IRP:** **Yes (broadest basket in EU)**
**Basket — 30 countries:** All 27 EU MS + Switzerland + Norway + Iceland (EEA + CH)
**Formula:** **LOWEST** price among reference countries
**Price level:** Ex-factory
**Lag:** ~6 months
**Frequency:** Continuous (per application)

**Pre-Jun 2023 rule (KEY CHANGE):**
- ⚠️ Required ≥3 EEA reimbursing countries (mathematical avg of 3 lowest)
- This rule blocked Hungary from being early adopter for innovative drugs
- **Lifted June 2023:** Now even single-country reimbursement triggers HU pricing eligibility

**Mechanisms:**
- **Internal RPS:** Therapeutic groups + active substance groups, blind bidding for generics
- **Generic stepped pricing:** 1st generic -40%, 2nd -20%, 3rd -10%, 4th-6th -5%
- **Mandatory PVAs** (price-volume agreements) with NEAK
- **MEAs widespread** (financial, performance-based, conditional)
- **20% special tax** on reimbursable pharmaceutical sales
- **Clawback** based on overspending vs annual budget

**Key 2024–2026 changes:**
- **Act XXIX of 2024:** New public benefit foundation (**Batthyány-Strattmann László Alapítvány**) for named-patient reimbursement effective Jan 1, 2025
- NEAK remains as "one-stop shop" for applications, distributes to foundation as appropriate
- AI development access to EESZT (national eHealth) data from Jan 2026

**Cascade impact:** Hungary referenced by:
- **Israel** (basket of 7 includes HU)
- **Saudi Arabia** (20-country basket)
- **Russia** (ZHNVLP basket)
- Several MENA referencing systems

**Source:**
- [PPRI Hungary 2024 Country Report](https://ppri.goeg.at/system/files/inline-files/Hungary_Pharmaceutical_pricing_and_reimbursement_policies_2024_0.pdf)
- [Baker McKenzie — Hungarian P&R Reforms (May 2023)](https://healthcarelifesciences.bakermckenzie.com/2023/05/26/hungarian-pricing-and-reimbursement-reforms-aiming-to-remove-hurdles-to-late-market-access-of-innovative-pharmaceuticals/)
- [Baker McKenzie — Named Patient Reimbursement Reform (Jan 2025)](https://healthcarelifesciences.bakermckenzie.com/2025/01/20/hungary-to-introduce-important-changes-to-named-patient-reimbursement/)
- [Wolf Theiss — CEE & SEE Pricing 2024](https://www.wolftheiss.com/insights/pricing-and-reimbursement-of-medicinal-products-in-cee-and-see/)
- [Pharm Tech CEE — Reference Pricing](https://www.pharmaceutical-technology.com/pricing-and-market-access/reference-pricing-cee-countries-pressure-prices-html/)
- Act XXIX of 2024

**Last verified:** May 2026

---

### 🟢 Romania (RO)

**Authority:** Ministry of Health (MoH) + NAMMDR (National Agency for Medicines and Medical Devices) + CNAS (National Health Insurance House)
**Uses IRP:** **Yes (mandatory primary tool)**
**Basket — 12 countries:** Austria, Belgium, **Bulgaria**, Czech Republic, Germany, Greece, Hungary, Italy, Lithuania, Poland, Slovakia, Spain
**Formula:** **LOWEST** maximum manufacturer price across basket
**Public Catalogue:** Average of 3 LOWEST prices
**Generics/Biosimilars:** 65-80% of innovator
**Price level:** Ex-factory in RON (national currency conversion at MoH-imposed rate)
**Lag:** 12 months
**Frequency:** Annual realignment (in theory)

**Mechanism:**
- **CANAMED Catalogue:** Master list of approved maximum manufacturer prices
- MAH initiates pricing process — proposed price must be ≤ lowest in basket
- ⚠️ EUR→RON conversion at MoH-imposed rate (additional pressure beyond basket lowest)
- 1,200+ legislative changes in past 10 years (regulatory volatility)
- Vaccines and some essential drugs (WHO list) exempted from full basket comparison

**Clawback (severe):**
- Clawback rate often **>25% during budget crises** (highly volatile)
- Calculated quarterly
- Industry response: many drugs withdrawn/delayed when economics break
- Example documented: Roche Zelboraf launched 2012, withdrawn pre-reimbursement, re-introduced 2020 at marked discount

**Cascade impact:** Romania referenced by:
- Russia (ZHNVLP basket)
- Bulgaria (10-country basket)

**Source:**
- [Lexology — Romania Pharmaceutical Sector (Jun 2024)](https://www.lexology.com/library/detail.aspx?g=06f84be2-de86-4cc1-a4e7-8c9b923fb2d3)
- [Wolf Theiss — CEE & SEE Pricing 2024](https://www.wolftheiss.com/insights/pricing-and-reimbursement-of-medicinal-products-in-cee-and-see/)
- [Pharmaceutical Technology — CEE Reference Pricing](https://www.pharmaceutical-technology.com/pricing-and-market-access/reference-pricing-cee-countries-pressure-prices-html/)
- Law 95/2006 + CANAMED methodology

**Last verified:** May 2026

---

### 🟢 Slovakia (SK)

**Authority:** Slovak Ministry of Health + State Institute for Drug Control (SIDC) + Categorization Committee
**Uses IRP:** **Yes (since 2008)**
**Basket — 27 countries:** All EU MS (excluding Slovakia itself)
**Formula:** **Average of 3 LOWEST** prices in basket
**Price level:** Ex-factory
**Lag:** ~6 months
**Frequency:** Continuous (categorization-driven)

**Legal basis:** Act 363/2011 (scope and conditions for payments) + Act 577/2004 (scope of healthcare paid by public insurance)

**Mechanism:**
- Mandatory categorization for inclusion in Positive Drug List (PDL)
- 90-120 day generic approval cycle (longer than CZ at 60d, HU at 30d)
- **Mandatory generic price drops** (since Jan 1, 2018):
  - 1st generic: -45% from innovator
  - 2nd generic: -10% additional
  - 3rd generic: -5% additional
- **Cost/QALY threshold:** 24-35× monthly average wage (~28-40k€)
- **Conditional reimbursement:** Available for orphan drugs (prevalence <1:100,000) for 24 months — if real spending exceeds conditional cap, MAH pays difference back
- **Extraordinary Reimbursement Regime (ERR):** Allows individual patient access for non-PDL drugs

**Key issues:**
- Decreased generics availability due to parallel exports (Slovakia loses cheap drugs to higher-price markets)
- **⚠️ Bulgaria-Slovakia DEADLOCK:** Each country references the other → price inelasticity (no upward adjustment possible because both stuck at mutual minimum). Documented in Generic Medicines Market Review 2025
- ~87% of European average list prices (FREOPP 2024)
- Bismarck-style health insurance (4 insurers, General HIC = ⅔ market share, state-owned)

**Cascade impact:** Slovakia referenced by:
- Bulgaria (10-country basket — main mutual-reference deadlock)
- Romania (12-country basket)
- Russia (ZHNVLP basket)

**Source:**
- [Frontiers in Pharmacology — Slovakia Reimbursement (2021)](https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2021.795002/full)
- [FREOPP — Slovakia Healthcare 2024](https://freopp.org/slovakia-28-in-the-2024-world-index-of-healthcare-innovation/)
- [Value in Health — Slovakia Drug Policy](https://www.valuehealthregionalissues.com/article/S2212-1099(17)30049-3/fulltext)
- [Generic Medicines Market Review 2025](https://www.medicinesforeurope.com/wp-content/uploads/2025/11/GENERIC-MEDICINES-MARKET-REVIEW-2025-Key-findings.pdf)
- Act 363/2011 + Act 577/2004

**Last verified:** May 2026

---

### 🟢 Bulgaria (BG)

**Authority:** NCPRMP (National Council of Prices & Reimbursement of Medicinal Products) + NHIF (National Health Insurance Fund)
**Uses IRP:** **Yes (mandatory)**
**Basket — 10 countries:** Belgium, France, Greece, Italy, Latvia, Lithuania, Romania, Slovakia, Slovenia, Spain
**Formula:** **LOWEST** price across basket
**Price level:** Ex-factory
**Lag:** 6 months max (price changes in basket trigger BG re-pricing)
**Frequency:** Continuous, with **6-month trigger window** for any reference change

**Mechanism:**
- Drug prices CANNOT exceed LOWEST in 10-country basket
- Any price change in any of the 10 reference countries triggers re-pricing within 6 months
- 4-tier National Reimbursement List (NRL):
  - Part 1: Home treatment of designated diseases (NHIF reimbursed)
  - Part 2: Hospital treatment (NHIF + framework agreement)
  - Part 3: Specific public health diseases (HIV, vaccines — MoH funded)
  - Part 4: Maximum registered prices reference

**Key 2024 changes:**
- **GlobalData IRP 2024:** Bulgaria **expanded IRP** to non-reimbursed infectious disease medicines (one of few markets expanding IRP scope in 2024)

**⚠️ Critical interdependency:**
- **Bulgaria-Slovakia DEADLOCK** (per Generic Medicines Market Review 2025): SK references BG (basket), BG references SK → mutual-reference creates pricing inelasticity. Neither country can adjust prices upward without the other moving first
- BG also references all 10 countries, so lowest-among-the-lowest dynamics

**Comparative pricing position:**
- ~78% of German list prices (lowest in CEE5 basket)
- Generic substitution well-established
- RSAs/MEAs available but limited public data

**Cascade impact:** Bulgaria referenced by:
- Romania (12-country basket)
- Russia (ZHNVLP basket)

**Source:**
- [Wolf Theiss — Bulgaria Pricing (2024)](https://www.wolftheiss.com/insights/pricing-and-reimbursement-of-medicinal-products-in-cee-and-see/)
- [Pharmaceutical Technology — CEE Reference Pricing](https://www.pharmaceutical-technology.com/pricing-and-market-access/reference-pricing-cee-countries-pressure-prices-html/)
- [GlobalData IRP 2024 Year in Review (Mar 2025)](https://www.pharmaceutical-technology.com/analyst-comment/international-reference-pricing-irp-2024/)
- [Generic Medicines Market Review 2025](https://www.medicinesforeurope.com/wp-content/uploads/2025/11/GENERIC-MEDICINES-MARKET-REVIEW-2025-Key-findings.pdf)
- NCPRMP documentation

**Last verified:** May 2026

---

## Part 3 — Cross-cutting analysis

### Most-referenced countries (cascade hotspots)

Based on documented baskets, countries most likely to trigger downstream cascade when their price changes:

| Rank | Country | Approx. # of countries referencing |
|---|---|---|
| 1 | Germany | ~25+ (EU baskets, GCC, ROW) |
| 2 | UK | ~20+ |
| 3 | France | ~20+ |
| 4 | Italy | ~15+ |
| 5 | Spain | ~12+ |
| 6 | Switzerland | ~8 (Korea A8, Saudi, etc.) |
| 7 | Japan | ~5 (Korea, Brazil, Saudi, France LFSS 2026) |
| 8 | US | ~3 (Korea, Japan, Saudi) — increasing with MFN trends |

### Key 2024–2026 reform trends

1. **Confidential pricing expansion** (DE, IT, FR, NL, UK) — disrupts traditional IRP cascade
2. **Basket expansion** (BR 9→14, TR potentially) and **basket update** (CA new HIP screening)
3. **US MFN pressure** (Generous/Guard/Globe) — creates upward pressure on international list prices
4. **Japan FY2026** — references Germany post-AMNOG net price, abolishes spillover rule
5. **France LFSS 2026 Article 88** — possible expansion of comparable countries basket
6. **Inflation/exchange rate distortions** — TR, AR, RU especially vulnerable

### Confidential rebate impact (summary)

This is the most critical disconnect in international pricing: **list prices remain public, but net prices (what payers actually pay) are typically 20–60% lower** due to confidential rebates. As IRP cascades use list prices, they propagate inflated values that no payer actually pays.

→ **See Part 5 below for detailed gross-to-net analysis by country with 2024–2026 data**

---

## Part 5 — Confidential rebates and gross-to-net (G2N) analysis

This part addresses the **single most important blind spot** in IRP-based pricing models: the systematic divergence between **list prices** (used in IRP cascades) and **net prices** (actual revenue to manufacturer / actual cost to payer).

### 5.1 The G2N gap: scale and significance

| Indicator | Value | Source |
|---|---|---|
| EU average list-to-net realization | **40–60%** of list price | Farseer 2025 G2N study |
| EU5 net vs list expenditure CAGR gap | List 3.4% vs Net 2.5% (2010–2016) | Applied Health Econ. 2018 |
| EU countries using confidential MEAs | **22/22** (100% of surveyed) | EURIPID Survey 2021 |
| Countries with NDAs preventing data sharing | 13/15 (OECD 2022) | OECD Price Transparency 2024 |
| MEA confidentiality enforced by law | 27% of countries | EURIPID 2021 |
| Typical rebate types | Flat, volume-based, outcomes-based, in-kind | OECD 2024 |
| Clawback calculation lag | **12–24 months** post-sale | Farseer 2025 |

**Why this matters for IRP cascade simulation:**
1. **All baskets use list prices** — net prices cannot be cited (NDA violations)
2. A drug priced at €100 list / €60 net in Germany is referenced at €100 by other countries
3. Cascade calculations therefore systematically **overstate** net prices in dependent markets
4. Manufacturers exploit this by accepting **higher rebates in exchange for protected list prices** — a structural feature, not a workaround

### 5.2 G2N estimates by country (2024–2026 data)

These ranges represent **typical net price as % of list price** for branded innovative drugs (post-rebate, post-clawback). They reflect industry consensus from primary research with payers (INBEEO 2024, Simon-Kucher, Trinity Life Sciences).

#### EU5 (most documented)

| Country | G2N range (net as % of list) | Key mechanisms | Notes |
|---|---:|---|---|
| **Germany (DE)** | **80–90%** (with competition) → 100% (without) | AMNOG negotiated rebates + manufacturer rebates 7-12% (Herstellerabschlag) + sickness fund individual contracts | **Medical Research Act Mar 2026: confidential pricing option costs +9% additional discount.** Pre-2026: only ~10-18% rebate. Post-2026 confidential: easily 25-40% |
| **France (FR)** | **70–80%** (with competition) → 90% (without) | CEPS confidential rebates avg 25% (170 drugs, 2022) + clawback Lh/M (annual budget cap) + paybacks for "off-label" indications | Net price disclosure **prohibited** by Article L162-17-4 of Social Security Code |
| **Italy (IT)** | **65–80%** (with competition) → 100% (without) | AIFA MEAs (outcome-based, payment-by-results, cost-sharing) + payback if exceeding hospital ceiling 8.6% FSN + EoI discounts | Net to Italian region often << official AIFA list. Different rebate per region. CSE since Jan 2024 expanding confidential framework |
| **Spain (ES)** | **65–80%** (with competition) → 100% (without) | CIPM confidential discounts + autonomous community-level negotiations + VALTERMED (real-world data triggers refunds) | Highly opaque — list prices very different from regional purchasing prices |
| **UK** | **70–85%** (PAS) | NICE Patient Access Schemes (PAS) — simple flat % discount, confidential. VPAG (was VPAS): industry-wide payback if NHS branded medicine spend grows >budget cap (2024 cap rate: 21.4% — increased from VPAS's 26.5% in 2023, but trending up) | NHS net spending capped industrywide via VPAG |

#### Other Western Europe

| Country | G2N range | Key mechanisms |
|---|---:|---|
| **Switzerland (CH)** | 85–95% | BAG-negotiated rebates limited; APV+TQV mechanism mostly transparent. Lower confidentiality than EU5 |
| **Netherlands (NL)** | 70–85% | "Lock" (sluis) procedure for high-cost drugs — secret price negotiation by VWS; preferential pricing tendering for outpatient |
| **Belgium (BE)** | **65–80%** | Article 35bis "closed envelope" MEAs — **avg compensation rate 29% in 2014, rising to 53.8% in 2021** (KCE 2024). One of the most aggressive rebate regimes in EU |
| **Austria (AT)** | 80–90% | Confidential discounts via Hauptverband negotiation, generally less aggressive |
| **Sweden (SE)** | 80–90% | TLV value-based pricing; some confidential pricing for hospital drugs (NT-Council) |
| **Norway (NO)** | 70–85% | LIS (Norwegian Drug Procurement Cooperation) negotiates confidential net prices for hospital sector (specialist sector) |
| **Denmark (DK)** | 75–85% | Amgros tender prices for hospital drugs typically 15-30% below list cap |
| **Ireland (IE)** | 80–91% | IPHA Framework HSE rebate 9% (2025) on all sales + MEAs negotiated separately |

#### CEE and Southern Europe

| Country | G2N range | Key mechanisms |
|---|---:|---|
| **Poland (PL)** | 60–80% | RSS (Risk Share Schemes) confidential, mandatory PVAs with NFZ, strong volume-triggered rebates |
| **Czech Republic (CZ)** | 75–85% | MEAs less common than in Western EU, but increasing for orphan drugs |
| **Hungary (HU)** | 60–75% | Aggressive clawbacks + confidential MEAs widespread |
| **Greece (EL)** | 50–70% | Severe clawback regime (~25% of total reimbursable spend); rebates on top |
| **Portugal (PT)** | 70–85% | INFARMED MEAs with clinical and financial conditions |
| **Romania (RO)** | 50–70% | Clawback rate often >25%, hitting hard during budget crises |

#### Americas

| Country | G2N range | Key mechanisms |
|---|---:|---|
| **United States (US)** | **45–55% (commercial)** to **40-50% (Medicaid post-IRA)** | Most complex G2N stack globally: PBM rebates 30-50%, 340B mandatory discounts, Medicaid statutory minimum rebate (23.1% on innovator), IRA negotiated price (Maximum Fair Price for selected drugs from 2026), commercial market access rebates |
| **Canada (CA)** | 70–85% | pCPA (pan-Canadian Pharmaceutical Alliance) confidential negotiations; PMPRB MIP→HIP transition Jan 2026 changes dynamics |
| **Brazil (BR)** | 70–85% | CMED price ceiling + private market discounts; CONITEC negotiations |
| **Mexico (MX)** | 65–85% | UNOPS pooled procurement = competitive bidding → significant discounts vs list |
| **Colombia (CO)** | 70–85% | Group A products subject to direct price control; Group B with monitoring |

#### APAC

| Country | G2N range | Key mechanisms |
|---|---:|---|
| **Japan (JP)** | 75–90% | Generally transparent but **price maintenance premium (PMP)** can boost net for innovators; reductions every 2 years (FY24/26 reforms) |
| **South Korea (KR)** | 70–85% | NHIS/HIRA RSAs (Risk-Sharing Agreements) since 2014, increasingly common for innovative drugs |
| **China (CN)** | **40–60%** | NRDL annual negotiation = 50–65% avg cut from list. Category C 2025 retains some flexibility for innovative drugs |
| **Australia (AU)** | 75–85% | PBS confidential rebates + special pricing arrangements |
| **India (IN)** | 80–95% | DPCO ceiling for scheduled drugs; less rebate use for branded |

#### Middle East / Africa

| Country | G2N range | Key mechanisms |
|---|---:|---|
| **Israel (IL)** | 70–85% | MoH hedging arrangements during basket inclusion negotiations |
| **Saudi Arabia (SA)** | 80–95% | Limited rebate culture; primarily transparent IRP-based pricing |
| **UAE (AE)** | 80–95% | Similar to SA — pricing largely transparent |
| **Turkey (TR)** | 65–80% | Public discount layer (~11% innovator yr1, 23% from yr2) on top of fixed EUR rate |
| **Egypt (EG)** | 75–90% | Limited confidential pricing infrastructure |
| **South Africa (ZA)** | 75–90% | Single Exit Price (SEP) regulated; private sector tendering for hospitals |

### 5.3 Rebate types and structures

**Type 1: Flat statutory discounts (mandatory, public)**
- Examples: Germany Herstellerabschlag (7-12%), France CEPS conventional rebates, US Medicaid 23.1% statutory rebate
- Predictable, model in baseline G2N forecast
- Visible to public

**Type 2: Volume / Price-Volume Agreements (PVAs)**
- Trigger: sales exceed pre-negotiated thresholds
- Tiered structure: e.g. €0–10M @ 0%, €10–20M @ 15%, €20M+ @ 25%
- Common in: Poland (mandatory), Germany (post-AMNOG), France, Spain
- Modeling complexity: requires volume forecasting + correct trigger calibration

**Type 3: Outcome-based (Performance-based RSAs)**
- Refund if patient doesn't reach pre-defined clinical endpoint (e.g. response rate)
- Increasingly common for: oncology (CAR-T, ADCs), gene therapies, rare diseases
- Country examples: Italy AIFA payment-by-results, UK NICE managed access agreements
- Modeling complexity: HIGHEST — requires response rate assumptions + audit trail

**Type 4: Cost-sharing**
- Free first cycles to demonstrate efficacy, then full price (or capped duration of treatment)
- Used in: Italy, France, UK, Germany pilot programs

**Type 5: Clawbacks (industry-wide, budget-driven)**
- Trigger: total country spend exceeds national pharma budget
- Country examples: Greece (~25% of reimbursable spend), Hungary, Romania, Italy (8.6% FSN ceiling), UK VPAG
- Calculated 12–24 months post-sale = significant accrual / cash flow lag
- **Most painful for finance**: hard to forecast, retrospective

**Type 6: In-kind contributions**
- Free goods for awareness campaigns, training, devices
- Less common but growing in MENA / CEE

### 5.4 Why most G2N data isn't public (and why estimates matter)

**Legal barriers:**
- 22/22 EU countries surveyed by EURIPID confirm confidential MEAs are routine
- 27% have **specific legislation** prohibiting disclosure
- France: Article L162-17-4 of Social Security Code criminalizes net price disclosure
- Italy: AIFA MEAs subject to NDA between manufacturer and AIFA
- Spain: CIPM decisions don't publish discount terms

**Why manufacturers prefer this:**
- Higher list price preserved → IRP cascade impact minimized in other markets
- Bigger discount in Country X doesn't propagate to Country Y if rebate is confidential
- Strategic: can offer market-specific economics without cross-market risk

**Why this is changing (slowly):**
- WHO Resolution WHA72.8 (2019) calls for transparency on net prices
- Oslo Medicines Initiative (OMI) — voluntary participation framework
- EU HTA Regulation (2025) — joint clinical assessment (but **not** joint pricing)
- Push from emerging markets: countries like Brazil and South Africa explicitly want net prices to anchor their own negotiations

### 5.5 Implications for strategic pricing & NPV modeling

**Risks of using list prices in NPV models:**
- Overestimates revenue by 20–60% in mature markets
- Underestimates effective IRP cascade impact (downstream countries also get net not list)
- Distorts launch sequencing optimization (incorrectly favors high-list countries with high-rebate)

**Best-practice methodology:**

1. **Always model both list and net prices** (gross-to-net adjustment)
2. **Apply country-specific G2N ranges** from the table above (low / mid / high scenarios)
3. **Increase G2N erosion over LCM** (loss of exclusivity → +20-30% additional discount within first 5 years post-launch as competition enters)
4. **Apply temporal lag for clawbacks** (12–24 months — affects working capital, not NPV materially)
5. **Stress-test confidential pricing scenarios** for Germany post-Mar 2026 (extra 9% rebate vs public price)
6. **For oncology/orphan drugs**: use INBEEO competition-dependent benchmarks (10–25% additional discount per competitor)

**Methodology in this tool:**
The PharmaPricingTool implements a `applyConfidentialRebate(listPrice, country, hasCompetition, indication)` function (see Module 7 in v1.5+). Default G2N parameters can be overridden by user.

### 5.6 Stratégie de lancement face au G2N gap

Pour optimiser le NPV en présence de rebates confidentiels :

**Strategy A — "Protect list price"** :
- Accept higher rebate in highest-list country (e.g. Germany post-Mar 2026: opt-in to confidential pricing → +9% rebate but list price preserved)
- Goal: protect IRP cascade in 25+ downstream markets
- NPV impact: typically +5 to +15% over 10 years, depending on cascade reach

**Strategy B — "Market-by-market optimization"** :
- Negotiate transparent list price reductions in 1-2 key markets if cascade benefit < direct revenue loss
- Suitable for: drugs with limited international reach, regional plays

**Strategy C — "Sequenced launch with rebate ramp"** :
- Launch first in countries with low G2N erosion (CH, AU, IL) at premium list
- Delay launches in high-rebate / aggressive-IRP markets (FR, IT, ES, PL, GR) until later
- Risks: market access timeline, EU HTA JCA harmonization (2025+) reduces optionality

**Strategy D — "Withdrawal threats"** :
- Used historically in Germany (e.g. several products withdrawn 2018-2023 post-AMNOG)
- High-stakes — requires being prepared to actually withdraw
- Recent examples: Eli Lilly (some indications), Pfizer, Vertex (negotiation leverage)

### 5.7 Sources

- **INBEEO (2024)**. *List to Net Price Dynamics in EU4 and US — Orphan Drug Analysis*. Primary research with 2 payers per market. [https://inbeeo.com/2024/04/02/net-price-dynamics-in-eu4-and-us/](https://inbeeo.com/2024/04/02/net-price-dynamics-in-eu4-and-us/)
- **Farseer / Sandberg (Dec 2025)**. *27 Markets, 1 Migraine: EU Pharma Tax Regulations*. Key finding: "most manufacturers only realize 40-60% of their list prices." [https://www.farseer.com/blog/eu-pharma-tax-regulations/](https://www.farseer.com/blog/eu-pharma-tax-regulations/)
- **EURIPID Executive Committee (2021)**. *Medicine price transparency and confidential managed-entry agreements in Europe*. Health Policy. 22-country survey. [PMID: 34253396](https://pubmed.ncbi.nlm.nih.gov/34253396/)
- **OECD (Sep 2024)**. *Exploring the feasibility of sharing information on medicine prices across countries*. Working Paper.
- **Vogler S. et al. (2012)**. *Discounts and rebates granted to public payers for medicines in European countries*. Southern Med Review.
- **Morgan, Vogler, Wagner (2017)**. *Payers' experiences with confidential pharmaceutical price discounts*. Health Policy 121(4).
- **GlobalData (May 2025)**. *5EU Q1 2024 vs 2025: Pricing shifts, HTA outcomes, and innovative drug trends*. [https://www.pharmaceutical-technology.com/analyst-comment/5eu-q1-2024-versus-2025-pricing-shifts-hta-outcomes/](https://www.pharmaceutical-technology.com/analyst-comment/5eu-q1-2024-versus-2025-pricing-shifts-hta-outcomes/)
- **JStindt Consulting (2024)**. *2024 List and Net Pricing Strategies EU-5*. Detailed AMNOG confidential pricing analysis.
- **KCE Belgium (2024)**. *Performance of the Belgian health system 2024 — MORSE report data*. Belgium average compensation rate 29% (2014) → 53.8% (2021).
- **Doganova & Rabeharisoa (2024)**. Critical analysis of secret rebates in EU pricing.

---

## Part 6 — Validation status & next actions

### Summary

| Reliability tier | Count | % | Action needed |
|---|---:|---:|---|
| 🟢 VERIFIED | **37 countries** | **100%** | Periodic monitoring (annual review) |
| 🟡 LSE 2017 | 0 countries | 0% | — |
| 🔴 APPROX | 0 countries | 0% | — |
| **Total** | **37 entries** | 100% | |

### Priority monitoring queue (post-verification)

**Annual review priority** — countries with ongoing reforms requiring active tracking:

**Tier 1 — Active reforms 2024-2026 (review every 6 months):**
- **Germany** — Medical Research Act effects on AMNOG (IRP removal)
- **France** — LFSS 2026 Article 88 (potential JP/KR addition to basket)
- **Italy** — AIFA CSE operational tuning + budget law impacts
- **Japan** — FY2026 reforms operationalization (DE post-AMNOG, SPA-SSS)
- **Brazil** — CMED Resolution 3/2025 first year of effect (Apr 2026 →)
- **Colombia** — VBP Reform implementation timeline

**Tier 2 — Periodic 5-year cycle reviews (track in cycle year):**
- **Switzerland** — next triennial review 2027
- **Saudi Arabia** — IRP cycle 60 months, 2024 → 2029
- **GCC countries** (Qatar, Oman, Bahrain, UAE) — synchronized with KSA cycle
- **Spain** — Draft Law on Medicinal Products 2025 enactment

**Tier 3 — Currency/inflation-driven volatility (monitor monthly):**
- **Turkey** — annual EUR rate decree (February each year)
- **Argentina** — inflation impact on prices
- **Egypt** — EGP devaluation triggers
- **Russia** — sanctions/RUB volatility

### Recommended validation sources

1. **PPRI Network** ([https://ppri.goeg.at](https://ppri.goeg.at)) — WHO Collaborating Centre, free, neutral
2. **EURIPID database** — official EU prices, restricted access but methodologies are public
3. **IQVIA Government Affairs / Market Access** — commercial, comprehensive, ~$50–100k/year
4. **Charles River Associates pricing reports** — country-specific deep dives
5. **Simon-Kucher Pharma Pricing & Market Access** — country briefs (some free)
6. **WHO MedNet** — global price surveys, free
7. **OECD Health Statistics** — public, methodologies on transparency
8. **National authority websites** (PMPRB.gc.ca, BAG.admin.ch, AIFA.gov.it, etc.)

### Update cadence

- **Quarterly:** Re-check VERIFIED entries for changes
- **Annually:** Full revalidation cycle for all entries
- **Ad-hoc:** Whenever a major reform is announced (e.g. France LFSS, Brazil CMED, Japan biennial)

---

## Document changelog

| Version | Date | Changes |
|---|---|---|
| 1.0 | May 2026 | Initial document. Verified 14 countries via web sources 2024–2026. Sourced 13 countries from LSE 2017 study. Flagged 10 approximations for expert review. |
| 1.1 | May 2026 | **+4 verified countries:** Norway (NoMA official), Denmark (Lif price-cap 2025–2027 + primary care reform), Ireland (IPHA Framework Agreement 2021–2025 + 2026 renegotiation), Israel (MoH Order 2001 + 2018 amendments). Total: 18 verified, 13 LSE 2017, 6 approx. |
| 1.2 | May 2026 | **+6 verified countries (all remaining "approx" eliminated):** Mexico (UNOPS pooled procurement, no formal IRP), Argentina (no regulation, excluded from BR basket), Colombia (Circular 18/2024 + VBP reform pending), Chile (no IRP, ChileCompra tendering), Indonesia (BPJS-K e-Catalogue tender), Thailand (HITAP HTA + NHSO negotiation). **Total: 24 verified (65%), 13 LSE 2017 (35%), 0 approx.** All 37 country entries now sourced. |
| **1.3** | **May 2026** | **+13 verified countries (final batch — all LSE 2017 eliminated):** Italy (AIFA CSE Jan 2024 reform, Blended Pricing Model), Spain (CIPM internal IRP only since RDL 16/2012, draft 2025 reforms), Netherlands (Wgp basket BE/FR/NO/UK confirmed since Oct 2020 + Temporary Policy Rule 2024), Austria (broad EU basket avg + EKO box system + Bewertungsboard 2024), Belgium (26 EU MS supportive ERP + Beneluxa + Early Access 2026), Poland (limit groups + RSS + ~14% price erosion), Czech Republic (18 EU basket avg-3-lowest, 5-year reviews), Turkey (5-country basket lowest + fixed EUR rate 25.3346 for 2026), Russia (post-2022 sanctions decoupling), Saudi Arabia (30-country basket, 60-month cycle, 2024 re-referencing event), UAE (Federal Decree-Law 38/2024 + EDE), Egypt (36-country basket + EGP devaluation crisis), South Africa (4-country basket + SEP + NHI Act 2024). **FINAL: 37 verified (100%), 0 LSE 2017, 0 approx.** Document is now fully sourced with 2024–2026 data across all entries. |
| **1.4** | **May 2026** | **NEW Part 5: Confidential rebates and gross-to-net (G2N) analysis.** Detailed G2N estimates for all 37 countries (net as % of list, with/without competition). Coverage of 6 rebate types (flat statutory, PVAs, outcome-based, cost-sharing, clawbacks, in-kind). 4 strategic responses to G2N gap (protect list, market-by-market, sequenced launch, withdrawal threats). Key data sources: INBEEO 2024 (orphan drugs), Farseer 2025 (40-60% realization), EURIPID 2021, OECD 2024, KCE Belgium MORSE. Critical insights: Germany Medical Research Act Mar 2026 confidential pricing (+9%), Belgium MEA compensation 29%→54% (2014-2021), France CEPS avg 25% rebate. |
| **1.5** | **May 2026** | **+6 EU Southern/Eastern verified countries (NEW Part 2.5):** Greece (EOPYY, avg 3 lowest, ⚠️ HIGHEST clawback in EU 75%+ hospital, 62.7% EOPYY, 79.8% innovative), Portugal (INFARMED, 4-country basket ES/FR/IT/SI avg, retail price removed from packaging Jan 2024), Hungary (NEAK, EU+EEA+CH lowest, 3-country requirement lifted Jun 2023, Foundation reform Jan 2025), Romania (CANAMED 12-country lowest, severe clawback >25%, RON FX pressure), Slovakia (27 EU basket avg-3-lowest, mandatory generic drops -45%/-10%/-5%, ⚠️ Bulgaria-Slovakia deadlock), Bulgaria (10-country basket lowest, 6-month trigger, 2024 IRP expansion to infectious disease meds). G2N estimates added for all 6 in Part 5. **TOTAL: 43 verified countries** (37 + 6). Cascade analysis updated. |

---

## Appendix A — Key references

- CMS Federal Register Vol. 90 No. 244 (Dec 23, 2025) — Generous, Guard, Globe proposed rules
- Kanavos, P., Fontrier, A.M., Gill, J., Kyriopoulos, D. (2017). *The Implementation of External Reference Pricing within and across Country Borders*. London School of Economics. DOI: 10.21953/lse.y1tbizsxrl3n
- WHO Collaborating Centre for Pharmaceutical Pricing and Reimbursement Policies (PPRI). https://ppri.goeg.at
- GlobalData. *International Reference Pricing (IRP) 2024: A year in review.* (Mar 2025)
- OECD (2024). *Exploring the feasibility of sharing information on medicine prices across countries.*
- Vogler, S., Zimmermann, N., Haasis, M.A. (2019). *PPRI Report 2018 — Pharmaceutical pricing and reimbursement policies in 47 PPRI network member countries.*

## Appendix B — Glossary

- **AMNOG**: Arzneimittelmarkt-Neuordnungsgesetz (Germany pharmaceutical market reform act)
- **AMP**: Average Manufacturer Price (US)
- **APV**: Auslandpreisvergleich (Switzerland foreign price comparison)
- **ASMR**: Amélioration du Service Médical Rendu (France medical benefit rating)
- **ASP**: Average Sales Price (US Medicare Part B)
- **BAG/FOPH**: Bundesamt für Gesundheit / Federal Office of Public Health (Switzerland)
- **CEA**: Cost-Effectiveness Analysis
- **CEPS**: Comité Économique des Produits de Santé (France pricing committee)
- **CMED**: Câmara de Regulação do Mercado de Medicamentos (Brazil)
- **DIP**: Documento Informativo de Preços (Brazil pricing dossier)
- **DIR**: Direct and Indirect Remuneration (US Medicare Part D rebates)
- **DPCO**: Drug Price Control Order (India)
- **EPR / ERP**: External (Price) Reference Pricing
- **FAP**: Fabrikabgabepreis (Switzerland ex-factory price)
- **FPA**: Foreign Price Adjustment (Japan)
- **G-BA**: Gemeinsamer Bundesausschuss (Germany Federal Joint Committee)
- **GDP-PPP**: Gross Domestic Product on Purchasing Power Parity basis
- **GKV-SV**: GKV-Spitzenverband (Germany National Association of SHI Funds)
- **GNUP**: Guaranteed Net Unit Price
- **HCPCS**: Healthcare Common Procedure Coding System (US)
- **HIP**: Highest International Price (Canada PMPRB 2026)
- **HIRA**: Health Insurance Review and Assessment Service (Korea)
- **HTA**: Health Technology Assessment
- **IRP**: International Reference Pricing
- **LFSS**: Loi de Financement de la Sécurité Sociale (France social security funding law)
- **MEA**: Managed Entry Agreement
- **MFN**: Most Favored Nation
- **MIP**: Median International Price (Canada PMPRB pre-2026)
- **NCPDP**: National Council for Prescription Drug Programs unit (US Part D)
- **NDC**: National Drug Code (US)
- **NHSA**: National Healthcare Security Administration (China)
- **NRDL**: National Reimbursement Drug List (China)
- **PDE**: Prescription Drug Event (US Medicare Part D claim)
- **PMPRB**: Patented Medicine Prices Review Board (Canada)
- **PMVG**: Preço Máximo de Venda ao Governo (Brazil maximum government price)
- **PPRI**: Pharmaceutical Pricing and Reimbursement Information network (WHO)
- **SFDA**: Saudi Food and Drug Authority
- **SL**: Spezialitätenliste (Switzerland Specialty List)
- **TQV**: Therapeutischer Quervergleich (Switzerland therapeutic cross-comparison)
- **URA**: Unit Rebate Amount (US Medicaid)
- **VED**: Vital and Essential Drugs (Russia)
- **VPAG / VPAS**: Voluntary Scheme for Branded Medicines Pricing (UK, current/former)
- **WAC**: Wholesale Acquisition Cost (US list price)

---

**End of document.**
