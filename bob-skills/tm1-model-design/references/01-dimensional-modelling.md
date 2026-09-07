# Dimensional Modelling — TM1 Design Reference

> **Accuracy foundation:** Element types (N/C/S), hierarchy structure, sparsity behaviour,
> and dimension ordering are verified in `tm1-accuracy/references/dimensions-and-modelling.md`.
> Cross-check any syntax or technical claims against that file.

---

## 1. Cube inventory design

### The central question: one cube or many?

| Signal | Design decision |
|--------|----------------|
| All measures share the same dimensional axes | One cube |
| Measures have fundamentally different granularity (e.g., daily actuals vs monthly budget) | Separate cubes |
| Some measures are inputs; others are calculated and never entered | Separate Input cube + Rates/Reference cube |
| Reporting needs a flat, denormalised view for performance | Separate Summary/reporting cube |
| Cell-level security requirements differ by measure | Separate cubes or cell security cube |

### Standard cube triad for planning models

```
┌─────────────────────┐     rates     ┌──────────────────┐
│  Rates / Reference  │ ──────────── ▶│  Detail / Input  │
│  cube               │  (DB() ref)   │  cube            │
│  (no user input)    │               │  (user enters    │
└─────────────────────┘               │   Quantity;      │
                                      │   Amount = rule) │
                                      └────────┬─────────┘
                                               │ TM1 consolidation
                                               ▼ (or TI aggregate)
                                      ┌──────────────────┐
                                      │  Summary /        │
                                      │  Reporting cube   │
                                      │  (read-only)      │
                                      └──────────────────┘
```

---

## 2. Measures dimension — always use one

**Rule:** Every cube must have a dedicated **Measures** dimension containing all metrics
the cube holds. Never model metrics as separate cubes unless granularity genuinely differs.

### Why

- Rules can be scoped precisely: `[Measures:'Amount'] = N: [Measures:'Rate'] * [Measures:'Quantity'];`
- Feeders can be narrow: `[Measures:'Rate'] => [Measures:'Amount'];`
- Adding a new measure = adding one element, not a new cube
- Views can toggle between measures without changing the cube

### Measures dimension design pattern

```
Travel Measure (no consolidation — all leaf)
├── Rate          ← Input (or pulled from Rates cube via rule)
├── Quantity      ← Input (manual entry)
└── Amount        ← Calculated (Rule: Rate × Quantity — never entered)
```

**Critical:** The calculated measure (`Amount`) must be protected from direct input.
Use cell security or PAW input view design to prevent users writing to it.

---

## 3. Element types — exactly three

| Type | Code | Meaning | Holds direct input? |
|------|------|---------|---------------------|
| Numeric leaf | **N** | Base data value | Yes |
| Consolidated | **C** | Aggregation of children | No — writes cascade to N children |
| String | **S** | Text value | Yes (string only) |

**Design implication:** Plan which elements are C (consolidations) before building.
Consolidation parents must be created before their children in TI code, or using the
Parent/Child pattern in `DimensionElementInsert`.

---

## 4. Hierarchy and consolidation design

### Design checklist

- [ ] Define the top-level "All" consolidation member (e.g., `All Routes`, `Total Company`)
- [ ] Define intermediate consolidation levels (e.g., `From Sydney`, `Q1 FY2026`)
- [ ] Identify leaf (N-type) members — these hold actual data
- [ ] Avoid consolidation members that are also input cells (prevents double-counting)
- [ ] Keep hierarchies balanced where possible (same depth on all branches)

### Time dimension pattern

```
FY2026                          ← C (annual total)
├── Q1 FY2026                   ← C (quarterly)
│   ├── Jan 2026                ← N (leaf — data lives here)
│   ├── Feb 2026                ← N
│   └── Mar 2026                ← N
├── Q2 FY2026 ...
├── Q3 FY2026 ...
└── Q4 FY2026 ...
```

**Tip:** Use a quarterly rollup even if you only report monthly — it costs nothing
and is very hard to add later without rebuilding the dimension.

---

## 5. Dimension ordering for performance

TM1 stores data in a multi-dimensional array. Dimension order affects how efficiently
data is scanned and consolidated. Apply this guidance:

| Position | Dimension type | Rationale |
|----------|---------------|-----------|
| Early (1st–2nd) | Low-cardinality (e.g., Version, Scenario — 3–10 members) | Partitions the data space early; reduces scan width |
| Middle | Business dimensions (e.g., Department, Route) | Normal cardinality |
| Later | High-cardinality (many members — e.g., Trip 001–200) | TM1's sparse storage handles these efficiently at the end |
| Last | **Measures** | Rules scoping and feeder targeting are most precise when Measures is last |

**Example ordering for a Travel Budget Detail cube:**
```
1. Travel Version        (3 members — low cardinality)
2. Travel Department     (20 members)
3. Travel Route          (56 members)
4. Travel Cost Category  (5 members)
5. Travel Month          (13 members incl. annual total)
6. Travel Trip           (200 members — high cardinality)
7. Travel Measure        (3 members: Rate, Quantity, Amount)
```

---

## 6. Sparsity — design implications

TM1 stores data **sparsely**: only non-zero cells consume memory. This has direct
design consequences:

| Design decision | Implication |
|----------------|-------------|
| Large Trip dimension (200 members) | Safe — unused trips cost nothing in memory |
| Rules-calculated cells only exist if fed | Must use SKIPCHECK + FEEDERS (see `03-rules-and-feeder-architecture.md`) |
| Sparse dimensions go later in dimension order | Improves consolidation scan performance |
| Empty versions (e.g., Forecast not yet entered) | Zero memory cost — include them upfront |

---

## 7. Attributes — when and what

Use attributes to store metadata about dimension members that drives display or calculation:

| Attribute type | Use case | Example |
|---|---|---|
| Alias (`A`) | Alternative display name | Route `SYD_MEL` aliased as `SYD → MEL` |
| String (`S`) | Descriptive metadata | `State`, `Region`, `Manager` |
| Numeric (`N`) | Calculated metadata, sort order | `SortOrder`, `BudgetWeight` |

**Access in rules:**
```
# String attribute
ATTRS('Travel Route', !TravelRoute, 'DestinationCity')

# Numeric attribute
ATTRN('Travel Route', !TravelRoute, 'FlightDistance')
```

---

## 8. Alternate hierarchies

PA supports multiple hierarchies within one dimension. Use sparingly — only when a
dimension genuinely has two independent rollup structures (e.g., a cost centre that
rolls up both geographically and by business unit).

**Default for most models:** one hierarchy per dimension, named the same as the dimension.
Do not add alternate hierarchies speculatively.
