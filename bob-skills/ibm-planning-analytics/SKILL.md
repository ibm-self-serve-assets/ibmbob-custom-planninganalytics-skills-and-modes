---
name: ibm-planning-analytics
description: >-
  Work with IBM Planning Analytics (PA / TM1) and Planning Analytics Workspace
  (PAW) through their REST APIs. Use this whenever the user mentions Planning
  Analytics, PA, TM1, Planning Analytics Workspace / PAW, a TM1 cube / dimension
  / hierarchy / element / subset / view / process (TI) / chore / cellset, MDX
  against TM1, reading or writing cube data, executing a TurboIntegrator
  process, PAW content (books, views, folders, websheets), the TM1 REST API
  (OData), the PAW REST API, the planninganalytics.saas.ibm.com SaaS, MCSP / IAM
  auth for PA, or the TM1py Python SDK. Use for "list cubes/dimensions",
  "read/write cube cells", "run an MDX query", "execute a TI process", "create a
  view/subset", "manage PAW books/folders", or "connect to Planning Analytics
  from code".
metadata:
  enabled: true
  author: adapted from IBM PA/TM1 REST docs + live validation
  version: 1.0.0
  disable-model-invocation: true
---

# IBM Planning Analytics (TM1 + PAW) — REST API

Authoritative guide to automating **IBM Planning Analytics** — the **TM1**
in-memory OLAP engine plus **Planning Analytics Workspace (PAW)** — through their
**REST APIs**. Grounded in the IBM PA REST docs and **validated live against a
Planning Analytics SaaS (eu-central-1) MCSP account**.

> **Golden rule #1 — three API families, one gateway.** Everything goes through the
> PAW host:
> - **PAW content API** — books/views/folders: `…/api/<tenant>/v1/content/…`
> - **TM1 REST API** (OData v4) — cubes/dims/data/processes: `…/api/<tenant>/v1/tm1/<db>/api/v1/…`
> - **MCP endpoints** — AI-tool integration.
> On **multi-tenant SaaS the tenant id is in the path**: `/api/<tenantId>/v1/…`
> (verified — the gateway 302-redirects the non-tenant form to this). Get the
> tenant id from the browser URL (`?tenantId=…`).
>
> **Golden rule #2 — auth has two realities; pick the right one.**
> - **MCSP API key → token** (SaaS account/identity): `POST
>   https://account-iam.platform.saas.ibm.com/api/2.0/apikeys/token` `{"apikey":…}`
>   → a bearer JWT. **Verified working.**
> - **PAW REST (content + TM1) on SaaS** is documented to require the **OAuth 2.0
>   authorization-code flow** (interactive, scope `v0userContext`) via an OAuth
>   client configured in PA Admin → Integrations; **client-credentials is not
>   supported**. The content/TM1 `v1` routes also need **PAW 3.1.8+/2.1.21+** and
>   are **not available on Trial tenants** (verified: routes 404 even when the token
>   authenticates). Plan auth around the target environment — see §2.

---

## 1. Mental model

| Object | What it is | Lives in |
|--------|-----------|----------|
| **Database (TM1 server)** | An in-memory OLAP model (a "database" in PA terms) | TM1 |
| **Cube** | A multi-dimensional data container (measures by dimensions) | TM1 |
| **Dimension → Hierarchy → Element** | The axes; elements are members (N=numeric leaf, C=consolidated, S=string) | TM1 |
| **Attribute** | Element/cube metadata (alias, format, …) | TM1 |
| **Subset** | A named/dynamic (MDX) set of elements | TM1 |
| **View** | A saved slice of a cube (native or MDX) | TM1 |
| **Cellset** | The result of an MDX query (axes + cells) — how you read/write data | TM1 |
| **Process (TI)** | A TurboIntegrator ETL/automation script | TM1 |
| **Chore** | A schedule of processes | TM1 |
| **Sandbox** | A what-if private data layer over a cube | TM1 |
| **Book / View / Folder / Websheet** | PAW content assets | PAW |

Three programming surfaces (one PAW gateway): **PAW content API**, **TM1 REST API**
(OData), and **MCP**. The **TM1 REST API is the workhorse** for data and modeling.

Full URL/auth detail: **[references/authentication-and-urls.md](references/authentication-and-urls.md)**.

---

## 2. Connect & authenticate

Choose by environment. SaaS specifics validated below.

### SaaS — MCSP API key → token (validated)
```bash
# 1) exchange the MCSP API key for a bearer token (~1h)
curl -s -X POST https://account-iam.platform.saas.ibm.com/api/2.0/apikeys/token \
  -H "Content-Type: application/json" -d '{"apikey":"<MCSP_API_KEY>"}'   # -> {"token":"eyJ…"}
# 2) call PA with the token + the TENANT in the path:
curl -s -H "Authorization: Bearer <token>" -H "Accept: application/json" \
  "https://<region>.planninganalytics.saas.ibm.com/api/<tenantId>/v1/tm1/<db>/api/v1/Cubes?\$select=Name"
```
- Region host e.g. `eu-central-1.planninganalytics.saas.ibm.com`; tenant id from the
  browser URL (`?tenantId=…`). The token's `aud` includes the PA service CRN for the
  region and your MCSP **Service ID**.
