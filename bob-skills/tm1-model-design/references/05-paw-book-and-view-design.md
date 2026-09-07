# PAW Book and View Design — TM1 Design Reference

---

## 1. View types in TM1

| View type | Definition | Use for |
|---|---|---|
| **Native view** | Defined by placing dimensions on rows/columns/context using the PA Workspace UI | Standard input and reporting views — most common |
| **MDX view** | Defined by an MDX query | Complex dynamic sets, filtered subsets, developer-created views |

For planning models, prefer **native views** for input and simple reporting.
Use **MDX views** when dynamic filtering or complex member selection is required.

---

## 2. View axis design

Every view has three axis types:

| Axis | Purpose | Design rule |
|------|---------|-------------|
| **Rows** | The "what" — entities being planned | Put the dimension with the most members here (e.g., Cost Category × Measure) |
| **Columns** | The "when" — time periods | Time dimension; or Version dimension for variance views |
| **Context (page/filter)** | Fixes a specific member for all cells | All dimensions not on rows or columns go here |

**Input view design rule:** Every dimension must appear on exactly one axis.
Missing a dimension in a view causes TM1 to use the first element — silent and dangerous.

---

## 3. Standard views for a driver-based planning model

### View 1: Trip Detail Entry (input view)

**Purpose:** Budget analysts enter Quantity for each trip.

| Axis | Dimension | Members shown | Writeable? |
|------|-----------|---------------|-----------|
| Rows | Travel Cost Category | All 5 categories | — |
| Rows | Travel Measure | Rate, Quantity only *(suppress Amount)* | Rate: optional; Quantity: Yes; Amount: No |
| Columns | Travel Month | Selected month | — |
| Context | Travel Route | Selected route (e.g., SYD - MEL) | — |
| Context | Travel Trip | Selected trip (e.g., Trip 001) | — |
| Context | Travel Version | Budget | — |
| Context | Travel Department | User's department | — |

**Cell writability rules:**
- `Rate` cells: writeable only if per-trip rate override is allowed; otherwise read-only
- `Quantity` cells: writeable — this is the primary input
- `Amount` cells: **always read-only** — rule-calculated; suppress from input view or protect via cell security

**Zero suppression:** Enable on rows — suppress Cost Category rows where both Rate and Quantity are zero (empty trips).

---

### View 2: Monthly Summary (reporting view)

**Purpose:** Management reporting — monthly travel budget by route and cost category.

| Axis | Dimension | Members shown |
|------|-----------|---------------|
| Rows | Travel Route | Consolidations: "All Routes", "From Sydney" etc. |
| Columns | Travel Month | All 12 months + FY Total |
| Context | Travel Cost Category | "Total Travel Costs" (or drill to one category) |
| Context | Travel Measure | Amount only |
| Context | Travel Version | Budget |
| Context | Travel Department | All Departments (or selected) |

**Key design:** The Trip dimension is **not on any axis** in this view. It resolves to
"Total Trips" (the top consolidation) automatically, summing all trips.
This is how per-trip detail collapses to monthly totals — no TI process needed.

**Zero suppression:** Enable on rows — suppress routes with no budget entered.

---

### View 3: Rate Maintenance (admin view)

**Purpose:** Finance / procurement admin updates standard rates.

| Axis | Dimension | Members shown |
|------|-----------|---------------|
| Rows | Travel Route | All 56 leaf routes |
| Columns | Travel Cost Category | All 5 categories |
| Context | Travel Rate Measure | Rate |
| Context | Travel Version | Budget |
| Context | Travel Month | All (or specific period if rates vary) |

**Cell writability:** All Rate cells writeable. Restrict access to `TravelRateMaintainer`
group (see `tm1-accuracy/references/security.md` for group setup).

---

### View 4: Version Comparison (variance view)

**Purpose:** Compare Budget vs Revised Budget vs Forecast side-by-side.

| Axis | Dimension | Members shown |
|------|-----------|---------------|
| Rows | Travel Route | Consolidations |
| Rows | Travel Cost Category | "Total Travel Costs" |
| Columns | Travel Version | Budget, Revised Budget, Forecast |
| Columns | Travel Month | FY Total |
| Context | Travel Measure | Amount |
| Context | Travel Department | All |

---

## 4. PAW book design

A PAW book organises views and content into tabs that guide users through a workflow.
Design books around **user roles**, not around technical object types.

### Standard book structure for a travel budget model

```
📗 Travel Budget FY2026

Tab 1: Trip Entry
   └── View: Trip Detail Entry
       └── User selects: Route, Trip, Month via context slicers
       └── Instruction text: "Enter Quantity for each cost category"

Tab 2: Monthly Summary
   └── View: Monthly Summary (reporting)
       └── Chart: Bar chart — monthly total by cost category
       └── KPI tile: Total Budget FY2026

Tab 3: By Route
   └── View: Monthly Summary filtered to one route
       └── Map visual (if GEO dimension configured)

Tab 4: Rate Maintenance  (admin only — restrict via security)
   └── View: Rate Maintenance
       └── Instruction text: "Update rates for the new budget cycle"

Tab 5: Version Comparison
   └── View: Version Comparison
       └── Chart: Budget vs Revised Budget vs Forecast by month
```

---

## 5. Context slicer design

Context slicers (dimension selectors) let users change the dimension filter without
editing the view definition. Design rules:

- Put **Route, Trip, Department** on slicers in the Trip Entry tab — users change
  these frequently
- Put **Version** on a slicer in the Version Comparison tab
- Do **not** put Time on a slicer if the view already shows all months on columns —
  it creates confusion

---

## 6. Input protection — preventing writes to calculated cells

**Option A: PAW input cell format (recommended)**
In the PAW view, mark `Amount` cells as non-input using the "read-only" cell format.
This is the simplest approach and requires no TM1 security changes.

**Option B: Cell security cube**
Create a cell security cube for `Travel Budget - Trip Detail` and set the `Amount`
intersection to `Read` for all input groups. Use this when security must be enforced
at the server level regardless of the PAW view.

**Anti-pattern:** Relying on "nobody will type in the Amount column" — always enforce
programmatically.

---

## 7. Zero suppression guidelines

| View type | Zero suppression setting | Reason |
|---|---|---|
| Trip Entry (input) | Rows suppressed | Hide empty trips; show only trips with data or the current trip |
| Monthly Summary (reporting) | Rows suppressed | Hide routes with no budget |
| Rate Maintenance | No suppression | Admin needs to see all routes even if rate = 0 |
| Version Comparison | Rows suppressed | Hide routes with no budget in any version |

---

## 8. View naming convention

See `06-naming-conventions.md` for the full naming standard. Summary for views:

```
[Module] - [Purpose] - [Audience]
Examples:
  Travel Budget - Trip Entry - Analyst
  Travel Budget - Monthly Summary - Management
  Travel Budget - Rate Maintenance - Admin
  Travel Budget - Version Comparison - Finance
```
