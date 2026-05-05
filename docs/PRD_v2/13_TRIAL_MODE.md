# Trial Mode

## Purpose

Pricing Star supports two operational tiers:

- **Trial mode** (free, self-serve, gated by feature limits + disclaimer): for prospects to evaluate the product without legal/compliance friction
- **Production mode** (paid, contract-gated): for paying customers using real confidential pharma data

This architecture solves the chicken-and-egg problem of pharma SaaS GTM: prospects need to see the product before signing DPA/SOC2 paperwork, but pharma confidentiality requirements typically block any pre-contract data entry.

The design ensures that trial users can experience the full product value with sample data while creating a clean upgrade path to production for serious prospects.

## Design principles

1. **Trial is functionally complete**, not a stripped-down demo. All 9 tabs work. All calculations work. All exports work.
2. **Trial is data-limited**, not feature-limited. Limits are on quantity (max 5 assets, max 3 scenarios per asset, max 30-day account life) — not on capability.
3. **Trial users see the same UI as production**, with one persistent banner at the top.
4. **Trial accounts cannot upgrade in place** to production. Data is wiped on upgrade — clean break by design (forces prospect to re-enter their REAL data after contract, with full intent).
5. **Sample assets are pre-seeded** so prospects experience value immediately (no empty state).

## Tenant tiers

The `tenant.tier` field can be:

| Tier | Description | Access |
|------|-------------|--------|
| `trial` | Self-serve evaluation | 30-day expiry, limited resources, sample data pre-seeded, prominent disclaimer |
| `production` | Paying customer | Full access per contract terms |
| `internal` | Pricing Star team accounts | No limits, used for demos and support |

Default for new self-serve signups: `trial`.

## Trial mode specifications

### Account lifecycle

```
Day 0:    Self-serve signup → trial tenant created with sample data
Day 1-7:  Onboarding emails (tutorial, sample workflows, key features)
Day 21:   Reminder email "Your trial expires in 9 days"
Day 28:   Reminder email "Your trial expires in 2 days — talk to sales?"
Day 30:   Trial expires → tenant set to status='expired'
                          → users can log in but only see read-only mode
                          → banner: "Trial expired. Contact sales to upgrade."
Day 60:   Auto-archive (data preserved 90 days post-expiry per data retention)
Day 120:  Hard delete (per GDPR)
```

### Resource limits

| Resource | Trial limit | Production default | Notes |
|----------|-------------|--------------------|-----|
| Account duration | 30 days | Until cancellation | Trial auto-expires |
| Users per tenant | 3 | 50 | Trial limited to small evaluation team |
| Assets | 5 | 100 | Includes pre-seeded samples |
| Scenarios per asset | 3 | 50 | |
| Simulations per month | 100 | 10,000 | |
| Monte Carlo jobs per month | 5 | 100 | |
| Audit JSON exports per month | 10 | 1,000 | |
| API access | ❌ Disabled | ✅ Enabled | Trial = UI only |
| SSO/SAML | ❌ Disabled | ✅ Enabled | Trial = email/password only |

### Pre-seeded sample assets

When a trial tenant is created, the system automatically creates two sample assets matching the test fixtures:

#### Sample 1: "VX-CFTR-NG (Sample — Orphan Premium)"

- Pre-loaded with all data from `docs/reference/test_results_v11.json`
- Pre-built scenarios: "Pre-MFN Baseline", "Generous + Guard", "Full MFN G+G+G"
- Pre-built mitigations: empty (user can experiment)
- Documented as `SAMPLE` in asset metadata (read-only on most fields, editable on others for exploration)

#### Sample 2: "ONC-mAb-001 (Sample — Oncology Biologic)"

- Pre-loaded with all data from `docs/reference/test_v20_results.json`
- Pre-built scenarios: same as above
- Demonstrates the asymmetry: this one shows -$894M MFN impact

These samples are **immutable on critical fields** (asset name, US list price, fixture-defining fields) but **editable on exploration fields** (lever toggles, scenario duplication, comparisons). When users edit a sample asset, an "edited" flag appears.

### Trial UI elements

#### `<TrialBanner />` component

