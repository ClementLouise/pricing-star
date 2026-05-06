# API Contracts

## Conventions

- **Base URL**: `https://api.pricingstar.example.com/v1`
- **Authentication**: Bearer JWT in `Authorization` header
- **Tenant context**: Derived from JWT claims (`tenant_id`); not in URL
- **Content-Type**: `application/json` for all requests/responses
- **Date format**: ISO 8601 (`2026-05-04T18:42:17Z`)
- **IDs**: UUIDs (v4) as strings
- **Pagination**: cursor-based (`?cursor=...&limit=50`)
- **Errors**: RFC 7807 Problem Details (`application/problem+json`)

## Authentication endpoints

### POST /auth/login

Initiate OIDC/SAML login flow. Returns redirect URL to IDP.

```http
POST /v1/auth/login
Content-Type: application/json

{
  "tenant_slug": "acme-pharma",
  "redirect_uri": "https://app.pricingstar.example.com/callback"
}
```

**Response 200**:
```json
{
  "authorization_url": "https://auth.example.com/authorize?client_id=...&state=..."
}
```

### POST /auth/callback

Exchange OIDC code for tokens.

```http
POST /v1/auth/callback
{
  "code": "abc123",
  "state": "xyz"
}
```

**Response 200**:
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 3600,
  "token_type": "Bearer",
  "user": {
    "id": "uuid",
    "email": "user@acme.com",
    "name": "Sarah Chen",
    "role": "admin",
    "tenant": {
      "id": "uuid",
      "name": "Acme Pharma",
      "slug": "acme-pharma"
    }
  }
}
```

### POST /auth/refresh

Refresh access token using refresh token.

### POST /auth/logout

Invalidate refresh token.

### GET /auth/me

Get current user profile.

## Tenant management (admin only)

### GET /tenants/current

Get current tenant info.

### PATCH /tenants/current

Update tenant settings (name, metadata). Admin only.

### GET /tenants/current/users

List users in current tenant.

### POST /tenants/current/users

Invite new user.

```http
POST /v1/tenants/current/users
{
  "email": "newuser@acme.com",
  "name": "Marcus Reyes",
  "role": "editor"
}
```

**Response 201**: Created user object + invitation sent.

### PATCH /tenants/current/users/{user_id}

Update user (role change, disable).

### DELETE /tenants/current/users/{user_id}

Soft-delete user (set `disabled_at`).

## Asset management

### GET /assets

List assets in current tenant.

**Query params**:
- `archived` (bool, default false): Include archived
- `cursor` (string): Pagination
- `limit` (int, default 50, max 200)

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "VX-CFTR-NG",
      "therapeutic_area": "Cystic fibrosis",
      "modality": "Small molecule",
      "indication": "CF",
      "us_list_price": 370000,
      "us_net_share": 0.50,
      "launch_year": 2027,
      "loe_year": 2042,
      "created_at": "2026-04-15T10:00:00Z",
      "updated_at": "2026-05-01T14:30:00Z"
    }
  ],
  "next_cursor": "..."
}
```

### POST /assets

Create new asset.

```json
{
  "name": "ONC-mAb-001",
  "therapeutic_area": "Oncology",
  "modality": "Monoclonal antibody",
  "indication": "PD-L1 NSCLC 1L",
  "us_list_price": 180000,
  "us_net_share": 0.50,
  "launch_year": 2027,
  "peak_year": 2031,
  "loe_year": 2040,
  "us_patient_population": 12000,
  "ex_us_patient_population": 35000,
  "peak_capture_rate": 0.35,
  "part_b_share": 0.85,
  "discount_rate": 0.10
}
```

**Response 201**: Created asset.

**Validation errors (422)**:
- `us_list_price` must be > 0
- `loe_year > launch_year`
- `peak_year >= launch_year && peak_year < loe_year`

### GET /assets/{asset_id}

Get single asset with full details.

### PATCH /assets/{asset_id}

Update asset. Partial updates supported.

### DELETE /assets/{asset_id}

Soft-delete asset (sets `archived_at`).

### POST /assets/{asset_id}/duplicate

Duplicate an asset (with new name).

```json
{ "new_name": "ONC-mAb-001-aggressive" }
```

