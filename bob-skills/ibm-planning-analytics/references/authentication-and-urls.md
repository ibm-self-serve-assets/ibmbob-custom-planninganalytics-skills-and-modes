# Authentication & URL Map

How to reach Planning Analytics and authenticate, by environment (SKILL.md §2).
SaaS specifics here were **validated live** against `eu-central-1.planninganalytics.saas.ibm.com`.

## URL map (one PAW gateway, three API families)

Base: `https://<region>.planninganalytics.saas.ibm.com` (e.g. `eu-central-1`).
**Multi-tenant SaaS puts the tenant id in the path** (from the browser
`?tenantId=…`):

| API | URL pattern |
|-----|-------------|
| PAW content | `…/api/<tenantId>/v1/content/…` |
| TM1 REST (OData) | `…/api/<tenantId>/v1/tm1/<database>/api/v1/…` |
| OAuth | `…/oauth2/authorize` · `…/oauth2/token` |
| MCP | `…/api/<tenantId>/v1/…` (MCP routes) |

**Verified:** requesting the non-tenant form (`…/api/v1/content/…`) returns
`302 → …/api/<tenantId>/v1/content/…` — the gateway rewrites to the tenant path, so
always include the tenant. URL-encode spaces in names (`Planning%20Sample`).

## SaaS — MCSP API key → token (verified working)

```bash
curl -s -X POST https://account-iam.platform.saas.ibm.com/api/2.0/apikeys/token \
  -H "Content-Type: application/json" \
  -d '{"apikey":"<MCSP_API_KEY>"}'
# -> {"token":"eyJ…"}   (a JWT, exp ~1 hour)
```
- **Endpoint:** `https://account-iam.platform.saas.ibm.com/api/2.0/apikeys/token`
  — **no account id in the path** (the `…/accounts/<acct>/apikeys/token` form returns
  *"Scope not found"*; the `iam.platform.saas.ibm.com/siusermgr/…` form returns
  *"ApiKey is not valid"* — verified).
- The MCSP **API key** decodes to `k2:<keyId>:<secret>`. The returned **token**'s
  `aud` includes your MCSP **Service ID** and the PA service CRN
  `crn:v1:aws:public:planninganalytics:<region>:…`.
- Use it as `Authorization: Bearer <token>` with the tenant path. **Verified:** the
  token authenticates and the gateway resolves `/api/<tenant>/v1/…` (returns app-level
  200/404, no longer a login redirect).

## SaaS — OAuth 2.0 authorization-code (documented path for PAW REST)

IBM documents the PAW content + TM1 `v1` REST APIs as requiring **interactive OAuth
2.0 authorization-code**, scope **`v0userContext`** (other scopes/flows, incl.
**client-credentials, are not supported**):
1. An Environments/Subscription admin creates an **OAuth client** in PA Admin →
   **Integrations** (one client at a time; allowlist redirect URLs; generates a
   Client ID + secret).
2. App does the authorization-code dance against `…/oauth2/authorize` then exchanges
   the code at `…/oauth2/token` for a bearer token.
3. Call REST APIs with `Authorization: Bearer <access_token>`.
- **Prerequisite:** PAW **3.1.8+** or **2.1.21+**.
- Because it's interactive, an unattended agent needs a user to complete the flow
  once, then reuse/refresh the token.

## On-prem / classic TM1 (REST directly)

A TM1 server serves the REST API on its HTTPS port: `https://<tm1host>:<port>/api/v1/…`.
Auth modes (TM1 `IntegratedSecurityMode`):
- **1 = native/basic** — `Authorization: Basic base64(user:pass)`
- **2/3 = CAM** (Cognos Analytics) — CAM passport / SSO
- **5 = IntegratedSecurityMode 5 (IAM)** / **CAM + native**
- TM1py handles all of these via its connection config.

## Trial caveat (verified)

On a **Planning Analytics Trial** tenant, even with a valid token the content/TM1
`v1` routes return **`404 "The requested path was not found"`** — the REST surface is
gated and trial users can't model or create databases. For programmatic TM1/content
work use a full **PAW 3.1.8+/2.1.21+** environment with an OAuth client (or a TM1
database you can reach directly / via TM1py).

## Security
Keep the MCSP API key, OAuth client secret, and tokens in env vars / a secret store —
never in code or chat. Tokens expire (~1h) — refresh rather than hardcode.
