# TurboIntegrator Process Design — TM1 Design Reference

> **Accuracy foundation:** TI tab names, variable types, DataSourceType values,
> and error handling functions are verified in
> `tm1-accuracy/references/ti-processes.md`. The Planning Analytics mode's
> `3_workflows.xml` provides the atomic single-process pattern for cube/dimension
> creation. Cross-check all TI code against both.

---

## 1. The four tabs — responsibilities

A TurboIntegrator process has **exactly four tabs**. Assign logic correctly:

| Tab | Runs | Purpose — what belongs here |
|-----|------|------------------------------|
| **Prolog** | Once, before data source | Parameter validation, dimension/cube creation, element insertion, clearing data, locking objects, setting variables |
| **Metadata** | Once per data source record | Dimension maintenance only — creating/updating elements, hierarchies, attributes from the data source |
| **Data** | Once per data source record | Data loading only — writing values to cubes from the data source |
| **Epilog** | Once, after all records | Logging, unlocking objects, executing chained processes, sending notifications, final validation |

**Critical rule:** Do not mix concerns across tabs. Cube writes in Metadata or dimension
maintenance in Data causes hard-to-debug issues in production.

---

## 2. Process inventory for a driver-based model

Design these processes for every driver-based planning model:

| Process name | Tab used | Purpose |
|---|---|---|
| `[Module].BuildModel` | Prolog | Create all dimensions, insert all elements, create cubes (one-time setup) |
| `[Module].LoadRates` | Prolog + Data | Load/refresh rates from CSV into the Rates cube |
| `[Module].DefaultRatesToTrips` | Epilog | Copy rates from Rates cube into Trip Detail cube (budget cycle kickoff) |
| `[Module].ClearTripData` | Prolog | Clear trip data for a given version, month, department |
| `[Module].AggregateSummary` | Epilog | (Optional) Populate Summary cube from Trip Detail |
| `[Module].ExportBudget` | Prolog + Epilog | Export monthly budget to CSV for downstream systems |

---

## 3. Atomic single-process pattern for model build

When creating dimensions and cubes programmatically, **combine all steps in one
process**. Never split dimension creation and data loading into separate processes —
missing elements cause "Invalid key" errors.

### Prolog structure (correct order)

```
# 1. Create dimensions (check existence first)
IF(DimensionExists('Travel Route') = 0);
    DimensionCreate('Travel Route');
ENDIF;

# 2. Clean slate — faster than delete/recreate
DimensionDeleteAllElements('Travel Route');

# 3. Insert all elements (parent before child for C-type elements)
DimensionElementInsert('Travel Route', '', 'All Routes', 'C');
DimensionElementInsert('Travel Route', 'All Routes', 'From Sydney', 'C');
DimensionElementInsert('Travel Route', 'From Sydney', 'SYD - MEL', 'N');
DimensionElementInsert('Travel Route', 'From Sydney', 'SYD - BNE', 'N');
# ... all routes ...

# 4. Set attributes
AttrInsert('Travel Route', '', 'OriginCity', 'S');
AttrPutS('Sydney', 'Travel Route', 'SYD - MEL', 'OriginCity');

# 5. Create cube (dimensions must already exist)
IF(CubeExists('Travel Budget - Trip Detail') = 0);
    CubeCreate('Travel Budget - Trip Detail',
        'Travel Version',
        'Travel Department',
        'Travel Route',
        'Travel Cost Category',
        'Travel Month',
        'Travel Trip',
        'Travel Measure');
ENDIF;
```

### Epilog structure (data loading)

```
# Load fact data only after all dimensions and cubes are confirmed
CellPutN(350,
    'Travel Budget - Trip Detail',
    'Budget',           # Travel Version
    'Finance',          # Travel Department
    'SYD - MEL',        # Travel Route
    'Airfares',         # Travel Cost Category
    'Jan 2026',         # Travel Month
    'Trip 001',         # Travel Trip
    'Rate');            # Travel Measure
```

---

## 4. Rate loading process design

### `[Module].LoadRates` — design specification

**DataSourceType:** `CHARACTERDELIMITED` (CSV file)

**Parameters:**

| Name | Type | Default | Purpose |
|------|------|---------|---------|
| `pVersion` | String | `Budget` | Target version |
| `pFilePath` | String | *(required)* | Path to rates CSV file |
| `pDelimiter` | String | `,` | CSV delimiter |

