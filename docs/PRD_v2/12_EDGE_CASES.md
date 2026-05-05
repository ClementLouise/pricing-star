# Edge Cases Catalog

## Purpose

A defensive catalog of edge cases the system must handle correctly. Each case includes the trigger, expected behavior, and severity. Edge cases are categorized:

- **P0**: System breaks or produces wrong output. Must be fixed before launch.
- **P1**: Degraded experience but recoverable. Fix before GA.
- **P2**: Rare or low-impact. Document and fix opportunistically.

## Calculation engine edge cases

### EC-CALC-01: Cascade does not converge in max iterations

**Trigger**: Circular IRP rules or extreme price disparities cause cascade to oscillate.

**Severity**: P0

**Expected behavior**:
- Engine returns `{converged: false, iterations: max_iterations, history: [...]}`
- API endpoint returns 422 with code `cascade_did_not_converge`
- UI shows warning banner "Cascade did not stabilize. Suggest increasing max iterations or reviewing input data."
- Audit log entry created with full inputs for investigation

### EC-CALC-02: Method I has no valid countries

**Trigger**: All OECD-19 countries have null or zero prices (no launches in basket).

**Severity**: P0

**Expected behavior**:
- `calculate_guard_method_i()` returns None
- Downstream `calculate_guard_rebate()` returns `{rebate_per_unit: 0, benchmark: None}`
- UI shows "Insufficient data — launch at least one OECD-19 country"

### EC-CALC-03: Generous needs 2+ countries, only 1 launched

**Trigger**: Only one MFN-8 country launched.

**Severity**: P1

**Expected behavior**:
- `calculate_generous_price()` returns None (cannot compute 2nd-lowest)
- UI shows warning "Generous reference requires at least 2 launched MFN-8 countries"

### EC-CALC-04: Method II with all volumes zero

**Trigger**: Volumes not yet entered for any OECD-19 country.

**Severity**: P1

**Expected behavior**:
- `calculate_guard_method_ii()` returns None
- UI shows "Set volumes for at least one OECD-19 country to compute Method II"

### EC-CALC-05: NPV with launch_year > peak_year > LOE

**Trigger**: User inputs invalid year sequence.

**Severity**: P0 (input validation)

**Expected behavior**:
- API returns 400 validation error before reaching engine
- UI form validates: `launch_year <= peak_year < loe_year`
- Error message: "Peak year must be after launch year and before LOE"

### EC-CALC-06: Negative or zero prices

**Trigger**: User enters list price = -100 or 0.

**Severity**: P0

**Expected behavior**:
- API validation rejects with `validation_error`
- Form shows inline error "Price must be greater than 0"

### EC-CALC-07: Volume > 1.0 (more than 100% market share)

**Trigger**: User enters volume = 1.5 (interpreted as % share).

**Severity**: P1

**Expected behavior**:
- Form validates: 0 < volume <= 1
- Error: "Volume share must be between 0 and 100%"

### EC-CALC-08: PPP adjuster < 1.0 from data update

**Trigger**: CMS publishes adjuster data where Country GDP > US GDP (PPP).

**Severity**: P0 (per CMS rule)

**Expected behavior**:
- Reference data loader enforces lower bound 1.000
- Logs warning if any adjuster computed as < 1.0 in input
- Stores 1.000 in `country_reference.gdp_ppp_adjuster`

### EC-CALC-09: Asset launch year before current year

**Trigger**: User models historical asset (launch_year=2020).

**Severity**: P2

**Expected behavior**:
- Allow (useful for back-testing)
- Phase-in lookups use minimum year 2026
- NPV computed as if asset launched today (no historical revenue tracked)

### EC-CALC-10: Massive price (e.g., $10M/year for ultra-orphan)

**Trigger**: Pricing for Zolgensma-like ultra-orphan ($2.1M list).

**Severity**: P2

**Expected behavior**:
- All calculations work (no overflow with `decimal(15,2)`)
- UI handles large numbers gracefully (`$10M` not `$10,000,000` for display)
- Method I anchor still computes; PPP adjustment still applies

### EC-CALC-11: Discount rate = 0 or negative

**Trigger**: User enters WACC = 0% (undiscounted NPV) or WACC = -5%.

**Severity**: P1

**Expected behavior**:
- 0%: allowed, NPV = sum of yearly revenues
- Negative: blocked at validation (warn "Negative discount rate is unusual; consider 5-15%")

### EC-CALC-12: G2N time series with sparse years

**Trigger**: User defines `g2n_time_series = {"2027": 0.85, "2030": 0.75}` (skipping 2028, 2029).

**Severity**: P1

