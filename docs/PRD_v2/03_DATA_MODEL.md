# Data Model

## Entity overview

```
Tenant ──┬──< User
         │
         ├──< Asset ──< Scenario ──< SimulationResult
         │                  │
         │                  └──< AuditLog
         │
         └──< ApiKey
```

Cross-tenant constraint: **every domain entity has `tenant_id` and queries must filter by it**.

## Entity definitions

### Tenant

Represents a customer organization (mid-cap pharma company).

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | Generated v4 |
| `name` | varchar(255) | NOT NULL | Display name |
| `slug` | varchar(64) | NOT NULL, UNIQUE | URL-safe; e.g., "vertex" |
| `tier` | enum | NOT NULL, DEFAULT 'trial' | `trial`, `production`, `internal`. See `13_TRIAL_MODE.md` |
| `subscription_status` | enum | NOT NULL | `active`, `suspended`, `cancelled`, `expired` |
| `trial_expires_at` | timestamptz | NULL | Required if tier='trial', null otherwise |
| `seat_limit` | int | DEFAULT 50 | Max users per tenant. Trial: 3, production: per contract |
| `resource_limits` | jsonb | DEFAULT '{}' | Override defaults from `13_TRIAL_MODE.md` resource limits table |
| `created_at` | timestamptz | NOT NULL | |
| `created_by` | UUID | NULL | User ID of creator (if self-serve) |
| `metadata` | jsonb | DEFAULT '{}' | Custom fields per tenant |

Indexes: `slug`, `created_at`

### User

Authenticated user belonging to a tenant.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | |
| `tenant_id` | UUID | FK → Tenant, NOT NULL | |
| `email` | citext | NOT NULL | Unique within tenant |
| `name` | varchar(255) | NOT NULL | |
| `role` | enum | NOT NULL | `admin`, `editor`, `viewer` |
| `auth_provider_id` | varchar(255) | NULL | External IDP user ID (Auth0, Cognito) |
| `last_login_at` | timestamptz | NULL | |
| `created_at` | timestamptz | NOT NULL | |
| `disabled_at` | timestamptz | NULL | Soft-delete |

Indexes: `tenant_id, email` (unique), `auth_provider_id`

### Asset

A pharmaceutical asset being modeled (e.g., "ONC-mAb-001").

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | |
| `tenant_id` | UUID | FK → Tenant, NOT NULL | |
| `name` | varchar(255) | NOT NULL | E.g., "VX-CFTR-NG" |
| `therapeutic_area` | varchar(100) | NULL | E.g., "Oncology" |
| `modality` | varchar(100) | NULL | E.g., "Monoclonal antibody" |
| `indication` | varchar(255) | NULL | E.g., "NSCLC 1L" |
| `us_list_price` | decimal(12,2) | NULL | USD/year/patient |
| `us_net_share` | decimal(5,4) | NULL | 0-1 (e.g., 0.50) |
| `launch_year` | int | NULL | E.g., 2027 |
| `peak_year` | int | NULL | |
| `loe_year` | int | NULL | Loss of exclusivity |
| `cogs_percent` | decimal(5,4) | DEFAULT 0.15 | |
| `discount_rate` | decimal(5,4) | DEFAULT 0.10 | WACC |
| `us_patient_population` | int | NULL | |
| `ex_us_patient_population` | int | NULL | |
| `peak_capture_rate` | decimal(5,4) | DEFAULT 0.5 | |
| `part_b_share` | decimal(5,4) | DEFAULT 0.5 | For Globe vs Guard weighting |
| `created_at` | timestamptz | NOT NULL | |
| `updated_at` | timestamptz | NOT NULL | |
| `created_by` | UUID | FK → User | |
| `archived_at` | timestamptz | NULL | Soft-delete |
| `is_sample` | boolean | NOT NULL, DEFAULT false | True if pre-seeded sample (trial mode). See `13_TRIAL_MODE.md` |
| `sample_origin` | varchar(50) | NULL | If sample: source identifier (e.g., 'VX-CFTR-NG', 'ONC-mAb-001') |
| `sample_edited` | boolean | NOT NULL, DEFAULT false | True if user has modified an editable field on a sample |

