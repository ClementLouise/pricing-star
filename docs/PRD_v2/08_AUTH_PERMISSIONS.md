# Authentication & Permissions

## Overview

Multi-tenant SaaS with enterprise-grade auth from day 1. OIDC/SAML federation with RBAC inside each tenant.

## Authentication

### Identity provider

**Recommended**: Auth0 (faster integration) or AWS Cognito (AWS-native).
**Alternative**: Self-hosted Keycloak if team prefers no third-party.

### Supported flows

- **Social login** (Google, Microsoft): Allowed for individual users on trial
- **Enterprise SSO** (SAML 2.0, OIDC): Mandatory for paid tenants
- **API keys**: For service accounts (CI/CD, automated reports)

### MFA

- **TOTP**: Required for admin role
- **WebAuthn / FIDO2**: Optional but recommended for security-conscious tenants
- **SMS/Email OTP**: NOT used (security weakness)

### Session management

- **Access token**: JWT, 1 hour TTL
- **Refresh token**: 30 days, rotated on use
- **Inactivity timeout**: 30 minutes idle → logout
- **Absolute session limit**: 12 hours (re-auth required)

### Tenant onboarding

```
1. New tenant signs contract (out of band)
2. Admin user created via API (manual step by ops team)
3. Admin receives magic link to set password / enable MFA
4. Admin configures SSO (SAML metadata or OIDC client ID)
5. Admin invites users via UI (POST /tenants/current/users)
6. Invited users authenticate via tenant's SSO
```

## Permissions (RBAC)

### Roles

Three roles within each tenant:

| Role | Description | Typical user |
|------|-------------|--------------|
| `admin` | Full access incl. user management, billing, audit logs | Pricing Lead, IT admin |
| `editor` | Create/edit/delete assets, scenarios; cannot manage users | Pricing analysts |
| `viewer` | Read-only on all data | CFO, Regulatory, Legal |

### Permission matrix

| Action | admin | editor | viewer |
|--------|:-----:|:------:|:------:|
| **User management** | | | |
| Invite user | ✅ | ❌ | ❌ |
| Change user role | ✅ | ❌ | ❌ |
| Disable user | ✅ | ❌ | ❌ |
| **Asset** | | | |
| Create asset | ✅ | ✅ | ❌ |
| Update asset | ✅ | ✅ | ❌ |
| Archive asset | ✅ | ✅ | ❌ |
| View asset | ✅ | ✅ | ✅ |
| **Scenario** | | | |
| Create scenario | ✅ | ✅ | ❌ |
| Update scenario | ✅ | ✅ | ❌ |
| Delete scenario | ✅ | ✅ | ❌ |
| Run simulation | ✅ | ✅ | ✅ |
| **Audit** | | | |
| Export audit JSON | ✅ | ✅ | ✅ |
| View audit logs | ✅ | ❌ | ❌ |
| **Settings** | | | |
| View tenant settings | ✅ | ✅ | ✅ |
| Update tenant settings | ✅ | ❌ | ❌ |
| Manage API keys | ✅ | ❌ | ❌ |
| **Billing** | | | |
| View invoices | ✅ | ❌ | ❌ |
| Update payment method | ✅ | ❌ | ❌ |

### Permission enforcement

- **Frontend**: Hide UI elements based on user role; do NOT rely on this for security
- **Backend**: Verify permissions on every request via middleware/decorator

```python
# Example FastAPI implementation
@router.post("/assets")
@require_role(["admin", "editor"])
async def create_asset(
    payload: CreateAssetSchema,
    user: User = Depends(get_current_user)
):
    # User context already verified
    return await asset_service.create(payload, tenant_id=user.tenant_id, user_id=user.id)
```

## Multi-tenancy isolation

### Tenant context propagation

Every request must include tenant context:

```
1. JWT contains `tenant_id` claim
2. API middleware extracts tenant_id from JWT
3. Tenant context attached to request object (e.g., `request.state.tenant_id`)
4. Repository methods receive tenant_id and filter ALL queries
5. Database-level RLS as defense-in-depth (optional)
```