**Expected behavior**:
- Years 2027 and 2030: use explicit values
- Years 2028, 2029: fall back to `g2n_ratio` (static), then to `country_reference.default_g2n_ratio`
- Audit JSON documents the resolution chain used per (country, year)
- UI shows a notice: "Sparse time series — years 2028, 2029 use static fallback"

### EC-CALC-13: G2N time series year outside asset lifecycle

**Trigger**: User defines `g2n_time_series = {"2025": 0.85}` for asset with launch_year=2027.

**Severity**: P0 (input validation)

**Expected behavior**:
- API validation rejects with `validation_error`
- Form shows: "Year 2025 is before asset launch year 2027"
- Validation accepts years from `launch_year` to `loe_year + 5`

### EC-CALC-14: G2N time series with non-monotonic values

**Trigger**: User defines `{"2027": 0.85, "2028": 0.75, "2029": 0.90, "2030": 0.70}` (G2N goes up then down).

**Severity**: P2

**Expected behavior**:
- Allow (could model contract renegotiation cycles, volume tier changes)
- UI shows informational notice: "G2N is non-monotonic in years 2028-2029. Verify intentional."
- No blocking; this is a legitimate pattern in some contracts

### EC-CALC-15: Asset launch year changes after G2N time series defined

**Trigger**: User has `g2n_time_series = {"2027": 0.85, "2028": 0.83, ...}`. Then changes asset launch_year from 2027 to 2028.

**Severity**: P1

**Expected behavior**:
- On launch_year change, system detects time series misalignment
- Modal: "Launch year changed. Time series for DE starts at 2027. Choose: (a) Shift series forward by 1 year, (b) Drop pre-launch entries (2027), (c) Cancel launch year change"
- Default action: option (b) drop pre-launch entries
- Audit log entry records the resolution

### EC-CALC-16: G2N time series persisted but launched=false

**Trigger**: User defines time series for DE, then unchecks `launched` for DE.

**Severity**: P2

**Expected behavior**:
- Time series data preserved in DB (not auto-deleted)
- Calc engine ignores the country (launched=false → no contribution to NPV/Method II)
- If user re-launches DE later, time series re-applies
- UI shows "Time series saved (currently inactive — country not launched)"

### EC-CALC-17: Method II benchmark trajectory crosses rebate threshold mid-lifecycle

**Trigger**: Time-variant G2N causes Method II to drop below US net price in year Y but not year Y-1.

**Severity**: P1

**Expected behavior**:
- Per-year rebate calculated independently
- Years before Y: rebate_per_unit = 0
- Year Y onwards: rebate_per_unit = US_net - Method_II(Y)
- NPV correctly aggregates yearly rebates (not a single benchmark)
- UI in Tab 4 highlights the "rebate trigger year" prominently

## Multi-tenancy edge cases

### EC-TENANT-01: User accesses entity from another tenant via URL guess

**Trigger**: User A guesses URL `/assets/{uuid_of_tenant_B_asset}`.

**Severity**: P0 (security)

**Expected behavior**:
- API returns 404 NOT FOUND (not 403 — never confirm existence of cross-tenant resources)
- No data leaked
- Security event logged
- Tested by automated cross-tenant access tests in CI

### EC-TENANT-02: User's tenant suspended mid-session

**Trigger**: Admin suspends tenant; user already has active session.

**Severity**: P1

**Expected behavior**:
- Existing JWT remains valid until expiry (max 1h)
- Refresh token rejected → forced re-login → blocked at login
- UI shows "Your account has been suspended. Contact your admin."

### EC-TENANT-03: User role changed mid-session

**Trigger**: User had `editor`, admin demotes to `viewer` while user is editing.

**Severity**: P1

**Expected behavior**:
- API checks current role on every mutation
- Mid-edit save fails with 403 Forbidden
- UI shows toast "Your role has changed. Please reload."

### EC-TENANT-04: Tenant cancels with active scenarios

**Trigger**: Customer cancels subscription; scenarios exist.

**Severity**: P1

**Expected behavior**:
- Tenant set to `cancelled` status
- 90-day grace period: data accessible read-only
- After 90 days: data archived (encrypted backup) + soft-deleted
- After retention period: hard-deleted per GDPR

## UI edge cases

### EC-UI-01: User unsaved changes when navigating

**Trigger**: User edits asset, doesn't save, clicks another tab or browser back.

**Severity**: P1

**Expected behavior**:
- Modal: "You have unsaved changes. Discard or save?"
- Three buttons: Save & continue, Discard, Cancel
- `beforeunload` event for browser back/close

### EC-UI-02: Two users edit same scenario simultaneously