Indexes: `tenant_id, archived_at`, `tenant_id, name`, `tenant_id, is_sample`

### CountryData

Per-country pricing/volume data attached to an asset (or a scenario, depending on whether we model these as templates or per-scenario).

**Decision**: CountryData is a child of Scenario, NOT Asset. Rationale: scenarios may diverge in country pricing (e.g., "what if we don't launch in Germany?"). Asset has reference defaults; Scenario has overrides.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | |
| `tenant_id` | UUID | FK → Tenant, NOT NULL | (denormalized for tenant filtering) |
| `scenario_id` | UUID | FK → Scenario, NOT NULL | |
| `country_code` | char(2) | NOT NULL | ISO 3166-1 alpha-2; e.g., "DE" |
| `list_price` | decimal(12,2) | NULL | USD |
| `net_price` | decimal(12,2) | NULL | USD (after confidential rebates) |
| `volume` | decimal(8,4) | NULL | Share of total ex-US volume (0-1) |
| `launched` | boolean | DEFAULT false | |
| `launch_year` | int | NULL | |
| `withdrawn` | boolean | DEFAULT false | |
| `g2n_ratio` | decimal(5,4) | NULL | Default static G2N. If null, use country default from `CountryReference`. Used as fallback when `g2n_time_series` is null. |
| `g2n_time_series` | jsonb | NULL | Year-by-year G2N override. Schema: `{"2027": 0.85, "2028": 0.83, ...}`. If set, overrides `g2n_ratio` for years present. See "G2N Time Series resolution" below. |

Indexes: `scenario_id, country_code` (unique within scenario)

#### G2N Time Series resolution

The G2N value used in NPV computation for `(country, year)` is resolved via this fallback chain:

```
1. country_data.g2n_time_series[year]                    if present (per-year explicit override)
2. country_data.g2n_ratio                                 if not null (per-country static override)
3. country_reference.default_g2n_ratio                    fallback (country-level default)
```

**Validation rules**:
- `g2n_time_series` keys must be string years between asset's `launch_year` and `loe_year + 5`
- Each value must be in (0.0, 1.0]
- `g2n_time_series` may be sparse (only some years present); missing years fall back to step 2 then step 3
- If `g2n_time_series` has only 1 entry, the system replicates this value across all years (backward-compatible with static G2N)

**Example**:

```json
{
  "country_code": "DE",
  "g2n_ratio": 0.85,
  "g2n_time_series": {
    "2027": 0.85,
    "2028": 0.83,
    "2029": 0.80,
    "2030": 0.75,
    "2031": 0.72,
    "2032": 0.70
  }
}
```

For year 2027-2032: uses time series values (gradual AMNOG erosion).
For year 2026 (pre-launch) or 2033+ (beyond series): uses `g2n_ratio` = 0.85.

**Storage size**: typical scenario has 43 countries × 15 years = 645 floats max. Stored as compact jsonb (~5 KB per scenario). Negligible.

### Scenario

A regulatory + strategic configuration applied to an asset.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | |
| `tenant_id` | UUID | FK → Tenant, NOT NULL | |
| `asset_id` | UUID | FK → Asset, NOT NULL | |
| `name` | varchar(255) | NOT NULL | E.g., "Baseline 2027", "Aggressive ex-US" |
| `description` | text | NULL | |
| `is_baseline` | boolean | DEFAULT false | One per asset can be baseline |
| `regulations` | jsonb | NOT NULL | See "Scenario.regulations schema" below |
| `levers` | jsonb | DEFAULT '{}' | Withdrawals, price floors |
| `cascade_config` | jsonb | DEFAULT '{}' | Cascade options (enabled, max_iter) |
| `created_at` | timestamptz | NOT NULL | |
| `updated_at` | timestamptz | NOT NULL | |
| `created_by` | UUID | FK → User | |
| `archived_at` | timestamptz | NULL | |