- **Verified:** the token authenticates and the gateway resolves the tenant path
  (`/api/<tenant>/v1/…`); the non-tenant form 302-redirects to it.

### SaaS — OAuth 2.0 authorization-code (documented path for PAW REST)
The PAW content + TM1 `v1` REST APIs are documented to require **interactive OAuth**
(scope `v0userContext`) via an OAuth client (PA Admin → **Integrations** → add OAuth
client; one client at a time; allowlist redirect URLs). Endpoints:
`https://<paw_host>/oauth2/authorize` and `…/oauth2/token`. Non-interactive
client-credentials is **not** supported. Requires **PAW 3.1.8+ / 2.1.21+**.

### On-prem / classic TM1 (TM1 REST directly)
A TM1 server exposes the REST API on its own HTTPS port: `https://<tm1>:<port>/api/v1/…`
with TM1 auth modes — **basic** (mode 1), **CAM/SSO** (modes 2/3/5), or **integrated/
native**. The **TM1py** SDK wraps all of these (see §6).

> **Trial caveat (verified):** on a **Planning Analytics Trial** tenant the content/
> TM1 `v1` routes return **404** even with a valid token — trial accounts can't model
> or create databases and the REST surface is gated. Use a full PAW 3.1.8+/2.1.21+
> environment for programmatic TM1/content work.

Keep API keys/secrets in env/secret stores. Full auth matrix:
**[references/authentication-and-urls.md](references/authentication-and-urls.md)**.

---

## 3. TM1 REST API — the workhorse (OData)

The TM1 REST API is **OData v4**: resources, `$select/$filter/$expand/$top`,
navigation, and actions. Base (SaaS): `…/api/<tenant>/v1/tm1/<db>/api/v1/`. Full
surface + payloads: **[references/tm1-rest-api.md](references/tm1-rest-api.md)**.

### Metadata (discover the model)
```
GET .../Cubes?$select=Name
GET .../Dimensions?$select=Name
GET .../Dimensions('Region')/Hierarchies('Region')/Elements?$select=Name,Type
GET .../Cubes('Sales')?$expand=Dimensions($select=Name)
GET .../Processes?$select=Name        GET .../Chores?$select=Name
```

### Read data — MDX → Cellset (the core pattern)
You read cube data by **POSTing an MDX query** to create a **cellset**, then GET its
cells:
```
POST .../Cellsets            body: {"MDX":"SELECT … ON 0, … ON 1 FROM [Sales] WHERE (…)"}
   -> returns a Cellset with an ID
GET  .../Cellsets('<id>')?$expand=Cube($select=Name),Axes($expand=Tuples($expand=Members($select=Name))),Cells($select=Ordinal,Value,FormattedValue)
DELETE .../Cellsets('<id>')   # free it
```
Or the one-shot action: `POST .../ExecuteMDX` / `POST .../Cubes('X')/Views('Y')/tm1.Execute`.

### Write data
- Cell updates via an **Update Cellset**: `POST .../Cellsets` (MDX defining the
  cells), then `PATCH .../Cellsets('<id>')/Cells` with ordinals + values.
- Or a TI process / `tm1.Update` actions. Writes respect security & rules.

### Execute processes / chores
```
POST .../Processes('LoadActuals')/tm1.ExecuteWithReturn   body: {"Parameters":[{"Name":"pYear","Value":"2026"}]}
POST .../Chores('NightlyLoad')/tm1.Execute
```
Long operations: send `Prefer: respond-async` and poll the returned location.

### Views & subsets
Create/read **subsets** (static element lists or **dynamic MDX**) and **views**
(native or MDX) to slice cubes for reports and extracts.

> **MDX cellset cleanup:** always `DELETE` cellsets you create (they consume server
> memory). Use `$top`/`$select` to keep responses small; large extracts should use
> async + paging.

---

## 4. PAW content API

Manage Workspace assets — **books, views, folders, websheets** — under
`…/api/<tenant>/v1/content/…`. Full endpoints:
**[references/paw-content-api.md](references/paw-content-api.md)**.

