# TurboIntegrator Processes — Verified Reference

> **Version note:** The facts in this file were validated against **PA 2.1**.
> When this skill is used for a different version, verify against the target version's docs.
> Replace `<VERSION>` with `latest` (default) or the explicit version from the prompt.

Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=processes-turbointegrator`
Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=git-tm1-model-source-specification`
Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=variables-datasourcetype`

---

## The four tabs — always exactly four

A TurboIntegrator process has **exactly four procedure tabs**. Never describe it as
having three, two, or any other number.

| Tab | Purpose | Runs |
|-----|---------|------|
| **Prolog** | Setup logic executed before data source is read. Use for: parameter validation, locking objects, initialising variables, clearing data. | Once, at the start |
| **Metadata** | Dimension maintenance — creating/updating elements, hierarchies, attributes. Runs once per data source record. | Once per record |
| **Data** | Data loading — writing values to cubes. Runs once per data source record. | Once per record |
| **Epilog** | Teardown logic executed after all records are processed. Use for: committing transactions, sending notifications, logging, unlocking objects. | Once, at the end |

The Metadata and Data tabs are **mutually exclusive in purpose** — do not put cube writes
in Metadata or dimension maintenance in Data. This is a best practice, not an enforced
constraint, but violating it causes hard-to-debug issues in production.

---

## Variable types — only two

TM1 TurboIntegrator supports **exactly two variable types**:

| Type | Use for |
|------|---------|
| **Numeric** | Numbers, dates (stored as numeric), flags |
| **String** | Text values from data source columns |

**There is no Boolean type in TM1 TI.** Content that describes a Boolean variable type
is incorrect. Implement boolean logic using Numeric (0/1) and IF() conditionals.

---

## DataSourceType — valid values

Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=variables-datasourcetype`

```
DataSourceType = 'Type';
```

Valid types:

| Value | Data source |
|-------|------------|
| `CHARACTERDELIMITED` | Delimited text file (CSV, TSV, etc.) |
| `POSITIONDELIMITED` | Fixed-width text file |
| `VIEW` | TM1 cube view |
| `SUBSET` | TM1 dimension subset |
| `ODBC` | ODBC database connection |
| `OLEDBOLAP` | OLE DB for OLAP |
| `NULL` | No data source (Prolog-only processes) |

Any value not in this list is invalid. Do not invent types such as `REST`,
`API`, `JSON`, or `XML` — these are not native TI datasource types. Verify the
complete list against the target version's documentation.

---

## Process structure — field names (from TM1 REST API spec)

