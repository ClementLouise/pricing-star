# Non-Functional Requirements

## Performance

### Response time budgets

| Operation | P50 | P95 | P99 | Notes |
|-----------|-----|-----|-----|-------|
| Page load (cold) | 1.5s | 2.5s | 4s | Initial app shell + first render |
| Page navigation | 100ms | 300ms | 500ms | Tab switch, route change |
| API: simple GET | 50ms | 200ms | 500ms | List/read operations |
| API: simulate | 200ms | 500ms | 1000ms | Cascade + Method I/II + NPV |
| API: anchor analysis | 50ms | 150ms | 300ms | Sort + compute |
| API: DE cascade | 300ms | 600ms | 1000ms | Includes cascade re-run |
| API: Monte Carlo (N=500) | 5s | 15s | 30s | Async, with progress |
| API: audit JSON export | 200ms | 500ms | 1s | Includes full data assembly |

### Concurrency targets

- 50 concurrent users per tenant
- 500 concurrent users platform-wide (10 tenants × 50 users at MVP)
- 50 concurrent simulations
- 5 concurrent Monte Carlo jobs

### Scalability

Horizontal scaling on app-api (stateless). Database is the bottleneck:
- Connection pool: 20 connections per app instance
- DB read replicas added when read load > 70% CPU on primary
- Caching layer (Redis) for reference data (PPP adjusters, IRP rules)

## Availability

### SLA

- **MVP (months 0-6)**: 99% uptime (allows 7.2h downtime/month)
- **Year 1 GA**: 99.5% uptime
- **Year 2+**: 99.9% uptime

### Monitoring

- Health check endpoint: `/health` (liveness), `/health/ready` (readiness)
- Synthetic monitoring: Datadog or Pingdom hits key endpoints every 1 min
- Error rate alerts: > 1% errors over 5 min triggers PagerDuty
- Latency alerts: P95 > budget triggers warning

### Incident response

- On-call rotation: 1 primary + 1 backup (engineering team)
- SLA acknowledge: 15 min during business hours, 30 min off-hours
- SLA resolve: 4 hours for critical (P0), 1 business day for high (P1)
- Post-mortems mandatory for P0 incidents within 5 business days

## Security

### Encryption

- **At rest**: AES-256 for database, encrypted EBS/disks
- **In transit**: TLS 1.3 only (TLS 1.2 deprecated)
- **Backups**: Encrypted with separate KMS key
- **Secrets**: AWS Secrets Manager / HashiCorp Vault; never in code or env files

### Authentication

See `08_AUTH_PERMISSIONS.md`.

### Authorization

- All endpoints require auth (except `/health`, `/auth/login`, `/auth/callback`)
- Permission checks on every request (decorator-based)
- Tenant isolation tested on every PR

### Input validation

- All API inputs validated with Pydantic (or Zod) schemas
- Rejecting any input that doesn't match schema
- SQL injection prevented by ORM parameterization (no raw SQL with user input)
- XSS prevented by React's default escaping; no `dangerouslySetInnerHTML` without security review

### Output encoding

- API responses always JSON (no HTML interpolation)
- File downloads with `Content-Disposition: attachment`
- No user input echoed without sanitization

### Vulnerability management

- Dependabot / Renovate for dep updates
- Snyk or equivalent for vuln scanning (weekly)
- Annual penetration test (external firm)
- Bug bounty program (year 2+)

### Specific protections

- **CSRF**: SameSite=Strict cookies + CSRF tokens for state-changing operations
- **Clickjacking**: `X-Frame-Options: DENY`
- **MIME sniffing**: `X-Content-Type-Options: nosniff`
- **HSTS**: 2-year HSTS with preload
- **CSP**: Strict CSP (no `unsafe-inline`, no `unsafe-eval`)
- **Rate limiting**: Per-user and per-IP (see `05_API_CONTRACTS.md`)

### Data privacy

- No PII collected beyond email + name
- Pricing data is sensitive (commercial confidential) but not PII
- No tracking pixels, no third-party analytics that share user data
- Customers can request data export or deletion (GDPR compliance)

## Accessibility

### Standards

WCAG 2.1 Level AA compliance for all production pages.

### Testing