```
GET    .../v1/content/assets(path='shared')/assets      # list the shared folder
GET    .../v1/content/assets('<id>')                    # asset metadata (+ /content for the body)
POST   .../v1/content/assets(path='shared')/assets      # create a folder / book
PUT    .../v1/content/assets('<id>')                    # update an asset
DELETE .../v1/content/assets('<id>')                    # delete
```
~25 content endpoints (list/create/update/delete folders, books, views, retrieve
metadata/content). Resolve assets by **path** (when you don't know the id) or **id**.

---

## 5. MCP endpoints (AI tooling)

PAW also exposes **Model Context Protocol** endpoints for AI-tool integration
(`…/api/<tenant>/v1/…` MCP routes), so an agent can drive PA capabilities through a
standard tool interface. Availability tracks the PAW version/feature flags. See
**[references/tools-tm1py-mcp.md](references/tools-tm1py-mcp.md)**.

---

## 6. Tooling — TM1py & Postman

- **TM1py** — the de-facto Python SDK for the TM1 REST API. It wraps connection/auth
  (basic, CAM, IAM/MCSP, PAW-gateway), cubes, dimensions, elements, cellsets/MDX,
  processes, subsets, views, sandboxes — far less boilerplate than raw HTTP. Prefer
  it for Python automation. Patterns: **[references/tools-tm1py-mcp.md](references/tools-tm1py-mcp.md)**.
- **Postman** — IBM publishes a Planning Analytics collection (the "Planning
  Analytics" workspace on the Postman API Network) with worked TM1/PAW requests.

---

## 7. Critical constraints (these cause failures — internalize them)

- ✅ **Tenant in the path on SaaS:** `/api/<tenantId>/v1/…` (verified). Omit it and
  you get a 302 to `/login`.
- ✅ **Auth model matters:** MCSP API-key token works for SaaS identity (verified);
  the **PAW content/TM1 REST API is documented to require interactive OAuth
  `v0userContext`** + an OAuth client + PAW 3.1.8+/2.1.21+. Client-credentials is
  unsupported.
- ✅ **Trial tenants gate the REST surface** — `v1` routes 404 even when authenticated
  (verified). No modeling / no new databases on Trial.
- ✅ **Data is read/written via MDX cellsets**, not by GETting cube cells directly;
  **DELETE cellsets** you create.
- ✅ **OData discipline:** use `$select`/`$top`/`$filter`/`$expand`; element/object
  names are case-sensitive and URL-encode spaces (`Planning%20Sample`).
- ✅ **Long ops → `Prefer: respond-async`** and poll; don't block on big extracts/TI runs.
- ✅ **Tokens expire (~1h)** — refresh; never hardcode tokens/keys.
- ✅ **Writes respect TM1 security, rules, and feeders** — a write can be silently
  overridden by a rule-calculated cell.

---

## 8. Debugging playbook

| Symptom | Likely cause → fix |
|---------|--------------------|
| 302 → `/login` | Missing tenant in path. Use `/api/<tenantId>/v1/…`. |
| 401 `AUTH_REQUIRED` / `/login` | Token not accepted for PAW REST — needs the OAuth `v0userContext` flow (not a raw MCSP/service token), or session expired. |
| 404 "path not found" but authenticated | Route not available on this tenant/version (Trial gating, or PAW < 3.1.8/2.1.21), or wrong path/db name. Verify version & exact path. |
| MCSP token "Scope not found" | Wrong token endpoint. Use `…/api/2.0/apikeys/token` (no account in path). |
| TM1 call 404 on the database | Wrong `<db>` name or URL-encoding (encode spaces). `GET …/Cubes` only after the db path resolves. |
| MDX returns no cells | Suppression/zero rows, wrong element names (case-sensitive), or security. Test the MDX in PAW first. |
| Write "succeeds" but value reverts | Target cell is rule-calculated. Write to the leaf/input cell, not a consolidation or rule cell. |
| Slow/timeouts on big queries | Add `$top`/`$select`; use `Prefer: respond-async`; narrow the MDX. |
| 403 on an object | TM1 security — the user/identity lacks rights to that cube/dimension/process. |

Read the JSON `error` body (`status`, `message`, `transactionId`) — quote the
`transactionId` to IBM support. Diagnose, don't pass raw errors through.

---

## 9. References (load on demand)

| File | Contents |
|------|----------|
| [references/authentication-and-urls.md](references/authentication-and-urls.md) | MCSP token flow (validated), OAuth authorization-code, on-prem/CAM, the `/api/<tenant>/v1/…` URL map, TM1-via-PAW vs direct, trial caveats |
| [references/tm1-rest-api.md](references/tm1-rest-api.md) | TM1 OData surface: cubes/dimensions/hierarchies/elements/attributes, subsets, views, **cellsets & MDX (read + write)**, processes/chores, sandboxes, async, OData query options |
| [references/paw-content-api.md](references/paw-content-api.md) | PAW content assets: books/views/folders/websheets — list/create/update/delete by path or id, headers |
| [references/tools-tm1py-mcp.md](references/tools-tm1py-mcp.md) | TM1py SDK patterns (connect SaaS/on-prem, read/write, run TI), the MCP endpoints, the IBM Postman collection |

### Canonical external resources (you have internet access — use them)
- **TM1 REST API reference** (IBM Documentation) — the authoritative OData spec.
- **Planning Analytics on the Postman API Network** — worked request collection.
- **TM1py** — https://github.com/cubewise-code/tm1py (SDK + docs).
- **PAW REST API docs** — content endpoints, OAuth configuration.

This skill's SaaS auth + URL pattern were **validated live** against a PA SaaS
(eu-central-1) MCSP account. When a route 404s, check the PAW version and whether the
tenant (e.g. Trial) exposes that REST surface before assuming a path error.