Persistent banner at top of every page for trial tenants:

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚠ TRIAL MODE — Use only illustrative or public data.           │
│ Your trial expires on May 28, 2026 (24 days remaining).         │
│ Talk to sales →  |  Upgrade to production →                     │
└─────────────────────────────────────────────────────────────────┘
```

Visual specs:
- Background: amber `#FFF8E1`
- Border-left: gold `#B8860B`, 4px
- Always visible (sticky), never dismissable
- "Talk to sales" link opens a modal with calendar booking
- "Upgrade to production" link opens upgrade flow (see below)

#### Sample asset markers

Each sample asset shows a `Pill` badge:

```
🌟 SAMPLE  VX-CFTR-NG (Sample — Orphan Premium)
```

#### Limit warnings

When approaching limits, show non-blocking notices:

- 4 of 5 assets used → notice "Approaching trial asset limit (1 remaining)"
- 5 of 5 assets used → block creation with modal "Trial asset limit reached. Talk to sales to upgrade."

#### Upgrade CTAs

Strategically placed but not aggressive:

- Top banner (always visible): "Talk to sales"
- Limit reached modals: "Upgrade to production"
- Audit JSON export: "Production accounts can export to S3/SharePoint automatically"
- After successful simulation: "Save scenarios across teams in production"

### Disclaimer & ToS

#### Signup flow disclaimer

On the signup form:

```
By signing up, I acknowledge that:
[ ] I will only enter illustrative, hypothetical, or publicly available data during trial.
[ ] I will not enter confidential pharma data, real pricing, or commercially sensitive information.
[ ] I understand the trial expires after 30 days and data may be deleted.
[ ] I have read the Terms of Service and Privacy Policy.
[Continue]
```

All checkboxes mandatory. Recorded in `audit_log` with timestamp.

#### Inline reminders

When user enters numeric data resembling real prices (heuristic: list price > $100K with patterns matching known drug pricing), show a **soft notice**:

```
ℹ Reminder: This looks like real product pricing data.
  Trial mode is for illustrative use only.
  [I'm using illustrative data]  [Tell me about production]
```

Heuristic is intentionally non-blocking — false positives would frustrate users entering legitimate sample data.

### Restricted features in trial

The following features are disabled in trial:

- ❌ **API access**: All `/v1/api-keys` endpoints return 403 with "Upgrade to production for API access"
- ❌ **SSO/SAML**: Login is email + password (with TOTP option) only
- ❌ **User invites beyond 3**: Modal "Trial limited to 3 users. Upgrade for team access"
- ❌ **Custom IRP rule editor** (when shipped in v3.0): Production-only
- ❌ **Bulk CSV import**: Production-only (limit value of trial)
- ❌ **Audit log export beyond own actions**: Trial users see only their own audit trail; admin viewing all-tenant audit is production-only

Why these restrictions: They preserve commercial value (prospect must want production for these), without crippling the core product evaluation.

### Trial → Production upgrade flow

The upgrade is **NOT in-place**. It's a contract-then-rebuild process:

1. **Trial user clicks "Upgrade to production"**
2. **Sales workflow triggers**:
   - Calendar booking with sales
   - Discovery call to understand needs
   - Contract negotiation (DPA, MSA, pricing)
3. **Contract signed** (out of band)
4. **Operations team** creates production tenant with same admin email
5. **Admin gets magic link** to set up production tenant
6. **Trial tenant data is NOT migrated** automatically. Admin can:
   - **Option A**: Start fresh in production (recommended — prospect re-enters real data with intent)
   - **Option B**: Manually export trial scenarios to JSON and re-import in production (advanced)
7. **Trial tenant** continues to exist (read-only) for 30 days post-upgrade, then archived
8. **Audit log entry**: `tenant.upgraded_to_production` with both tenant IDs for traceability

### Self-serve trial signup flow

```
1. User visits app.pricingstar.example.com/signup
2. Enter email + name + company
3. Verify email (link sent)
4. Set password (12+ chars, complexity per password policy)
5. Accept disclaimer + ToS (3 mandatory checkboxes)
6. Optional MFA setup (TOTP — recommended, can skip)
7. Tenant + admin user created (tenant.tier='trial', expires_at=now+30days)
8. Sample assets seeded (background job, ~5 seconds)
9. User redirected to /dashboard with welcome modal:
   "Welcome to Pricing Star! Two sample assets have been pre-loaded.
    Try the 'Optimizer' tab to see MFN impact analysis on VX-CFTR-NG."
   [Show me the samples]  [Take the product tour]
```