**Trigger**: Race condition.

**Severity**: P1

**Expected behavior**:
- Optimistic concurrency: each save includes `updated_at` from last fetch
- Server rejects if `updated_at` doesn't match current value (409 Conflict)
- UI shows "Another user updated this scenario. Reload to see changes." with diff option

### EC-UI-03: User opens app in two tabs

**Trigger**: Same user, two browser tabs.

**Severity**: P2

**Expected behavior**:
- Both tabs work independently
- Mutation in tab A → tab B doesn't auto-refresh (acceptable)
- Avoid websocket complexity in v2.0; revisit for v3.0

### EC-UI-04: Browser back button after deep navigation

**Trigger**: User navigates assets > scenarios > simulate > optimizer, then clicks back many times.

**Severity**: P1

**Expected behavior**:
- React Router history works
- Each tab change is a route change (deep linkable)
- Back navigation restores previous state

### EC-UI-05: User pastes 1000+ rows of CSV data

**Trigger**: Bulk import with massive CSV.

**Severity**: P1

**Expected behavior**:
- Parse client-side (no server upload until validated)
- Show progress for parsing
- Limit: 10,000 rows max (43 countries × ~250 scenarios is unusual)
- If exceeded: error "CSV too large; please split into smaller files"

### EC-UI-06: Slow network during simulation

**Trigger**: 5G drops to 3G mid-simulation.

**Severity**: P2

**Expected behavior**:
- Loading indicator visible
- Timeout after 30s for sync simulations → suggest async via Monte Carlo flow
- TanStack Query auto-retries with exponential backoff

### EC-UI-07: User's screen resolution < 1280px

**Trigger**: Smaller laptop or zoomed-in browser.

**Severity**: P2

**Expected behavior**:
- Layout reflows; tabs may scroll horizontally
- Below 1024px: show banner "Best viewed at 1280px+. Some features may be cramped."

## Data edge cases

### EC-DATA-01: Country list expands (CMS adds 20th OECD country)

**Trigger**: CMS final rule adds Iceland to OECD-19.

**Severity**: P1

**Expected behavior**:
- Reference data tables updated (one config change, no code change)
- Existing scenarios unaffected (use historical OECD-19 list)
- New scenarios use updated list
- Engine versioning supports re-running historical analyses with old or new list

### EC-DATA-02: Country withdraws from OECD

**Trigger**: Hypothetically Switzerland leaves OECD.

**Severity**: P1

**Expected behavior**:
- Reference data updated
- Historical scenarios still reference CH (engine version frozen)
- New scenarios exclude CH from basket calculations

### EC-DATA-03: PPP adjuster for a country becomes < 1.0

**Trigger**: Country's GDP per capita PPP rises above US.

**Severity**: P0 (per CMS rule)

**Expected behavior**:
- Adjuster floored at 1.000 (CMS lower bound rule)
- Logged for transparency
- Documented in audit JSON

### EC-DATA-04: Brazil CMED rule activates (live flag flipped)

**Trigger**: BR regulator activates the CMED 3/2025 MIN rule.

**Severity**: P1

**Expected behavior**:
- Tenant admin can toggle "BR CMED active" in scenario
- Cascade applies stricter MIN rule for BR
- This is a v1.8 backlog item but architecture supports it

### EC-DATA-05: User enters scientific notation (1.8e5 = $180,000)

**Trigger**: Spreadsheet copy-paste artifact.

**Severity**: P2

**Expected behavior**:
- Parse scientific notation correctly
- Display as standard decimal in form

### EC-DATA-06: Currency mismatch (user enters EUR thinking USD)

**Trigger**: User confusion.

**Severity**: P2

**Expected behavior**:
- v2.0: All prices in USD only. Document clearly.
- v3.0+: support multi-currency with conversion via official rates

## Auth edge cases

### EC-AUTH-01: SSO IdP unavailable

**Trigger**: Tenant's IdP (e.g., Okta) is down.

**Severity**: P1

**Expected behavior**:
- Login flow times out gracefully (10s)
- Error message: "Unable to authenticate. Please try again or contact your admin."
- Existing valid sessions continue to work

### EC-AUTH-02: User's email changes in IdP

**Trigger**: HR changes user's email.

**Severity**: P1

**Expected behavior**:
- On next login, JWT contains new email
- Backend updates user record (matched by stable IdP user ID)
- Audit log entry: `auth.email.changed`

### EC-AUTH-03: API key compromise

**Trigger**: API key leaked publicly (e.g., committed to GitHub).

**Severity**: P0

