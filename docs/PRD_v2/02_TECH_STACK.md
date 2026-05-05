# Tech Stack & Architecture

## Architecture overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CDN / Edge layer                       │
│                  (Cloudflare or AWS CloudFront)             │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Frontend (SPA)                           │
│         React 18 + TypeScript + Vite + TanStack Query       │
│              Tailwind CSS + Recharts + Zustand              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTPS / OAuth 2.0
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    API Gateway (REST)                       │
│            Rate limiting, auth verification, logging        │
└──────────────────────────┬──────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
┌───────────▼─────┐ ┌──────▼──────┐ ┌────▼──────────┐
│  Application    │ │ Calc Engine │ │  Background   │
│  Service        │ │   Service   │ │   Workers     │
│  (Python/Node)  │ │  (Python)   │ │  (Celery/BMQ) │
└───────────┬─────┘ └──────┬──────┘ └──────┬────────┘
            │              │                │
            └──────────────┼────────────────┘
                           │
            ┌──────────────┴──────────────┐
            │                              │
┌───────────▼──────────┐    ┌──────────────▼─────────┐
│    PostgreSQL 15     │    │  Redis 7 (cache/queue) │
│   (multi-tenant)     │    │                        │
└──────────────────────┘    └────────────────────────┘
```

## Recommended stack

### Frontend

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Framework | **React 18 + TypeScript** | Mirrors V1.7 reference; React ecosystem maturity; TS for safety |
| Build | **Vite** | Fast dev experience; modern bundling |
| Styling | **Tailwind CSS** | Utility-first; consistent with V1.7 inline styling approach but more maintainable |
| State (server) | **TanStack Query** | Cache management, optimistic updates, error retry built-in |
| State (client) | **Zustand** | Simpler than Redux for our scale; works well with React 18 |
| Charts | **Recharts** | Used in V1.7; sufficient for our needs; no need for D3 complexity |
| Forms | **React Hook Form + Zod** | Type-safe validation, performant |
| Routing | **React Router v6** | Standard, stable |
| Testing | **Vitest + React Testing Library + Playwright** | Vitest matches Vite ecosystem; RTL for components; Playwright for E2E |

### Backend

| Layer | Choice (preferred) | Alternative | Rationale |
|-------|--------------------|-------------|-----------|
| Language | **Python 3.11+** | Node.js/TypeScript | Calc engine has math; Python ecosystem (numpy/scipy if needed) is stronger; both acceptable |
| Web framework | **FastAPI** | Express.js | Async support, auto-generated OpenAPI docs, type hints |
| ORM | **SQLAlchemy 2.0 + Alembic** | Prisma (if Node) | Mature, async-friendly, migrations |
| Validation | **Pydantic v2** | Zod (if Node) | Schema-driven validation, OpenAPI integration |
| Background jobs | **Celery + Redis** | BullMQ (if Node) | Mature for long-running tasks (Monte Carlo) |
| Testing | **pytest + httpx + factoryboy** | Jest (if Node) | Standard Python test stack |

### Database

| Choice | Rationale |
|--------|-----------|
| **PostgreSQL 15+** | Strong consistency, JSON support for audit trails, mature multi-tenancy patterns |
| **Redis 7+** | Caching layer + job queue + session store |
| ❌ NoSQL | Rejected — relational data (assets, scenarios, cross-tenant isolation) demands SQL |

### Infrastructure

| Layer | Choice (v2.0 MVP) | Choice (scale stage) | Notes |
|-------|-------------------|----------------------|-------|
| Hosting platform | **Railway** | AWS / GCP | Railway = fast time-to-market; migrate when SLA needs increase |
| Container | Railway native (or Docker) | **ECS/Fargate** or **GKE** | Stateless services; horizontal scaling |
| Database | **Railway Postgres** | **RDS Postgres** or **Cloud SQL** | Managed; multi-AZ for prod |
| Cache/Queue | **Railway Redis** | **ElastiCache** or **Memorystore** | |
| CDN | **Cloudflare** | CloudFront | Static asset delivery |
| Secret mgmt | Railway env vars + 1Password | **AWS Secrets Manager** or **Vault** | No secrets in code |
| Monitoring | Sentry (free tier) | **Datadog** or **New Relic** | Sentry sufficient for MVP |
| Logging | Railway native + Sentry | CloudWatch / Datadog | Aggregate when scale demands |
| CI/CD | **GitHub Actions** | Same | Push-to-deploy via Railway hook |

**Why Railway for MVP**: Railway provides Postgres, Redis, app deployment, and SSL all in one platform with $0-50/month for early stage. No DevOps engineer needed. Migration path to AWS exists when scale or compliance requires it (year 2+).

### Auth

| Layer | Choice (v2.0 MVP) | Choice (enterprise stage) | Notes |
|-------|-------------------|---------------------------|-------|
| Identity provider | **Self-managed via Keycloak on Railway** OR **Auth0 free tier** | **Auth0 paid** or **AWS Cognito** | Keycloak free / Auth0 free up to 7000 MAU |
| Trial mode auth | Email + password + optional TOTP | Same | No SSO for trial (per `13_TRIAL_MODE.md`) |
| Production tenant SSO | OIDC (any IdP) | OIDC + SAML | SAML added when first enterprise prospect requires |
| Session | **JWT + refresh tokens** | Same | Standard pattern; refresh token rotation |
| MFA | **TOTP** | TOTP + WebAuthn | TOTP via libraries (e.g., `pyotp`); WebAuthn deferred to enterprise stage |

**Recommendation for first build**: Start with **Auth0 free tier** (faster to integrate, 7000 MAU free). Migrate to Keycloak self-hosted on Railway when:
- MAU approaches 7000 (cost crossover)
- Enterprise prospects require self-hosted IdP
- Year 2+ when team has bandwidth for Keycloak operations

## Why these choices

### Why Python over Node.js for backend

The calculation engine is math-heavy. Python's numerical ecosystem (`numpy`, `scipy.stats` for Monte Carlo) is more mature than Node's. The V1.7 reference is JavaScript, but the math is trivially portable. Python also produces more readable code for the calculation functions, which matters for audit/regulatory review.

If the team strongly prefers Node.js, the engine ports easily — we have working Python implementations in the test simulations (`run_oncmab_test_v20.py`, `run_vertex_test_v11.py`).

### Why Postgres over MongoDB

- Tenant isolation is easier with row-level security in Postgres (or app-level filters with strong typing)
- Audit trails benefit from JSON columns (Postgres has excellent JSON support)
- Reporting queries (cross-asset analyses) need joins
- Pricing data is structured; NoSQL flexibility offers no benefit

### Why Tailwind over CSS-in-JS

V1.7 uses inline styles, which got unwieldy. Tailwind brings discipline (utility classes) without bundle bloat. The team can extract recurring patterns into components without losing the speed of utility-first.

### Why FastAPI over Django

Django is overkill for our API surface. FastAPI gives auto-generated OpenAPI docs (huge value for frontend devs), async support out of the box, and Pydantic integration. Django's admin console is irrelevant for our use case.

## Service decomposition

### Service: `app-api` (main backend)

- All REST endpoints
- Business logic (asset management, scenarios, audit)
- Auth verification
- Tenant context injection
- Stateless, horizontally scalable

### Service: `calc-engine` (calculation worker)

- All math functions (Method I/II, IRP cascade, NPV, Monte Carlo)
- Stateless
- Called synchronously for fast operations (cascade < 200ms)
- Called asynchronously for slow operations (Monte Carlo with N=500)
- Could be co-located with `app-api` in MVP, separated later for scale

### Service: `worker-async` (background jobs)

- Monte Carlo simulations
- Audit log batch writes (if needed)
- Report generation
- Celery + Redis for queue

### Service: `frontend` (React SPA)

- Static build deployed to S3 + CloudFront
- No server-side rendering (SSR not needed; tool is for authenticated users only)

## Data flow examples

### "Run a scenario simulation"

```
1. User clicks "Run scenario" in Tab 6 (Optimizer)
2. Frontend POSTs /api/scenarios/{id}/simulate
3. app-api validates request, fetches scenario from DB
4. app-api calls calc-engine.simulate(scenario)
5. calc-engine runs cascade → method I → method II → NPV
6. calc-engine returns result (~200ms typical)
7. app-api persists simulation result + audit log
8. app-api returns result to frontend
9. Frontend updates UI with results
```

### "Run Monte Carlo G2N analysis"

```
1. User clicks "Run Monte Carlo" in Tab 6
2. Frontend POSTs /api/scenarios/{id}/monte-carlo
3. app-api validates, enqueues job to worker-async via Redis
4. app-api returns 202 Accepted with job_id
5. Frontend polls /api/jobs/{job_id} every 2s
6. worker-async runs N=500 simulations (~10-30s)
7. worker-async writes result to DB
8. Frontend polls return 200 with result; UI displays confidence intervals
```

## Performance budgets

| Operation | Budget | Rationale |
|-----------|--------|-----------|
| Page load (cold) | < 2s | Demo-ability for prospects |
| Page navigation | < 200ms | Feel snappy |
| Cascade calculation | < 200ms | Real-time feedback |
| NPV calculation | < 500ms | User clicks "calculate" → result |
| Monte Carlo (N=500) | < 30s | Async, with progress indicator |
| Audit JSON export | < 1s | One-click download |

## Security requirements (high-level — see `09_NON_FUNCTIONAL.md` for detail)

- HTTPS only (TLS 1.3)
- All data encrypted at rest (AES-256)
- All data encrypted in transit
- Tenant data isolation verified by automated test on every PR
- No PII in logs (drug pricing data is sensitive but not PII)
- Audit log immutable (append-only)
- SOC 2 Type II compliance target (year 1)

## Monorepo vs split repos

**Recommendation**: Single monorepo with clear directory structure.

```
pricing-star/
├── frontend/           # React app
├── backend/            # FastAPI service(s)
├── shared/             # Shared types (TypeScript) / schemas (JSON)
├── infrastructure/     # Terraform / CDK
├── docs/               # PRD + API docs
└── .github/workflows/  # CI/CD
```

Rationale: A monorepo is simpler at our team size (5-7 engineers). Lock-step deployments easier. Shared types are real (calculation inputs/outputs are used by both frontend and backend).

If team prefers split, the boundary should be at frontend vs backend. Don't split backend into multiple repos until services genuinely need independent release cycles.

---

*Next: read `03_DATA_MODEL.md`*