### Cross-tenant access prevention

**At application layer** (mandatory):

```python
# Repository pattern
class AssetRepository:
    def get(self, asset_id: UUID, tenant_id: UUID) -> Asset | None:
        return self.session.query(Asset).filter(
            Asset.id == asset_id,
            Asset.tenant_id == tenant_id,  # ALWAYS
            Asset.archived_at.is_(None)
        ).one_or_none()
```

**At database layer** (defense-in-depth, optional):

```sql
ALTER TABLE asset ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON asset
  USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

### Testing tenant isolation

A dedicated test suite verifies isolation:

```python
def test_user_a_cannot_access_tenant_b_assets():
    user_a = create_user(tenant_id=tenant_a)
    asset_b = create_asset(tenant_id=tenant_b)
    
    response = client.get(f"/assets/{asset_b.id}", headers=auth(user_a))
    assert response.status_code == 404  # NOT 200, NOT 403
```

These tests must run on every PR; failure blocks merge.

## API key management

For service accounts (e.g., scheduled report generation, CI/CD):

### Creation

```http
POST /v1/api-keys
{
  "name": "Reports automation",
  "permissions": ["read:assets", "read:scenarios", "run:simulations"],
  "expires_at": "2027-05-01T00:00:00Z"
}
```

Response includes the full key once (cannot be retrieved later):

```json
{
  "id": "uuid",
  "name": "Reports automation",
  "key": "ppi_live_abc123...xyz",   // Only shown once!
  "key_prefix": "ppi_live_abc1",
  "permissions": [...]
}
```

### Storage

- Hashed with bcrypt (cost factor 12) before storage
- Only key prefix (8 chars) stored unhashed for identification
- Cannot be retrieved; must be recreated if lost

### Revocation

```http
DELETE /v1/api-keys/{key_id}
```

Sets `revoked_at`. Revoked keys fail auth immediately.

### Rotation policy

- API keys expire after 1 year by default
- Email reminder 30 days before expiry
- Customer portal allows self-service rotation

## Password policy (for users with password auth — not SSO)

- Minimum 12 characters
- At least 1 uppercase, 1 lowercase, 1 digit, 1 special char
- Cannot reuse last 5 passwords
- Forced reset every 90 days (if not using SSO/MFA)
- Account lockout after 5 failed attempts (30-min lockout)
- Bcrypt hash (cost factor 12)

For SSO users: password policy enforced by IdP, not us.

## Audit logging for auth events

Every auth event is logged:

| Event | Logged data |
|-------|-------------|
| `auth.login.success` | user_id, ip, user_agent, mfa_used |
| `auth.login.failure` | email_attempted, ip, reason |
| `auth.logout` | user_id, session_duration |
| `auth.mfa.enabled` | user_id, method (totp/webauthn) |
| `auth.password.reset` | user_id, ip |
| `auth.role.changed` | user_id (target), changed_by, old_role, new_role |
| `auth.user.disabled` | user_id, disabled_by, reason |
| `auth.api_key.created` | api_key_id, created_by |
| `auth.api_key.revoked` | api_key_id, revoked_by |

Audit logs immutable; retained 7 years.

## Compliance

### SOC 2 Type II

Target: certification within 12 months of launch.

Required controls:
- Access logging
- Encryption at rest and in transit
- Vulnerability scanning
- Backup and DR
- Incident response procedures

### GDPR

For EU customers:
- Right to access: user can export all their data via UI
- Right to erasure: workflow for full account deletion (30-day grace period)
- Data residency: EU customers' data stored in EU region (if requested)

### HIPAA

NOT required (we don't handle PHI; pricing data is not PHI).

### SOX 404

For tenants subject to SOX:
- Audit JSON Export feature provides defensible records
- Audit logs immutable
- Engine version traceability for re-running historical analyses

---

*Next: read `09_NON_FUNCTIONAL.md`*