**Expected behavior**:
- Customer revokes key via UI immediately
- All requests with revoked key return 401
- Optional: rate-limit detection + auto-revoke if anomalous traffic detected

## Async job edge cases

### EC-ASYNC-01: Worker crashes during Monte Carlo

**Trigger**: Worker process dies mid-N=500 simulation.

**Severity**: P1

**Expected behavior**:
- Job marked as `failed` with error code `worker_crashed`
- User sees "Job failed; please retry"
- Celery retry policy: 3 attempts with exponential backoff

### EC-ASYNC-02: Job queue overload

**Trigger**: 100+ Monte Carlo jobs queued.

**Severity**: P2

**Expected behavior**:
- Per-tenant rate limit (10 jobs/hour)
- Queue depth visible in user UI
- Estimated wait time shown

### EC-ASYNC-03: Job completed but user has logged out

**Trigger**: User starts Monte Carlo, closes browser, comes back next day.

**Severity**: P2

**Expected behavior**:
- Job result persisted in DB regardless
- On re-login, "Recent simulations" panel shows completed jobs
- Optional: email notification when job completes (if > 30s)

## Internationalization edge cases (future-proofing)

### EC-I18N-01: User in non-English locale

**Trigger**: French user accesses English-only UI.

**Severity**: P2

**Expected behavior**:
- v2.0: English UI with `lang="en"` HTML attribute
- Browser translation extensions work
- Server returns dates/numbers per user's locale (Accept-Language header)

### EC-I18N-02: Right-to-left language (Arabic, Hebrew)

**Trigger**: Future expansion.

**Severity**: P2 (not in v2.0 scope)

**Expected behavior**:
- v2.0: Don't break if locale is RTL (rare for pharma)
- v3.0+: full RTL support

## Browser edge cases

### EC-BROWSER-01: User on Internet Explorer

**Trigger**: Legacy enterprise environment.

**Severity**: P2

**Expected behavior**:
- Detect IE via user agent
- Show full-page banner: "This application is not supported on Internet Explorer. Please use Chrome, Edge, or Firefox."
- Block app load (no degraded experience)

### EC-BROWSER-02: User disables JavaScript

**Trigger**: Privacy-conscious user.

**Severity**: P2

**Expected behavior**:
- `<noscript>` tag with message: "JavaScript required."
- No SSR for v2.0 (acceptable trade-off)

### EC-BROWSER-03: User on iPad / mobile in landscape

**Trigger**: Field rep tries to demo on iPad.

**Severity**: P2

**Expected behavior**:
- v2.0: Show "Best on desktop" banner below 1024px
- App still loads, layouts may break
- Some interactions (drawer, slider) may be awkward but functional

## Compliance edge cases

### EC-COMP-01: GDPR data subject access request

**Trigger**: EU user requests "all my data".

**Severity**: P0

**Expected behavior**:
- Admin runs export tool
- Generates ZIP with: user profile, all assets created by user, all scenarios edited, all simulations run, all audit log entries
- Delivered within 30 days (GDPR requirement)

### EC-COMP-02: GDPR right to erasure

**Trigger**: User requests deletion.

**Severity**: P0

