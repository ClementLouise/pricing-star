# Product Vision

## Mission

**Help mid-cap pharma pricing teams identify, quantify, and respond to MFN regulatory risk before it impacts NPV.**

## The problem

The CMS MFN regulations (Generous, Guard, Globe) — proposed Dec 2025 — introduce mandatory rebate calculations tied to international reference prices across 19 OECD countries. For mid-cap pharma (Vertex, Regeneron, Ipsen, etc.), these regulations create three operational challenges:

1. **MFN risk is profile-dependent**, not uniform. Some assets are structurally protected (orphan premium with high ex-US prices), others are structurally exposed (oncology biologics with mid-tier ex-US pricing). Without dedicated tooling, mid-caps cannot reliably tell which is which.

2. **Method I anchor is non-obvious**. Under CMS multiply convention (`PPP-adjusted price = nominal × adjuster`), the Method I anchor is almost always CH/IE/NO (PPP=1.000), not the lowest-nominal-price markets like Italy or Czech Republic. Excel-based analysis routinely misses this.

3. **IRP cascade is complex**. 43 markets reference each other in dense webs (e.g., 27 markets reference Germany). A 9pp cut to Germany's disclosed price cascades to ~$2.76B NPV harm for a typical mid-cap launch — but quantifying this requires multi-iteration cascade simulation that Excel cannot reliably do.

## The solution

A **multi-tenant SaaS platform** that gives mid-cap pharma pricing teams:

- **MFN risk classification** for any asset in their portfolio (orphan premium, specialty premium, mid-tier biologic, aggressive ex-US)
- **Automated Method I anchor identification** with PPP normalization
- **43-market IRP cascade simulation** with convergence detection
- **NPV impact quantification** with confidence intervals (Monte Carlo G2N)
- **Audit-grade decision documentation** (SOX 404 ready)
- **Strategic mitigation recommendations** profile-specific

## Target users

### Primary persona: Sarah Chen, Mid-Cap Pricing Lead

- 8-15 years experience, Director-level
- Reports to VP Commercial / VP Pricing & Market Access
- Manages pricing strategy across 5-15 pipeline assets
- Currently spends 70%+ of time in Excel doing what should be automated
- Pain: "I cannot run an MFN scenario across all our assets in less than 2 weeks"
- Gain: "I want to walk into the next QBR with portfolio-level MFN exposure quantified"

### Secondary persona: Marcus Reyes, CFO

- 15-25 years experience, C-suite
- Decides on which assets to advance based on NPV projections
- Pain: "Pricing tells me $X NPV is at risk but I cannot defend the methodology to my board"
- Gain: "I want decision-grade documentation for every pricing call we make"

### Tertiary persona: Elena Volkov, Regulatory Affairs

- 10-20 years experience, Senior Director
- Validates that pricing decisions comply with CMS regulations
- Pain: "Pricing teams' Excel models don't surface the methodology — I can't audit them"
- Gain: "Audit JSON exports give me defensible records of every pricing decision"

(Full persona details in `personas_brief.docx`.)

## Why now

Three converging forces make this the right time to build:

1. **CMS final rules expected mid-2026**. Mid-cap pharma needs operational tooling before phase-in begins (2026 −10%, 2027 −20%, 2028+ −30%).

2. **Excel-based analysis is breaking**. The complexity of multi-method MFN calculations + 43-market cascades + PPP adjustment exceeds what's reliably maintainable in spreadsheets.

3. **Big pharma has internal tools; mid-cap doesn't**. The major pharma companies (Pfizer, Roche, Novartis) have dedicated pricing intelligence teams with custom tooling. Mid-cap pharma is currently stuck with consultants ($500K+ per engagement) or Excel. The market gap is real.

## Competitive positioning

| Competitor | Strength | Gap we fill |
|------------|----------|-------------|
| Big consultancies (BCG, IQVIA Consulting) | Strategic depth, executive relationships | Slow ($500K+ engagements), one-off analyses |
| IQVIA Pricing Insights | Data depth | No MFN-specific modeling, no cascade engine |
| Eversana NAVLIN | Reference price data | Not interactive, no scenario simulation |
| Internal Excel models | Customized to firm | Brittle, untestable, not audit-grade |

**Our positioning**: "The first MFN-native pricing intelligence platform built for mid-cap pharma. Faster than consultancies, more rigorous than Excel, dedicated to the new regulatory landscape."

## Success metrics

### Product metrics (12 months post-launch)
- 10+ paying tenants
- 80%+ retention rate (annual)
- Average 5+ users per tenant
- 90%+ of pricing decisions backed by audit JSON export

### Business metrics
- ARR target: $5M by month 12
- ACV target: $400-600K per tenant
- Sales cycle: 4-6 months (typical for mid-cap pharma SaaS)

### User metrics
- Time-to-first-value < 4 hours from signup
- 70%+ time savings on MFN analyses (vs. Excel baseline)
- NPS ≥ 40

## Strategic constraints

These are **product principles**, not engineering constraints:

1. **Methodology rigor over feature breadth**. We will say "no" to features that compromise calculation defensibility. Every formula must be backed by CMS rule citations.

2. **Mid-cap focus, not enterprise sprawl**. We resist building features that only matter for top-10 pharma (e.g., 10,000-user tenancy, custom workflow engines).

3. **Demo-driven sales**. The product must be demo-able in 30 minutes to a pricing committee. Features that don't survive a demo are deprioritized.

4. **Audit-first defaults**. Every action that affects NPV is logged. Audit JSON is one click away from any scenario.

## Vision (3 years out)

If v2.0 succeeds:

- **v3.0** (year 2): Custom IRP rule editor, multi-asset portfolio view, IQVIA/Eversana API integrations
- **v4.0** (year 3): Markov demand modeling, payer-specific NPV (Medicaid vs Medicare vs commercial), expansion to EU drug pricing regulations

The v2.0 build must be architected to support these expansions without fundamental rewrites.

## Out-of-scope for v2.0 (explicit non-goals)

- Replace consultancies entirely (we complement them)
- Cover therapeutic areas beyond pharma (no medical devices, no diagnostics)
- Predict FDA approval timelines (we model post-approval pricing only)
- Generate marketing/launch materials (we produce strategic analysis only)
- Compete with Veeva (CRM, content management) or with Symphony (sales analytics)

## The "elevator pitch" version

> *"Mid-cap pharma is about to face mandatory MFN rebates that could erode 10-20% of NPV on key launches. Excel can't handle the math. Big consultancies cost $500K per engagement. We're building the first SaaS platform purpose-built for MFN-aware pricing intelligence — automated Method I anchor identification, 43-market cascade simulation, audit-grade decision documentation. 6 months to MVP, $5M ARR target year 1."*

---

*Next: read `02_TECH_STACK.md`*