**Prolog:**
```
# Validate parameters
IF(pVersion @= '');
    ProcessBreak;
ENDIF;

# Clear existing rates for the version
ViewZeroOut('Travel Budget - Rates', 'All');
```

**Data tab** (one row per rate in the CSV):
```
vRoute    = Value1;
vCategory = Value2;
vRate     = StringToNumber(Value3);

# Skip rows with missing data
IF(vRoute @= '' % vCategory @= '' % vRate = 0);
    ItemSkip;
ENDIF;

# Validate route exists
IF(DIMIX('Travel Route', vRoute) = 0);
    ItemSkip;
ENDIF;

CellPutN(vRate,
    'Travel Budget - Rates',
    vRoute,
    vCategory,
    'Rate',
    pVersion,
    'All');
```

**Epilog:**
```
ASCIIOutput('C:\logs\LoadRates.txt',
    'Rates loaded for version: ' | pVersion | ' at ' | Now(1));
```

---

## 5. Clear data process design

### `[Module].ClearTripData` — design specification

**DataSourceType:** `NULL` (no data source — Prolog only)

**Parameters:**

| Name | Type | Default | Purpose |
|------|------|---------|---------|
| `pVersion` | String | `Budget` | Version to clear |
| `pMonth` | String | `All` | Month to clear (or "All" for full year) |
| `pDepartment` | String | `All Departments` | Department to clear |

**Prolog:**
```
# Validate
IF(pVersion @= '');
    ProcessBreak;
ENDIF;

# Use SubsetCreateByMDX for targeted clearing
vSubset = 'TempClear_' | GetProcessName();

# Clear using a view scoped to the parameters
CubeClearData('Travel Budget - Trip Detail');
# Note: For production, use a targeted view clear rather than
# CubeClearData, which clears ALL data in the cube.
```

---

## 6. Variable types — only two

TM1 TI has exactly two variable types. There is no Boolean type.

| Type | Use for | Boolean workaround |
|------|---------|-------------------|
| **Numeric** | Numbers, flags, dates (stored as numbers) | Use 0/1 with IF() conditionals |
| **String** | Text values from data source or parameters | — |

```
# Boolean flag implemented as Numeric
pClearFirst = 1;   # 0 = no, 1 = yes

IF(pClearFirst = 1);
    CubeClearData('Travel Budget - Trip Detail');
ENDIF;
```

---

## 7. Error handling design

Every production-grade TI process must handle these cases:

```
# Prolog — parameter validation
IF(pVersion @= '');
    LogOutput('ERROR', 'pVersion parameter is required');
    ProcessBreak;
ENDIF;

# Data — skip invalid records (not break)
IF(DIMIX('Travel Route', vRoute) = 0);
    LogOutput('WARN', 'Route not found, skipping: ' | vRoute);
    ItemSkip;   # Continue to next record
ENDIF;

# Data — break on critical error
IF(vRate < 0);
    LogOutput('ERROR', 'Negative rate not allowed: ' | NumberToString(vRate));
    ItemBreak;  # Stop processing records, go to Epilog
ENDIF;
```

| Function | Effect |
|---|---|
| `ProcessBreak` | Terminates process with an error — use for invalid parameters |
| `ProcessQuit` | Terminates process gracefully (no error) — use for "nothing to do" |
| `ItemSkip` | Skips current record, continues to next — use for bad data rows |
| `ItemBreak` | Stops record processing, goes to Epilog — use for unrecoverable data errors |

---

## 8. Process chaining

Call one process from another using `ExecuteProcess`:

```
# In Epilog of BuildModel process — chain to rate loading
ExecuteProcess('[Module].LoadRates',
    'pVersion', 'Budget',
    'pFilePath', 'C:\data\rates.csv');
```

Arguments: process name (string), then parameter name–value pairs in sequence.

---

## 9. Process design anti-patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| Splitting dimension creation and data loading into separate processes | Missing elements when data load runs first | Use atomic single-process pattern |
| `CubeClearData` in a shared-access model | Clears ALL versions and departments, not just the target | Use a targeted view clear scoped to parameters |
| No parameter validation in Prolog | Silent failures with wrong version or path | Always validate required parameters with `ProcessBreak` |
| Cube writes in the Metadata tab | Hard to debug; Metadata is for dimension maintenance only | Move cube writes to Data or Epilog tab |
| Hardcoded file paths | Process breaks when deployed to a different server | Use a String parameter for the file path |
| No logging in Epilog | No audit trail of what ran and when | Always `ASCIIOutput` or `LogOutput` process completion |