## Scenario management

### GET /assets/{asset_id}/scenarios

List scenarios for an asset.

### POST /assets/{asset_id}/scenarios

Create scenario.

```json
{
  "name": "Full MFN 2029",
  "description": "Generous + Guard + Globe all active",
  "is_baseline": false,
  "regulations": {
    "generous": { "active": true, "year": 2027, "medicaid_share": 0.07 },
    "guard": { "active": true, "year": 2028, "submit_method_ii": false },
    "globe": { "active": true, "year": 2029, "submit_method_ii": false }
  },
  "levers": {
    "withdrawals": [],
    "price_floors": {},
    "delayed_launches": {},
    "de_opt_in": false
  },
  "country_data": {
    "DE": { "list_price": 90000, "net_price": 76500, "volume": 0.10, "launched": true, "launch_year": 2027 },
    "FR": { "list_price": 77400, "net_price": 58050, "volume": 0.08, "launched": true, "launch_year": 2027 }
  }
}
```

**Response 201**: Created scenario.

### GET /scenarios/{scenario_id}

Get single scenario with all country_data.

### PATCH /scenarios/{scenario_id}

Update scenario.

### DELETE /scenarios/{scenario_id}

Soft-delete scenario.

### POST /scenarios/{scenario_id}/duplicate

Duplicate scenario.

## Country data management

Country data is nested under scenarios but can be edited individually.

### PATCH /scenarios/{scenario_id}/country-data/{country_code}

Update single country's data.