From the TM1 Source Specification (see target version's docs):

| Field | Type | Notes |
|-------|------|-------|
| `Name` | String | Required. Process name. |
| `HasSecurityAccess` | Boolean | Whether the user has security rights to run this process. |
| `Code` | String | Contains the Prolog, Metadata, Data, and Epilog procedure code. |
| `DataSource` | ProcessDataSource | The data source configuration object. |
| `Parameters` | Collection(ProcessParameter) | Process parameters. |
| `Variables` | Collection(ProcessVariable) | Variables mapped from the data source. |

---

## Error handling best practices

These are not enforced by the engine but are required for production-quality TI code:

```
# Prolog — validate parameter
IF(pYear @= '',
  ProcessBreak;
);

# Data — handle missing member
IF(DIMIX('Products', vProductName) = 0,
  ItemSkip;
);

# Epilog — log completion
ASCIIOutput('C:\logs\process_log.txt',
  'Process completed: ' | GetProcessName() | ' at ' | Now(1));
```

Key functions:
- `ProcessBreak` — terminates the process with an error
- `ProcessQuit` — terminates the process gracefully (no error)
- `ItemSkip` — skips the current data record and continues
- `ItemBreak` — stops processing records and goes to Epilog

---

## Process chaining

Call another TI process from within a TI process using `ExecuteProcess`:

```
ExecuteProcess('LoadRates', 'pYear', pYear, 'pVersion', pVersion);
```

Arguments: process name (string), then parameter name–value pairs.

---

## SaaS vs On-Prem TI function availability

> **Source:** Validated live against IBM Planning Analytics SaaS (PA Latest) on the
> `Ramya` server during the Australia Travel Budget model build (Sep 2026).
> Always probe a new server before writing a full build process (see Pre-flight
> pattern below).

### Function availability matrix

| TI Function | SaaS (PA Latest) | On-Prem | Notes |
|-------------|:-:|:-:|-------|
| `DimensionCreate` | ✅ | ✅ | |
| `DimensionDeleteAllElements` | ✅ | ✅ | |
| `DimensionElementInsert` | ✅ | ✅ | |
| `AttrInsert` | ✅ | ✅ | **Must run in a SEPARATE process** after `DimensionCreate` (see rule below) |
| `AttrPutS` / `AttrPutN` | ✅ | ✅ | **Must run in a SEPARATE process** after `DimensionCreate` |
| `CubeCreate` | ✅ | ✅ | |
| `CellPutN` / `CellPutS` | ✅ | ✅ | Target cells must be N-type (leaf). Writing to a C-type consolidation raises "Cell type is consolidated" error |
| `CellGetN` / `CellGetS` | ✅ | ✅ | |
| `TEXTOUTPUT` | ✅ | ✅ | On SaaS writes to the TM1 log/data directory; file path is relative to the TM1 data root |
| `LogOutput` | ✅ | ✅ | Use `'INFO'`, `'WARN'`, `'ERROR'` as the severity string |
| `ExecuteProcess` | ✅ | ✅ | |
| `ItemSkip` / `ItemBreak` | ✅ | ✅ | |
| `ProcessBreak` / `ProcessQuit` | ✅ | ✅ | |
| `DIMIX` | ✅ | ✅ | Returns 0 if element not found — use for validation |
| `DimensionExists` | ✅ | ✅ | Returns 1 if exists, 0 if not |
| `CubeExists` | ✅ | ✅ | Returns 1 if exists, 0 if not |
| `NumberToString` | ✅ | ✅ | |
| `StringToNumber` | ✅ | ✅ | |
| `CHAR` | ✅ | ✅ | Use `CHAR(39)` for single-quote, `CHAR(10)` for newline |
| `WHILE` / `END` | ✅ | ✅ | Loop construct; use `vI = vI + 1;` to increment |
| `IF` / `ELSEIF` / `ELSE` / `ENDIF` | ✅ | ✅ | |
| `Now` | ✅ | ✅ | Returns **Numeric** (decimal days). Cannot pipe directly to a String. Use `NumberToString(INT(Now(1)))` |
| `CubeRulesLoad` | ❌ | ✅ | Not available on SaaS. Use REST API `PATCH /api/v1/Cubes('{name}')/Rules` instead |
| `CubeUnload` | ❌ | ✅ | Not available on SaaS |
| `CubeSetAttribute` | ❌ | ✅ | Not a standard TI function. Use `AttrPutS` / `AttrPutN` for element attributes |
| `FileOutput` | ❌ | ❌ | Not a valid TM1 TI function (do not use). Use `TEXTOUTPUT` instead |
| Boolean variable type | ❌ | ❌ | Does not exist in TM1 TI. Use Numeric (0/1) |

---

### Critical SaaS rule: AttrPut requires a committed dimension

**Problem:** Calling `AttrInsert` or `AttrPutS`/`AttrPutN` on a dimension that was
just created with `DimensionCreate` in the **same process** causes:

```
Error: Element '<name>' not found in dimension '<dim>'
```

**Reason:** TM1 SaaS does not commit the dimension to the server within the same
process execution context until the process completes. `AttrPut` functions look up
the element against the committed state, not the in-progress state.

**Correct pattern — always split into two processes:**

```titanium
# Process 1: Travel.BuildModel (DataSourceType: NULL)
# Creates the dimension and its elements
DimensionCreate('Travel Route');
DimensionElementInsert('Travel Route', '', 'All Routes', 'C');
DimensionElementInsert('Travel Route', 'All Routes', 'SYD - MEL', 'N');
# ... all elements ...

# Process 2: Travel.SetRouteAttributes (DataSourceType: NULL)
# Runs AFTER Process 1 completes
AttrInsert('Travel Route', '', 'OriginCity', 'S');
AttrPutS('Sydney', 'Travel Route', 'SYD - MEL', 'OriginCity');
# ... all attribute values ...
```

**Never combine `DimensionCreate` + `AttrPut` in the same process on SaaS.**

---

### Critical SaaS rule: CellPutN requires a leaf (N-type) target

Writing to a consolidated (C-type) element raises:

```
Error: Prolog procedure line (n): Cell type is consolidated
```

**Common trap with date/period dimensions:** If your time dimension has a
consolidation (e.g. `FY2026`) as the top-level member and you pass it to `CellPutN`,
it will fail. Always target a **leaf (N-type) element**.

**Pattern for version-level rates** (rates not varying by month):
Add a dedicated leaf element `'All'` to the month dimension as a rate anchor:

```titanium
# Add once during dimension setup
DimensionElementInsert('Travel Month', '', 'All', 'N');

# Use 'All' as the month dimension value when writing rates
CellPutN(320, 'Travel Budget - Rates', 'SYD - MEL', 'Airfares', 'Rate', 'Budget', 'All');
```

---

### Critical SaaS rule: Now() is Numeric — cannot pipe to String directly

```titanium
# WRONG — syntax error on SaaS (and on-prem)
LogOutput('INFO', 'Completed at: ' | Now(1));

# CORRECT — convert to string first
LogOutput('INFO', 'Completed at: ' | NumberToString(INT(Now(1))));

# ALSO CORRECT — omit timestamp from LogOutput
LogOutput('INFO', 'Process completed successfully.');
```

---

### Applying cube rules on SaaS — REST API required

There is no TI function available on PA SaaS to load rules programmatically.
Use the TM1 REST API directly:

```bash
# PA Latest — PATCH rules onto a cube
PATCH /api/v1/Cubes('MyCube')/Rules
Content-Type: application/json
Authorization: Bearer <token>

{
  "RulesText": "SKIPCHECK;\n\n['Amount'] = N: ['Rate'] * ['Quantity'];\n\nFEEDERS;\n\n['Quantity'] => ['Amount'];\n"
}
```

Or via PAW: open the cube → Rules tab → paste rules text → Save.

---

### Pre-flight probe pattern

Run this **before writing any full build process** against an unfamiliar server.
It confirms which patterns are safe on that server in under 5 seconds.

```titanium
# Process: _Probe.ServerCapabilities  (DataSourceType: NULL)
# Delete this process after confirming results.

# Test 1: String concatenation with Now()
vTimeStr = NumberToString(INT(Now(1)));
LogOutput('INFO', 'Test 1 PASS: Now() to string = ' | vTimeStr);

# Test 2: AttrPut in same process as DimensionCreate
IF(DimensionExists('__probe__') = 1);
    DimensionDeleteAllElements('__probe__');
ELSE;
    DimensionCreate('__probe__');
ENDIF;
DimensionElementInsert('__probe__', '', 'probeElem', 'N');
AttrInsert('__probe__', '', 'probeAttr', 'S');
AttrPutS('probeVal', '__probe__', 'probeElem', 'probeAttr');
vAttrResult = AttrS('__probe__', 'probeElem', 'probeAttr');
IF(vAttrResult @= 'probeVal');
    LogOutput('INFO', 'Test 2 PASS: AttrPut in same process works on this server.');
ELSE;
    LogOutput('WARN', 'Test 2 FAIL: AttrPut requires a separate process on this server.');
ENDIF;

# Cleanup
DimensionDeleteAllElements('__probe__');
```

If Test 2 logs `FAIL`, immediately plan to split `DimensionCreate` and `AttrPut`
into separate processes for the full build.