## Data model implications

See `03_DATA_MODEL.md` for full schemas. Key fields added:

```sql
-- Tenant table
ALTER TABLE tenant ADD COLUMN tier varchar(20) NOT NULL DEFAULT 'trial';
ALTER TABLE tenant ADD COLUMN trial_expires_at timestamptz;  -- NULL for production
ALTER TABLE tenant ADD CONSTRAINT tier_check CHECK (tier IN ('trial', 'production', 'internal'));

-- Asset table
ALTER TABLE asset ADD COLUMN is_sample boolean NOT NULL DEFAULT false;
ALTER TABLE asset ADD COLUMN sample_origin varchar(50);  -- e.g., 'VX-CFTR-NG' or 'ONC-mAb-001'

-- Audit log
-- Action types added: 'trial.disclaimer_accepted', 'trial.limit_reached', 'trial.expired', 'tenant.upgraded_to_production'
```

## Build phase implications

See `11_BUILD_ORDER.md` for phasing. Key changes:

- **Phase 0**: Tier scaffolding (tenant.tier, sample asset seeding service stub)
- **Phase 1**: Sample asset data loaded as fixtures (ties directly to test_results_v11.json)
- **Phase 2**: Trial limits enforced at API layer
- **Phase 3**: `<TrialBanner />` component, sample asset markers, signup flow with disclaimer
- **Phase 6**: Email automation (trial expiry warnings, onboarding sequence)

## Performance considerations

- Sample asset seeding must complete in < 10 seconds (background job, async)
- Trial limit checks add < 5ms to mutation requests (cached tenant.tier in JWT claim)
- Trial banner renders without API call (data in JWT)

## Security considerations

- Trial accounts cannot access production tenants' data (standard tenant isolation)
- Production accounts cannot accidentally drop into trial mode (tier change requires admin + audit)
- Sample assets are tenant-isolated despite being identical content (separate rows per trial tenant — small storage cost, large isolation guarantee)
- API keys cannot be created in trial (prevents trial account from being used as API gateway)

## Customer-facing FAQ

These questions need to be answered on the marketing site / signup flow:

**Q: Can I use my real pharma data in trial?**
A: No. Trial mode is for illustrative or public data only. Trial accounts include two sample assets that demonstrate the platform's full capabilities. For real data, please contact sales for production access.

**Q: What happens to my trial data when I upgrade?**
A: Trial data is not automatically migrated to production. This is by design — production data should be entered with full intent and under contract. You can manually export trial scenarios as JSON and re-import them in production if needed.

**Q: How long is the trial?**
A: 30 days from signup. We send reminders at days 21, 28, and 30.

**Q: Can I extend my trial?**
A: Contact sales — extensions are case-by-case for serious prospects.

**Q: What happens after 30 days?**
A: Your account becomes read-only for 30 more days, then archived. Data is preserved 90 days total before deletion.

**Q: Is my trial data isolated from other trials?**
A: Yes. Every tenant (trial or production) has full data isolation — no other tenant can see your data, ever.

## Acceptance criteria for v2.0

The trial mode is considered complete when:

- [ ] Self-serve signup flow functional (email verification, MFA optional, disclaimer)
- [ ] New trial tenants get sample assets pre-seeded within 10 seconds
- [ ] `<TrialBanner />` displays on every page for trial tenants
- [ ] Trial limits enforced at API layer (asset count, scenario count, user count)
- [ ] Trial expiry email sequence (days 21, 28, 30, 60)
- [ ] Trial → expired transition disables mutations, allows reads
- [ ] Trial → production upgrade workflow documented in admin runbook
- [ ] Inline price-detection heuristic shows reminder (false positives < 5%)
- [ ] Audit log entries for trial events
- [ ] Sample asset markers visible in UI

## Out of scope for v2.0

- Self-serve **production upgrade** (must go through sales — by design)
- Stripe/payment integration (sales-led, manual invoicing in v2.0)
- Custom trial duration per signup (always 30 days in v2.0)
- Trial-to-trial migration (1 trial per email)
- Reseller/partner trial accounts (deferred to v3.0)

---

*Next: read `12_EDGE_CASES.md`*
