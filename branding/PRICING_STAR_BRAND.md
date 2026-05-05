# Pricing Star — Branding Guide

Quick branding reference for Pricing Star, used during the production build to ensure consistency in UI, documentation, and marketing-adjacent surfaces.

## Name

**Product name**: Pricing Star
**Pronunciation**: /ˈpraɪsɪŋ stɑːr/ — "PRY-sing STAR"
**Tagline (working)**: *"Navigate MFN. Defend NPV."*

Alternative taglines for different contexts:
- For pricing analysts: *"Your daily pricing intelligence"*
- For CFOs: *"Audit-grade pricing decisions"*
- For board: *"The MFN-native pricing platform"*

## Positioning statement

> *"Pricing Star is the first MFN-native pricing intelligence platform built for mid-cap pharma. Faster than consultancies, more rigorous than Excel, dedicated to the new regulatory landscape."*

## Brand attributes

| Attribute | Description |
|-----------|-------------|
| **Authority** | Decisions backed by CMS rule citations and audit-grade documentation |
| **Clarity** | Surfaces non-obvious insights (Method I anchor, DE cascade trap) immediately |
| **Speed** | Replaces weeks of Excel work with seconds of platform analysis |
| **Trust** | Methodology rigor, transparent errata handling, defensible outputs |

## Visual identity

### Logo concept

A stylized 4-pointed compass star (★ or ✦) — evoking:
- **Star** = guidance, leadership, "the star asset" in a pharma portfolio
- **Compass** = navigation through regulatory complexity
- **4 points** = the 4 strategic directions surfaced by the platform (Generous / Guard / Globe / IRP cascade)

Logo wordmark: "Pricing Star" with the star icon to the left:
```
✦  Pricing Star
```

### Color palette

Inherits from the V1.7 design system (`docs/PRD_v2/06_UI_COMPONENTS.md`):

| Color | Hex | Usage |
|-------|-----|-------|
| **Navy** | `#0F1B2D` | Primary brand color, headers, primary buttons |
| **Gold** | `#B8860B` | Accent, KPIs, the "star" element |
| **Red** | `#C00000` | MFN exposure indicators, alerts |
| **Green** | `#2E7D32` | Positive outcomes, "MFN escapes" |
| **Background dark** | `#0D1117` | App background (dark theme) |

The Navy + Gold pairing is the signature combo. Red and Green are functional only.

### Typography

| Use | Font | Notes |
|-----|------|-------|
| Headlines | Calibri / system display | Per V1.7 prototype |
| Body | System sans-serif (Apple/Segoe/Helvetica) | High readability |
| Code/data | SF Mono / Monaco / Inconsolata | For audit JSON, prices |

## Tone of voice

### Do

- **Direct and confident.** "MFN exposure: $894M at risk." Not "There may be some exposure."
- **Cite sources.** "Per CMS § 514.5, the PPP adjuster..." 
- **Use plain English.** Avoid jargon when possible. Define on first use when unavoidable.
- **Quantify.** "70% time savings" not "significant time savings."

### Don't

- **Don't be playful with the data.** This is high-stakes financial decision support.
- **Don't oversell.** The product has real edge cases and limitations; surface them.
- **Don't use marketing fluff.** "Revolutionary," "game-changing," "best-in-class" — avoid.
- **Don't anthropomorphize.** "The platform identifies..." not "Pricing Star believes..."

## Naming conventions

For technical artifacts that reference the product:

| Context | Convention | Example |
|---------|-----------|---------|
| Repository | `pricing-star` | `github.com/your-org/pricing-star` |
| API base URL | `api.pricingstar.example.com` | (per `docs/PRD_v2/05_API_CONTRACTS.md`) |
| Application URL | `app.pricingstar.example.com` | |
| Storybook | `storybook.pricingstar.example.com` | |
| Database name | `pricing_star_prod` | snake_case |
| Service names | `pricing-star-api`, `pricing-star-engine` | kebab-case |
| TypeScript namespaces | `PricingStar.*` | PascalCase |
| Python package | `pricing_star` | snake_case |

## File naming

| Asset type | Convention | Example |
|-----------|-----------|---------|
| Audit JSON exports | `pricing-star_audit_{asset}_{scenario}_{date}.json` | `pricing-star_audit_VX-CFTR-NG_full-mfn_2026-05-04.json` |
| PDF exports | `pricing-star_report_{title}_{date}.pdf` | |
| Comparison exports | `pricing-star_comparison_{ids}_{date}.xlsx` | |

## Marketing-adjacent surfaces

These are NOT in v2.0 scope but should be reserved/considered:

- **Domain**: `pricingstar.com` (preferred), `pricingstar.io`, `pricingstar.app`
- **Trademark**: To be filed before public launch (legal team)
- **Social handles**: `@pricingstar` (LinkedIn primary, Twitter/X secondary)
- **Pitch deck cover**: Navy bg, gold star, "Pricing Star" wordmark

## Pre-launch checklist

Before going public:

- [ ] Trademark search and filing (US + EU)
- [ ] Domain acquired (`pricingstar.com` minimum)
- [ ] LinkedIn company page reserved
- [ ] Logo finalized (current is concept; final logo from designer)
- [ ] Brand guidelines doc completed (this is a stub)
- [ ] Internal usage in all PRD docs ✅ (done — all references updated)

---

*This file lives at `/branding/PRICING_STAR_BRAND.md` and is referenced by `CLAUDE.md` for naming conventions during the build.*