**Expected behavior**:
- 30-day grace period (in case of accidental request)
- After grace: full deletion of user record + anonymization of audit logs (replace user_id with system marker)
- Pricing data created by user retained (it's tenant data, not personal data)

### EC-COMP-03: SOX 404 audit request

**Trigger**: External auditor reviews tenant's pricing decisions.

**Severity**: P1

**Expected behavior**:
- Tenant admin can export all audit JSONs from a date range
- Audit logs immutable (no UPDATE/DELETE possible at DB level)
- Audit JSON includes engine version, methodology citations, full inputs

## Trial mode edge cases

### EC-TRIAL-01: Trial user enters apparent real pharma data

**Trigger**: User in trial enters US list price of $189,000 (looks real, not illustrative).

**Severity**: P1

**Expected behavior**:
- Heuristic detects: list price > $100K AND matches known drug pricing pattern
- Non-blocking soft notice appears: "This looks like real product pricing data. Trial mode is for illustrative use only."
- Two CTAs: "I'm using illustrative data" (dismiss) | "Tell me about production"
- False positive rate must be < 5% (tested in QA with synthetic illustrative data)
- Audit log records the warning shown (for legal traceability)

### EC-TRIAL-02: Trial expires while user is mid-session

**Trigger**: User has tab open at moment trial reaches `trial_expires_at`.

**Severity**: P1

**Expected behavior**:
- Background check on next API mutation: API returns 403 with code `trial_expired`
- UI shows modal: "Your trial expired. Read-only mode active. Talk to sales to upgrade."
- All data preserved; reads still work (so user can review their work)
- Cannot create/update/delete anything until upgrade

### EC-TRIAL-03: Trial user reaches asset limit (5 of 5)

**Trigger**: User clicks "Create asset" with 5 assets already.

**Severity**: P1

**Expected behavior**:
- API returns 403 with code `trial_limit_reached`
- UI shows modal with limit info: "Trial accounts limited to 5 assets. You have used 5/5. Upgrade to production for 100+ assets."
- Modal CTA: "Talk to sales" + "Archive an asset"
- Sample assets count toward limit (so trial = max 3 user-created assets after 2 samples)

### EC-TRIAL-04: Trial user tries to invite 4th user

**Trigger**: Trial admin clicks "Invite user" with 3 users already in tenant.

**Severity**: P1

**Expected behavior**:
- API returns 403 with code `trial_limit_reached`
- UI: "Trial accounts limited to 3 users. Upgrade to production for unlimited team access."
- Audit log entry: `trial.user_invite_blocked`

### EC-TRIAL-05: Trial user tries to access API with API key

**Trigger**: Trial user attempts to create an API key.

**Severity**: P1

**Expected behavior**:
- POST /api-keys returns 403 with code `feature_not_in_trial`
- UI shows: "API access is a production feature. Talk to sales."
- This prevents trial accounts from being abused as API gateways

### EC-TRIAL-06: Sample asset critical field edit attempt

**Trigger**: User tries to change US list price of "VX-CFTR-NG (Sample)" from $370,000 to $400,000.

**Severity**: P2

**Expected behavior**:
- Critical fields (asset name, US list price, fixture-defining fields) are read-only on sample assets
- API returns 403 with code `sample_field_immutable`
- UI: "Critical fields on sample assets are read-only to preserve methodology demonstration. Duplicate this asset to create an editable version."
- "Duplicate" CTA copies the sample to a new editable asset (counts toward 5-asset limit)

### EC-TRIAL-07: Sample asset duplication exceeds limit

**Trigger**: User has 4 user-created assets + 2 samples = 6 (sample exempt? No, both count). Tries to duplicate sample.

**Severity**: P2

**Expected behavior**:
- Block with limit-reached message
- Suggest: "Archive one of your assets to make room"

### EC-TRIAL-08: User signs up with existing email (already a trial)

**Trigger**: Same email signs up twice within retention window.

**Severity**: P1

**Expected behavior**:
- Detect existing trial tenant
- Show: "An account already exists for this email. Sign in instead?" with login link
- Do NOT auto-create a second trial (prevent abuse of 30-day trial reset)
- If original trial expired: offer "Talk to sales for production access" but no second trial

### EC-TRIAL-09: User upgrades to production then loses access to trial data

**Trigger**: Tenant tier changes from `trial` to `production`. User opens trial bookmark URL.

**Severity**: P2

**Expected behavior**:
- Trial tenant remains accessible (read-only) for 30 days post-upgrade
- After 30 days: trial tenant archived; URL returns "Trial archived. Your production tenant is at app.pricingstar.example.com/{prod_slug}"
- Audit log entry: `tenant.upgraded_to_production` with both tenant IDs

### EC-TRIAL-10: Disclaimer not accepted at signup (legal/audit)

**Trigger**: Audit asks for proof user accepted disclaimer.

**Severity**: P0 (legal)

**Expected behavior**:
- Audit log entry `trial.disclaimer_accepted` with timestamp, IP, user agent for every signup
- Disclaimer text version stored alongside (so legal can identify which version was accepted)
- If user did NOT check all 3 boxes: signup blocked, no tenant created
- Audit log query by user email returns disclaimer acceptance proof

---

*This is the final file in the PRD. The complete specification is now available for the engineering team to begin Phase 0.*

## Cross-references summary

For convenience, key cross-references across the PRD:

- **Calc engine functions**: `04_CALC_ENGINE_SPEC.md`
- **API endpoint contracts**: `05_API_CONTRACTS.md`
- **Data schemas**: `03_DATA_MODEL.md`
- **UI patterns**: `06_UI_COMPONENTS.md`
- **Tab-by-tab specs**: `07_TABS_SPEC/*`
- **Security & permissions**: `08_AUTH_PERMISSIONS.md`
- **Performance budgets**: `09_NON_FUNCTIONAL.md`
- **Validation fixtures**: `10_TEST_FIXTURES.md`
- **Build phasing**: `11_BUILD_ORDER.md`

For questions during build, refer back to `00_README.md` for navigation and to `01_PRODUCT_VISION.md` for product strategy context.
