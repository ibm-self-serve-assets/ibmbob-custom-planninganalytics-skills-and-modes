# TM1 REST API (OData v4)

The TM1 REST API is the workhorse for data and modeling (SKILL.md §3). It's
**OData v4**: resource collections, `$select/$filter/$expand/$top/$orderby`,
navigation properties, and bound **actions** (`tm1.Execute`, …).

Base (SaaS via PAW): `…/api/<tenant>/v1/tm1/<database>/api/v1/`
Base (direct TM1): `https://<tm1host>:<port>/api/v1/`
All examples below are relative to that base. `Accept: application/json`.

## Metadata — discover the model

```
GET Cubes?$select=Name
GET Cubes('Sales')?$expand=Dimensions($select=Name)
GET Dimensions?$select=Name
GET Dimensions('Region')/Hierarchies?$select=Name
GET Dimensions('Region')/Hierarchies('Region')/Elements?$select=Name,Type
GET Dimensions('Region')/Hierarchies('Region')/Elements?$filter=Type eq 1     # 1=Numeric,2=String,3=Consolidated
GET Dimensions('Region')/Hierarchies('Region')/Edges                          # parent/child
GET Dimensions('Time')/Hierarchies('Time')/Elements('Jan')/Attributes
GET $metadata                                                                 # full OData CSDL
```
Control objects (security, stats) are under `}…` cubes/dims, e.g. `Cubes('}ElementSecurity_Region')`.

## Read data — MDX → Cellset (the core pattern)

You do **not** GET cube cells directly; you run MDX to build a **cellset**, read it,
then delete it.

```
POST Cellsets
  body: {"MDX":"SELECT {[Account].[Sales],[Account].[Cost]} ON 0,
                 NON EMPTY [Region].Members ON 1
                 FROM [Sales] WHERE ([Time].[2026],[Version].[Actual])"}
  -> 201, returns {"ID":"<cellsetId>", …}

GET Cellsets('<cellsetId>')?$expand=
      Cube($select=Name),
      Axes($expand=Hierarchies($select=Name),Tuples($expand=Members($select=Name,UniqueName))),
      Cells($select=Ordinal,Value,FormattedValue,Updateable)

DELETE Cellsets('<cellsetId>')        # ALWAYS free it (server memory)
```
One-shot convenience action (no explicit cellset to clean up):
```
POST ExecuteMDX            body: {"MDX":"…"}            # returns a cellset inline
POST Cubes('Sales')/Views('Budget Input')/tm1.Execute  # execute a saved view
```
Cell ordinals run row-major over the axes; map `Cells[i]` to the tuple combination by
ordinal.

## Write data

**Via an update cellset:**
```
POST Cellsets   body: {"MDX":"SELECT {[Account].[Sales]} ON 0, {[Region].[North]} ON 1
                              FROM [Sales] WHERE ([Time].[2026],[Version].[Budget])"}
PATCH Cellsets('<id>')/Cells
  body: [{"Ordinal":0,"Value":12345}]            # one entry per target cell
DELETE Cellsets('<id>')
```
**Via the cube action (array of cells):**
```
POST Cubes('Sales')/tm1.Update
  body: {"Cells":[{"Tuple@odata.bind":[
            "Dimensions('Account')/Hierarchies('Account')/Elements('Sales')",
            "Dimensions('Region')/Hierarchies('Region')/Elements('North')",
            "Dimensions('Time')/Hierarchies('Time')/Elements('2026')"],
          "Value":12345}]}
```
Writes target **leaf (N) input cells** — writing to a consolidation or a
rule-calculated cell is ignored/overridden. Use a **Sandbox** for what-if (header
`TM1-Sandbox: <name>` or the `Sandboxes('<name>')` path).

## Subsets & Views

**Subset** (static or dynamic MDX):
```
POST Dimensions('Region')/Hierarchies('Region')/Subsets
  body: {"Name":"BigRegions","Elements@odata.bind":[
           "Dimensions('Region')/Hierarchies('Region')/Elements('North')"]}
# dynamic:
  body: {"Name":"AllLeaf","Expression":"{TM1FILTERBYLEVEL({TM1SUBSETALL([Region])},0)}"}
```
**View** (native or MDX) on a cube:
```
POST Cubes('Sales')/Views
  body: {"@odata.type":"#ibm.tm1.api.v1.MDXView","Name":"Q1","MDX":"SELECT … FROM [Sales]"}
GET  Cubes('Sales')/Views('Q1')/tm1.Execute?$expand=Cells($select=Value)
```

## Processes (TI) & Chores

```
GET  Processes?$select=Name
GET  Processes('LoadActuals')?$select=Name,Parameters
POST Processes('LoadActuals')/tm1.ExecuteWithReturn
     body: {"Parameters":[{"Name":"pYear","Value":"2026"},{"Name":"pMonth","Value":"Jan"}]}
   -> {"ProcessExecuteStatusCode":"CompletedSuccessfully", …}
POST Processes('LoadActuals')/tm1.Execute          # fire-and-forget variant
# ad-hoc TI without saving:
POST ExecuteProcessWithReturn   body: {"Process":{ …inline process… }}
GET  Chores?$select=Name        POST Chores('Nightly')/tm1.Execute
```

## Async (long operations)

Add header **`Prefer: respond-async`** to a POST/GET; TM1 returns `202` with a
`Location` to poll until the result is ready. Use for big MDX extracts, large TI runs,
and long metadata reads. Also cancel via the **Threads**/**Sessions** collections.

## OData query options (use them)

`$select` (only needed fields), `$top`/`$skip` (paging), `$filter`, `$orderby`,
`$count=true`, `$expand` (navigations, can nest). Keep payloads small — TM1 metadata
collections (e.g. Elements) can be huge.

## Sandboxes

```
GET  Sandboxes?$select=Name
POST Sandboxes   body:{"Name":"whatif1"}
# then send TM1-Sandbox: whatif1 on reads/writes; commit via tm1.PublishSandbox / discard via tm1.ResetSandbox
```

## Gotchas

- Names are **case-sensitive**; URL-encode spaces and special chars.
- **Always DELETE cellsets** you create.
- A `200` write that "doesn't stick" = consolidation/rule cell, security, or you
  forgot the sandbox commit.
- `}` -prefixed objects are control/system objects (security, attributes, stats).
- Element `Type`: `1`=Numeric (leaf), `2`=String, `3`=Consolidated.