- Automated: axe-core in CI (blocks merge on violations)
- Manual: keyboard-only navigation test in QA sign-off
- Annual third-party audit

### Specific requirements

- Color contrast: 4.5:1 for normal text, 3:1 for large text and UI elements
- All interactive elements keyboard accessible (Tab, Enter, Esc)
- All images have alt text (or marked decorative)
- All form fields have associated labels
- Focus indicators visible (no `outline: none` without replacement)
- Screen reader: tested with NVDA (Windows) and VoiceOver (Mac)
- Reduced motion: `prefers-reduced-motion` honored
- Skip-to-content link

## Internationalization (i18n)

### MVP scope

English only. All UI copy in `en` locale.

### Architecture

Implement i18n infrastructure from day 1 (using `react-i18next` or equivalent), even if only English ships:

- All user-facing strings externalized to JSON catalogs
- No hardcoded strings in components
- Date/number formatting via `Intl.DateTimeFormat` and `Intl.NumberFormat`

### Future locales (not in v2.0 scope)

- French (fr) — for European mid-cap pharma
- German (de) — for DACH pharma
- Japanese (ja) — for Japanese mid-cap

## Browser support

Production support:

| Browser | Minimum version | Notes |
|---------|-----------------|-------|
| Chrome | Last 2 stable | Primary target |
| Edge | Last 2 stable | |
| Firefox | Last 2 stable | |
| Safari | Last 2 stable | macOS desktop only |

Not supported:
- Internet Explorer (any version)
- Mobile browsers (responsive but not optimized)
- Browsers older than 2 stable releases

## Data retention & backup

### Retention

See `03_DATA_MODEL.md` "Data retention" section.

### Backup

- Database: Daily full backup, hourly incremental, 30-day retention
- Object storage (audit JSONs, exports): Versioning enabled, 30-day retention
- Cross-region replication for production
- Backup restoration tested quarterly (drill)

### Disaster recovery

- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 1 hour
- DR runbook documented and tested annually

## Logging & observability

### Application logs

- Structured JSON logs (compatible with Datadog/Splunk/CloudWatch)
- Log levels: DEBUG (dev only), INFO, WARN, ERROR
- Required fields: timestamp, level, service, tenant_id (when applicable), trace_id, message
- No PII in logs (drug pricing OK; user emails masked except in auth events)

### Metrics

- Request rate, error rate, latency (P50, P95, P99)
- Per-endpoint metrics
- Business metrics: simulations run/day, audit exports/day, monte carlo jobs/day
- Custom dashboards in Datadog or Grafana

### Tracing

- OpenTelemetry instrumentation
- Trace ID propagated from frontend to backend
- Slow trace alerts (> P99 budget)

### Error tracking

- Sentry or Rollbar
- All unhandled exceptions captured
- Source maps uploaded for production builds

## Operational metrics (SLI / SLO)

| SLI | SLO target |
|-----|------------|
| API availability | 99.5% |
| Simulation success rate | > 99% |
| API P95 latency | < 500ms |
| Page load P95 | < 2.5s |
| Audit JSON export success rate | > 99.9% |

## Deployment

### Strategy

Blue-green or rolling deploys, zero-downtime.

### Frequency

- Backend: Multiple times per day (continuous deployment to staging on merge)
- Frontend: Multiple times per day
- Production: Behind feature flags; release to small % of traffic first

### Rollback

- Automatic rollback on error rate spike
- Manual rollback available via dashboard
- Database migrations always backwards-compatible (forward + rollback)

## Cost & resource constraints

### Cloud spend targets

- MVP (10 tenants): < $5K/month
- GA (50 tenants): < $25K/month
- Cost per tenant: target $500/month at scale

### Resource quotas per tenant

| Resource | Default quota | Notes |
|----------|---------------|-------|
| Active users | 50 | Configurable per contract |
| Assets | 100 | Soft limit; admin can request increase |
| Scenarios per asset | 50 | |
| Simulations per month | 10,000 | Most tenants use < 1000 |
| Monte Carlo jobs per month | 100 | |
| Audit JSON exports per month | 1,000 | |
| API calls per hour | 1,000 per user | See rate limiting |

Quotas displayed in Settings; upgrade path via sales.

---

*Next: read `10_TEST_FIXTURES.md`*