```json
{
  "list_price": 85000,
  "net_price": 72250,
  "volume": 0.10,
  "launched": true,
  "launch_year": 2027,
  "withdrawn": false,
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

**G2N field semantics**:
- `g2n_ratio` (optional): Static G2N applied to all years if `g2n_time_series` is null or doesn't cover the year
- `g2n_time_series` (optional): Per-year overrides. If provided, takes precedence for years explicitly listed
- Both null: System uses `country_reference.default_g2n_ratio` for all years
- Resolution chain documented in `03_DATA_MODEL.md` "G2N Time Series resolution"
- To clear a time series, send `"g2n_time_series": null` explicitly

### DELETE /scenarios/{scenario_id}/country-data/{country_code}

Reset country to default (treats as not launched).

## Simulation execution

### POST /scenarios/{scenario_id}/simulate

Run a synchronous simulation. Returns full results.

**Request body**: Empty (uses scenario as-stored).

**Response 200**:
```json
{
  "simulation_id": "uuid",
  "engine_version": "1.7.0",
  "computed_at": "2026-05-04T18:42:17Z",
  "computed_in_ms": 187,
  "results": {
    "npv": 4960000000,
    "peak_revenue": 790000000,
    "method_i_value": 56390,
    "method_i_anchor": "CH",
    "method_ii_value": 50423,
    "applicable_benchmark": 56390,
    "per_unit_rebate": 33610,
    "effective_us_net": 56390,
    "cascade_iterations": 3,
    "cascade_converged": true,
    "final_prices": {
      "US": 180000,
      "DE": 90000,
      "FR": 77400
    },
    "yearly_breakdown": [
      {"year": 2027, "us_revenue": 540000000, "ex_us_revenue": 432000000, "total_net": 972000000, "discounted": 972000000},
      {"year": 2028, "us_revenue": 1080000000, "ex_us_revenue": 864000000, "total_net": 1944000000, "discounted": 1767272727}
    ]
  }
}
```

**Errors**:
- 422: Missing required prices in OECD-19 basket
- 422: Cascade did not converge (max iterations reached without convergence)

### POST /scenarios/{scenario_id}/monte-carlo

Run async Monte Carlo simulation.

```json
{
  "n": 500,
  "sigma": 0.05,
  "seed": 42
}
```

**Response 202**:
```json
{
  "job_id": "uuid",
  "status": "queued",
  "polling_url": "/v1/jobs/uuid"
}
```

### GET /scenarios/{scenario_id}/simulations

List historical simulations for this scenario.

```json
{
  "items": [
    {
      "simulation_id": "uuid",
      "computed_at": "2026-05-04T18:42:17Z",
      "engine_version": "1.7.0",
      "npv": 4960000000,
      "method_i_anchor": "CH"
    }
  ]
}
```

### GET /simulations/{simulation_id}

Get full simulation result by ID.

### POST /simulations/{simulation_id}/audit-export

Generate audit JSON for SOX defensibility.

**Response 200** (`Content-Type: application/json`):
```json
{
  "metadata": { ... },
  "asset": { ... },
  "methodology": { ... },
  "pppAdjusters": { ... },
  "inputs": { ... },
  "calculations": { ... },
  "auditTrail": [ ... ],
  "disclaimer": "..."
}
```

Browser triggers download via `Content-Disposition: attachment` header.

## Analysis modules

### POST /scenarios/{scenario_id}/anchor-analysis

Compute MFN Method I anchor analysis.

**Query param**: `model` ∈ {`GUARD`, `GENEROUS`, `GLOBE`} (default `GUARD`)

**Response 200**:
```json
{
  "model": "GUARD",
  "anchor": {
    "country": "CH",
    "country_name": "Switzerland",
    "nominal": 55284,
    "ppp": 1.000,
    "adjusted": 55284
  },
  "second": {
    "country": "NL",
    "nominal": 54354,
    "ppp": 1.065,
    "adjusted": 57887
  },
  "benchmark": 56390,
  "anchor_gap": 2603,
  "anchor_gap_pct": 0.047,
  "is_non_obvious_anchor": true,
  "nominal_lowest": {
    "country": "CZ",
    "nominal": 54000
  },
  "ringfence_recommendation": "CH anchor is fragile — NL is within 5%. Small price changes in either could shift the anchor.",
  "all_ranked": [
    {"country": "CH", "nominal": 55284, "ppp": 1.000, "adjusted": 55284},
    {"country": "NL", "nominal": 54354, "ppp": 1.065, "adjusted": 57887},
    "..."
  ]
}
```

### POST /scenarios/{scenario_id}/de-cascade

Simulate German confidential opt-in cascade.

**Request body**:
```json
{
  "opt_in_rebate_pct": 0.09
}
```

**Response 200**:
```json
{
  "opt_in_rebate_pct": 0.09,
  "de_price_before": 90000,
  "de_price_after": 81900,
  "de_disclosed_delta": -8100,
  "market_impacts": [
    {
      "country": "AT",
      "country_name": "Austria",
      "before": 81000,
      "after": 65610,
      "delta": -15390,
      "delta_pct": -0.190
    }
  ],
  "referencing_markets_count": 27,
  "actually_impacted_count": 8,
  "cascade_iterations": 3
}
```

## Job management (async tasks)

### GET /jobs/{job_id}

Poll job status.

**Response 200**:
```json
{
  "job_id": "uuid",
  "status": "running",
  "progress_pct": 45,
  "started_at": "2026-05-04T18:42:00Z",
  "estimated_completion_at": "2026-05-04T18:42:25Z"
}
```

When complete:
```json
{
  "job_id": "uuid",
  "status": "completed",
  "completed_at": "2026-05-04T18:42:23Z",
  "result": {
    "samples_n": 500,
    "mean": 56390,
    "p05": 53800,
    "p50": 56400,
    "p95": 58900,
    "range": 5100,
    "sigma_input": 0.05
  }
}
```

When failed:
```json
{
  "job_id": "uuid",
  "status": "failed",
  "failed_at": "2026-05-04T18:42:10Z",
  "error": {
    "code": "INSUFFICIENT_DATA",
    "message": "Cannot run Monte Carlo: at least 5 OECD-19 countries must have prices set"
  }
}
```

## Comparison

### POST /scenarios/compare

Compare 2+ scenarios side-by-side.

```json
{
  "scenario_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response 200**:
```json
{
  "scenarios": [
    { "id": "uuid1", "name": "Baseline", "npv": 5850000000 },
    { "id": "uuid2", "name": "Full MFN", "npv": 4960000000 },
    { "id": "uuid3", "name": "Mitigated", "npv": 5400000000 }
  ],
  "deltas": [
    { "from": "uuid1", "to": "uuid2", "delta": -890000000, "delta_pct": -0.152 },
    { "from": "uuid1", "to": "uuid3", "delta": -450000000, "delta_pct": -0.077 }
  ]
}
```

## Reference data (read-only)

### GET /reference/countries

List all countries with reference data.

```json
{
  "items": [
    {
      "country_code": "DE",
      "name": "Germany",
      "region": "Europe",
      "gdp_ppp_adjuster": 1.202,
      "default_g2n_ratio": 0.85,
      "in_oecd_19": true,
      "in_mfn_8": true,
      "irp_rule": {
        "basket": ["UK","FR","IT","ES","NL","BE","AT","DK","SE","FI"],
        "rule": "avg",
        "discount": 0.05
      }
    }
  ]
}
```

### GET /reference/baskets

```json
{
  "GENEROUS": ["UK","FR","DE","IT","CA","JP","DK","CH"],
  "GUARD": ["AU","AT","BE","CA","CZ","DK","FR","DE","IE","IL","IT","JP","NL","NO","KR","ES","SE","CH","UK"],
  "GLOBE": ["AU","AT","BE","CA","CZ","DK","FR","DE","IE","IL","IT","JP","NL","NO","KR","ES","SE","CH","UK"]
}
```

### GET /reference/phase-ins

```json
{
  "GUARD": {"2026": -0.10, "2027": -0.20, "2028": -0.30, "2029": -0.30, "2030": -0.30},
  "GLOBE": {"2026": -0.10, "2027": -0.20, "2028": -0.30, "2029": -0.35, "2030": -0.35}
}
```

## Audit logs

### GET /audit-logs

Query audit logs (admin only).

**Query params**:
- `entity_type`: filter by type
- `entity_id`: filter by specific entity
- `user_id`: filter by user
- `from`: ISO date
- `to`: ISO date

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "user_email": "sarah@acme.com",
      "action": "scenario.simulate",
      "entity_type": "scenario",
      "entity_id": "uuid",
      "payload": { "engine_version": "1.7.0", "npv": 4960000000 },
      "ip_address": "192.0.2.1",
      "created_at": "2026-05-04T18:42:17Z"
    }
  ],
  "next_cursor": "..."
}
```

## Error response format

All errors return RFC 7807 Problem Details:

```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation failed",
  "status": 422,
  "detail": "us_list_price must be greater than 0",
  "instance": "/v1/assets",
  "errors": [
    { "field": "us_list_price", "code": "min_value", "value": -100 }
  ]
}
```

### Error codes

> **Note:** This API follows the WebDAV (RFC 4918) convention adopted by FastAPI/Pydantic for HTTP semantic errors:
> - **400 Bad Request** — malformed request (unparseable JSON, wrong Content-Type, missing required headers)
> - **422 Unprocessable Entity** — well-formed request but semantically invalid data (Pydantic validation: price = 0, year ordering violations, out-of-range values, etc.)

| Code | HTTP | When |
|------|------|------|
| `bad_request` | 400 | Malformed request (parse error, wrong Content-Type) |
| `validation_error` | 422 | Invalid input data (Pydantic constraint violated) |
| `unauthenticated` | 401 | Missing or invalid token |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Entity does not exist (or in different tenant) |
| `conflict` | 409 | Constraint violation (e.g., duplicate name) |
| `unprocessable` | 422 | Valid input but business rule violation |
| `rate_limited` | 429 | Too many requests |
| `engine_error` | 500 | Calculation engine internal error |
| `cascade_did_not_converge` | 422 | Cascade ran out of iterations |
| `insufficient_data` | 422 | Not enough country data to compute |

## Rate limiting

- Default: 1000 requests/hour per user
- Simulation endpoints: 100 simulations/hour per user
- Monte Carlo: 10 jobs/hour per tenant

Headers returned:
- `X-RateLimit-Limit: 1000`
- `X-RateLimit-Remaining: 847`
- `X-RateLimit-Reset: 1715000000`

## API versioning

- Current version: `v1`
- Breaking changes require new version (`v2`)
- Backwards-compatible additions allowed within version
- Deprecation: 6-month notice via `Deprecation` and `Sunset` headers

---

*Next: read `06_UI_COMPONENTS.md`*
