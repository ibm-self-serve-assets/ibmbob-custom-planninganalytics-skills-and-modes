# Planning Analytics Workspace (PAW) Content API

Manage Workspace content — **books, views, folders, websheets** — programmatically
(SKILL.md §4). Base (SaaS): `…/api/<tenant>/v1/content/…`. ~25 content endpoints
(list/create/update/delete + metadata).

Headers: `Authorization: Bearer <token>`, `Content-Type: application/json`,
`Accept: application/json`. (The older "Content Services API" used cookie/SSO headers
`ba-sso-authenticity` + `cookie`; the current PAW REST API uses OAuth bearer tokens —
prefer the latter.)

## Assets model

Everything in PAW is an **asset** (folders, books, views, …) identified by an **id**
or addressable by **path**. The two roots are typically `shared` and a user's private
space.

## List / read

```
# list children of a folder by PATH (useful when you don't know ids):
GET .../v1/content/assets(path='shared')/assets
GET .../v1/content/assets(path='shared/Finance')/assets

# filter / expand children:
GET .../v1/content/assets(path='shared')/assets?$filter=type eq 'folder'

# by id — metadata only, then the content body:
GET .../v1/content/assets('<assetId>')
GET .../v1/content/assets('<assetId>')/content
```

## Create

```
# new folder under a path:
POST .../v1/content/assets(path='shared')/assets
  body: {"type":"folder","name":"Finance"}

# new book/dashboard at a path:
POST .../v1/content/assets(path='shared/Finance')/assets
  body: {"type":"book","name":"Q1 Review", "content": { …book spec… }}
```

## Update / delete

```
PUT    .../v1/content/assets('<assetId>')      # update metadata/content (name, body, …)
DELETE .../v1/content/assets('<assetId>')      # delete an asset
```

## Patterns

- **Resolve by path vs id:** use `assets(path='…')` to navigate when you only know the
  human path; capture the returned `id` for subsequent precise calls.
- **Folders are assets too** — manage the tree by creating/deleting folder assets.
- The initial REST release focuses on **content management**; more PAW endpoints are
  planned. Confirm availability on your PAW version (3.1.8+/2.1.21+).

## Notes / gotchas

- Tenant in the path on SaaS (`/api/<tenant>/v1/content/…`) — see authentication-and-urls.md.
- On **Trial** tenants the content `v1` routes may 404 (gated) — verified.
- For the data *inside* a view/book (cube data), use the **TM1 REST API** (cellsets/
  MDX) — the content API manages the asset, not the cube cells.
