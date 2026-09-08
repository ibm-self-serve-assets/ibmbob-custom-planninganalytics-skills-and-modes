# Tooling — TM1py, MCP & Postman

Higher-level ways to drive Planning Analytics than raw HTTP (SKILL.md §5–§6).

## TM1py (recommended for Python)

`TM1py` (cubewise-code) is the de-facto Python SDK over the TM1 REST API. It wraps
auth, OData, cellsets/MDX, processes, subsets, views, sandboxes — far less
boilerplate than hand-rolled HTTP.

```bash
pip install tm1py
```

### Connect — on-prem / direct TM1
```python
from TM1py import TM1Service
with TM1Service(address="tm1host", port=12354, user="admin", password="…", ssl=True) as tm1:
    print(tm1.server.get_product_version())
    print(tm1.cubes.get_all_names())
```

### Connect — Planning Analytics SaaS via the PAW gateway
```python
from TM1py import TM1Service
# base_url points at the tenant TM1 path; bearer is the MCSP/OAuth token
tm1 = TM1Service(
    base_url="https://eu-central-1.planninganalytics.saas.ibm.com/api/<tenantId>/v1/tm1/<database>",
    mode="v12",                    # PA "v12"/cloud gateway style
    # auth: pass the bearer token TM1py supports (e.g. access_token=…), or IAM/CAM as configured
)
```
> SaaS connection options evolve with PA versions; check the TM1py docs for the exact
> `TM1Service` kwargs for **PAv12 / cloud** (token vs api_key vs CAM). The token comes
> from the MCSP or OAuth flow in `authentication-and-urls.md`.

### Common operations
```python
tm1.cubes.get_all_names()
tm1.dimensions.hierarchies.elements.get_element_names("Region","Region")
df = tm1.cells.execute_mdx_dataframe("SELECT … ON 0, … ON 1 FROM [Sales]")   # MDX -> pandas
tm1.cells.write("Sales", {("Sales","North","2026","Budget"): 12345})         # write cells
tm1.processes.execute_with_return("LoadActuals", pYear="2026")               # run TI
tm1.subsets.create(Subset(...)); tm1.views.create(...)
```
TM1py handles cellset create/read/**delete** for you — a big reason to prefer it.

## MCP endpoints

PAW exposes **Model Context Protocol** endpoints (`…/api/<tenant>/v1/…` MCP routes)
so an AI agent can call PA capabilities through a standard tool interface rather than
crafting REST calls. Availability depends on PAW version/feature flags — discover
what's exposed on your tenant. When present, prefer MCP tools for agent-driven
discovery/actions, falling back to the TM1/PAW REST APIs for anything not covered.

## Postman

IBM publishes a **Planning Analytics** collection on the Postman API Network with
worked TM1 + PAW requests (auth, cellsets/MDX, processes, content). Use it to
prototype a call, then translate to your client/TM1py. (Search "Planning Analytics"
on the Postman API Network.)

## Choosing an approach

| Goal | Use |
|------|-----|
| Python automation / data science | **TM1py** (MDX→pandas, write, run TI) |
| Agent-driven (Bob) discovery/actions | **MCP** endpoints when available, else TM1/PAW REST |
| Quick exploration / prototyping | **Postman** collection |
| Anything not wrapped by the above | raw **TM1 REST** (OData) — see tm1-rest-api.md |
