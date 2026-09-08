# IBM Planning Analytics (TM1 + PAW) — Agent Skill

Equip any skills-compatible Bob AI agent to automate **IBM Planning Analytics** — the **TM1** OLAP engine and **Planning Analytics Workspace (PAW)** — through their REST APIs.

> Built from the IBM PA/TM1 REST docs and the PAW REST API docs, and **validated
> live** against a Planning Analytics SaaS (eu-central-1) MCSP account.

## What it covers

| Area | Topics |
|------|--------|
| **Auth & URLs** | MCSP API-key→token (SaaS), OAuth authorization-code (`v0userContext`), on-prem/CAM, the `/api/<tenant>/v1/…` pattern |
| **TM1 REST API** | Cubes, dimensions, hierarchies, elements, attributes, subsets, views; **read/write data via MDX cellsets**; processes (TI) & chores; sandboxes; async; OData query options |
| **PAW content API** | Books, views, folders, websheets — list/create/update/delete by path or id |
| **MCP & tooling** | PAW MCP endpoints, the **TM1py** Python SDK, the IBM Postman collection |

## Why it's reliable

- **Auth is validated, with the real gotchas.** MCSP API-key→token verified
  (`account-iam.platform.saas.ibm.com/api/2.0/apikeys/token`, no account in path);
  the **tenant goes in the path** `/api/<tenantId>/v1/…` (the gateway 302-redirects to
  prove it); PAW content/TM1 REST is documented to need **interactive OAuth**
  (`v0userContext`) + PAW 3.1.8+/2.1.21+, and **Trial tenants 404 the v1 routes**
  (verified).
- **Data the TM1 way.** Reads/writes go through **MDX cellsets** (create → read/patch
  → delete), not direct cell GETs — the #1 thing newcomers get wrong.
- **OData discipline + async** for big metadata and long TI/extract operations.
- **Points to TM1py** so Python users skip the cellset boilerplate.

## Install

```bash
cp -r ibm-planning-analytics ~/.bob/skills/
# Python automation (optional): pip install tm1py
```

## Structure

```
ibm-planning-analytics/
├── SKILL.md                              # the skill — 9 sections
├── README.md                             # this listing
├── VALIDATION-REPORT.md                  # live SaaS validation results
└── references/
    ├── authentication-and-urls.md         # MCSP/OAuth/on-prem + URL map (validated)
    ├── tm1-rest-api.md                    # the OData TM1 surface (cellsets/MDX/TI/…)
    ├── paw-content-api.md                 # PAW content assets
    └── tools-tm1py-mcp.md                 # TM1py, MCP endpoints, Postman
```

## Requirements / scope
- A Planning Analytics environment: SaaS (MCSP API key + tenant id), or PAW
  3.1.8+/2.1.21+ with an OAuth client for the content/TM1 REST API, or a TM1 server
  reachable directly (on-prem / TM1py).
- Note: **Trial** SaaS tenants gate the REST surface and disallow modeling.

## License / source
Adapted from IBM Planning Analytics / TM1 REST API documentation and the PAW REST API
docs; TM1py is an external open-source SDK (cubewise-code).