Indexes: `tenant_id, asset_id, archived_at`

#### Scenario.regulations schema (jsonb)

```json
{
  "generous": {
    "active": true,
    "year": 2027,
    "medicaid_share": 0.07
  },
  "guard": {
    "active": true,
    "year": 2028,
    "submit_method_ii": false,
    "phase_in": -0.30
  },
  "globe": {
    "active": true,
    "year": 2029,
    "submit_method_ii": false,
    "phase_in": -0.35
  }
}
```

#### Scenario.levers schema (jsonb)

```json
{
  "withdrawals": ["GR", "BG"],
  "price_floors": {
    "DE": 0.60,
    "CH": 0.65
  },
  "delayed_launches": {
    "BR": 2029
  },
  "de_opt_in": false
}
```

### SimulationResult

Output of running a scenario through the calculation engine.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | |
| `tenant_id` | UUID | FK → Tenant, NOT NULL | |
| `scenario_id` | UUID | FK → Scenario, NOT NULL | |
| `engine_version` | varchar(20) | NOT NULL | E.g., "1.7.0" |
| `npv` | decimal(15,2) | NOT NULL | 14-Y or 15-Y NPV in USD |
| `peak_revenue` | decimal(15,2) | NULL | |
| `method_i_value` | decimal(12,2) | NULL | |
| `method_i_anchor` | char(2) | NULL | Country code |
| `method_ii_value` | decimal(12,2) | NULL | |
| `applicable_benchmark` | decimal(12,2) | NULL | |
| `per_unit_rebate` | decimal(12,2) | NULL | |
| `effective_us_net` | decimal(12,2) | NULL | |
| `cascade_iterations` | int | NULL | |
| `cascade_converged` | boolean | NULL | |
| `final_prices` | jsonb | NOT NULL | Full price set after cascade |
| `yearly_breakdown` | jsonb | NOT NULL | Year-by-year revenue array |
| `computed_at` | timestamptz | NOT NULL | |
| `computed_by` | UUID | FK → User | |
| `monte_carlo_result` | jsonb | NULL | If Monte Carlo was run |

Indexes: `tenant_id, scenario_id, computed_at DESC`

#### SimulationResult.final_prices schema (jsonb)

```json
{
  "US": 180000,
  "DE": 90000,
  "FR": 77400,
  ...43 countries...
}
```

#### SimulationResult.yearly_breakdown schema (jsonb)

```json
[
  {"year": 2027, "us_revenue": 1080000000, "ex_us_revenue": 850000000, "total_net": 1930000000, "discounted": 1930000000},
  {"year": 2028, "us_revenue": 1296000000, ...},
  ...
]
```

### AuditLog

Immutable append-only log of all significant actions.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | |
| `tenant_id` | UUID | FK → Tenant, NOT NULL | |
| `user_id` | UUID | FK → User, NULL | NULL if system action |
| `action` | varchar(64) | NOT NULL | E.g., "scenario.run", "asset.update" |
| `entity_type` | varchar(64) | NOT NULL | E.g., "scenario", "asset" |
| `entity_id` | UUID | NULL | ID of affected entity |
| `payload` | jsonb | NOT NULL | Action-specific data |
| `ip_address` | inet | NULL | |
| `user_agent` | text | NULL | |
| `created_at` | timestamptz | NOT NULL | |

Indexes: `tenant_id, created_at DESC`, `tenant_id, entity_type, entity_id, created_at DESC`

**Constraint**: AuditLog records are append-only. No UPDATE or DELETE operations allowed at the application layer. Database-level: REVOKE UPDATE, DELETE on audit_log FROM app_user.

### ApiKey (for service accounts)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | |
| `tenant_id` | UUID | FK → Tenant, NOT NULL | |
| `name` | varchar(255) | NOT NULL | |
| `key_hash` | varchar(255) | NOT NULL, UNIQUE | bcrypt-hashed |
| `key_prefix` | varchar(16) | NOT NULL | First 8 chars for identification |
| `permissions` | jsonb | NOT NULL | Scoped permissions |
| `last_used_at` | timestamptz | NULL | |
| `expires_at` | timestamptz | NULL | |
| `created_at` | timestamptz | NOT NULL | |
| `revoked_at` | timestamptz | NULL | |

Indexes: `key_hash`, `tenant_id`

## Reference data (read-only, shared across tenants)

These are global constants from CMS rules. Loaded at startup, refreshed periodically.

### CountryReference

```sql
CREATE TABLE country_reference (
  country_code char(2) PRIMARY KEY,
  name varchar(255) NOT NULL,
  region varchar(64) NOT NULL,
  gdp_ppp_adjuster decimal(7,4) NOT NULL,  -- e.g., 1.573 for CZ
  default_g2n_ratio decimal(5,4) NOT NULL, -- e.g., 0.85 for DE
  in_oecd_19 boolean NOT NULL,
  in_mfn_8 boolean NOT NULL,
  irp_rule jsonb,                          -- IRP basket and discount
  updated_at timestamptz NOT NULL
);
```

The PPP adjusters and IRP rules are versioned (separate `country_reference_history` table) so we can re-run historical analyses with the rules-as-of-then.

### USModelBasket

```sql
CREATE TABLE us_model_basket (
  model varchar(20) PRIMARY KEY,        -- 'GENEROUS', 'GUARD', 'GLOBE'
  basket_countries jsonb NOT NULL,      -- e.g., ["UK", "FR", ...]
  active_from date NOT NULL,
  active_until date,
  source_citation text NOT NULL         -- E.g., "CMS Federal Register § 514.220(d)"
);
```

## Multi-tenancy enforcement

### Database level

Approach: **Row-level security (RLS) is OPTIONAL but app-level filtering is MANDATORY**.

Rationale: RLS is harder to debug; mid-cap scale (10-50 tenants in v2.0) doesn't require it. App-level filtering with mandatory `WHERE tenant_id = :current_tenant` on every query is sufficient if enforced consistently.

If team prefers RLS, enable it with policies like:

```sql
ALTER TABLE asset ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON asset USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

### Application level (mandatory)

Every repository method must accept `tenant_id` as a parameter and use it in queries:

```python
# GOOD
def get_asset(asset_id: UUID, tenant_id: UUID) -> Asset:
    return db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.tenant_id == tenant_id,  # ALWAYS
        Asset.archived_at.is_(None)
    ).one_or_none()

# BAD - DO NOT DO THIS
def get_asset(asset_id: UUID) -> Asset:
    return db.query(Asset).filter(Asset.id == asset_id).one()
```

## Soft-delete pattern

Soft-deleted entities have `archived_at` (or equivalent: `disabled_at`, `cancelled_at`, `revoked_at`) set to a timestamp. Hard delete is forbidden except via:

1. GDPR data subject erasure request (separate workflow with legal sign-off)
2. Tenant cancellation + retention period expiry (90 days post-cancellation)

Repository methods filter out archived rows by default. An explicit `include_archived=True` flag is needed to retrieve them.

## Migration strategy

- All schema changes via Alembic migrations (Python) or equivalent
- Migrations are idempotent and reversible
- Production migrations run BEFORE deploy of new code (zero-downtime requires backwards-compatible migrations)
- No `DROP COLUMN` migrations without 2-version deprecation cycle
- All new tables include `tenant_id` (no exceptions for domain entities)

## Data retention

| Entity | Retention | Rationale |
|--------|-----------|-----------|
| AuditLog | 7 years | SOX 404 requirement |
| SimulationResult | 5 years | Regulatory defense window |
| Scenario | Indefinite (until tenant cancels) | Customer data |
| Asset | Indefinite | Customer data |
| User | 90 days post-account-deletion | Compliance |
| ApiKey | Indefinite (revoked records kept) | Audit trail |

---

*Next: read `04_CALC_ENGINE_SPEC.md`*
