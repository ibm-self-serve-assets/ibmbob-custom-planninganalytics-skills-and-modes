# tm1-model-design

**Author:** IBM Bob — TM1 model design methodology  
**Version:** 1.0.0

A Bob skill providing the **design methodology** layer for IBM Planning Analytics (TM1) model work. Covers dimensional modelling, driver-based budget/forecast patterns, rules and feeder architecture, TurboIntegrator process design, PAW book and view design, naming conventions, and implementation sequencing.

> All TM1 syntax, rules, feeders, TI code, and security patterns produced by this skill are grounded in the `tm1-accuracy` skill's verified reference files. Load `tm1-accuracy` alongside this skill for full coverage.

---

## Table of Contents

1. [When to use this skill](#when-to-use-this-skill)
2. [Install](#install)
3. [Requirements and scope](#requirements-and-scope)
4. [Model type classification](#model-type-classification)
5. [Design methodology (ordered)](#design-methodology-ordered)
6. [Design accuracy self-check](#design-accuracy-self-check)
7. [Design document output format](#design-document-output-format)
8. [Design quality audit output format](#design-quality-audit-output-format)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)
11. [Reference files](#reference-files)
12. [License and source](#license-and-source)

---

## When to use this skill

Activate this skill when you need to:

- **Design a new TM1 model** from scratch — cubes, dimensions, rules, TI processes, PAW books
- **Review an existing model's architecture** for design quality
- **Plan the implementation** of a Planning Analytics solution

**Trigger phrases:** `design a TM1 model`, `create a budget model`, `how should I structure this cube`, `design dimensions for`, `what cubes do I need`, `rules architecture`, `feeder strategy`, `TI process design`, `PAW book design`, `implementation plan for TM1`, `model design document`, `driver-based model`, `rate times quantity`, `planning model`

---

## Install

```bash
cp -r tm1-model-design ~/.bob/skills/
```
 Bob loads it automatically when a matching trigger phrase is detected.

To activate manually in a conversation, say:

> "Use the tm1-model-design skill"

or reference a trigger phrase from the list above.

**Recommended companion skill:** Load `tm1-accuracy` alongside this skill to enforce technical correctness on all generated TM1 syntax, rules, and TI code.

---

## Requirements and scope

| Requirement | Detail |
|---|---|
| **IBM Bob** | Any version with skills support |
| **IBM Planning Analytics** | PA 2.0 or later; skill is version-agnostic at the design level — version-specific syntax is enforced by `tm1-accuracy` |
| **No TM1 server connection needed** | This skill produces design documents and architecture — it does not connect to a live server |


**In scope:**
- Cube inventory design and Measures dimension pattern
- Dimension design: element types (N/C/S), hierarchies, consolidations, attributes
- Driver-based budget/forecast patterns (Rate × Quantity)
- Rules and feeder architecture decisions
- TurboIntegrator process design (tab assignment, parameter design, atomic process pattern)
- PAW book and view design (input views, reporting views, drill-through)
- Naming conventions for all TM1 object types
- Implementation sequencing and phased build planning
- Design quality audits of existing models

**Out of scope:**
- Live model execution or post-build verification (use `tm1-model-validation`)
- Syntax correctness enforcement (use `tm1-accuracy`)
- Non-TM1 planning tools or spreadsheet-based models

---

## Model type classification

| Model type | Key characteristic | Primary reference files |
|---|---|---|
| **Driver-based budget / forecast** | All costs = Rate × Quantity | `02-driver-based-patterns.md`, `03-rules-and-feeder-architecture.md` |
| **Financial consolidation** | Legal/management hierarchies, inter-company elimination | `01-dimensional-modelling.md`, `03-rules-and-feeder-architecture.md` |
| **Operational planning** | Headcount, workforce, capacity, project | `01-dimensional-modelling.md`, `02-driver-based-patterns.md` |
| **Reporting / analytics only** | Read from source, no planning input | `01-dimensional-modelling.md`, `05-paw-book-and-view-design.md` |
| **ETL / data integration** | Loading from source systems, transformations | `04-ti-process-design.md` |

---

## Design methodology (ordered)

Work through these seven areas in sequence. Each maps to a reference file.

### 1. Dimensional modelling
Determine cube inventory, apply the Measures dimension pattern, establish dimension ordering for performance, design hierarchy and consolidation structure, identify sparse vs dense dimensions.

### 2. Driver-based patterns *(if applicable)*
Map every cost/revenue line to Rate × Quantity. Design the Rates reference cube, the Trip/Detail input cube, and the Summary/reporting cube. Define the data flow: Rates → Detail → Summary.

### 3. Rules and feeder architecture
Identify which cells are calculated vs input. Choose rule scope (N:/C: or both). Design narrow feeders targeted to the specific rule area. Identify cross-cube `DB()` references. Verify SKIPCHECK + FEEDERS order and FEEDSTRINGS placement.

### 4. TurboIntegrator process design
Identify all required TI processes (load rates, aggregate, clear, export). Apply the atomic single-process pattern for dimension/cube creation. Assign logic to the correct tabs (Prolog / Metadata / Data / Epilog). Define parameters and error handling.

### 5. PAW book and view design
Design input views (rows/columns/context). Design reporting views (management summary, drill-through). Design PAW books (tabs, page layout, navigation). Define cell security and write-back rules for input sheets.

### 6. Naming conventions
Apply consistent prefixes for cubes, dimensions, processes, views, and chores. Name consolidation and leaf members consistently. Name TI processes using the `Module.ActionName` pattern.

### 7. Implementation sequencing
Order the build phases correctly (dimensions before cubes, cubes before rules). Identify dependencies between components. Define UAT checkpoints.

---

## Design accuracy self-check

Before finalising any design output, verify:

- [ ] Every cube has a dedicated Measures dimension (not separate cubes per metric)
- [ ] Dimension ordering follows: low-cardinality first, Measures last
- [ ] Every calculated cell has a corresponding feeder — no orphaned rules
- [ ] `SKIPCHECK` precedes `FEEDERS`; `FEEDSTRINGS` is first line if string rules exist
- [ ] Feeders are as narrow as the rule — no full-dimension feeders
- [ ] No TI process uses Boolean variable types (Numeric 0/1 only)
- [ ] TI tabs are correctly assigned: Prolog=setup, Metadata=dimension maintenance, Data=row processing, Epilog=teardown
- [ ] Driver-based models: Amount is **never** a manual input — always Rule-derived
- [ ] Rates cube is separate from the detail/input cube
- [ ] Security defaults are None for new objects (not Read)
- [ ] Naming conventions are applied consistently throughout

---

## Design document output format

Design documents produced by this skill follow this structure:

```
1. Model Overview
   - Purpose, scope, design principles, PA version target

2. Cube Inventory
   - Table: Cube name | Purpose | Dimensions | Has Rules? | Input/Read-only

3. Dimension Designs
   - For each dimension: element structure (tree), element types (N/C/S),
     attributes, consolidation hierarchy

4. Rate Reference Table (for driver-based models)
   - Default rates by cost category and applicable dimensions

5. Rules Architecture
   - Rule statements with correct syntax
   - Feeder design with scope justification
   - SKIPCHECK / FEEDERS / FEEDSTRINGS placement

6. TurboIntegrator Processes
   - For each process: name, purpose, parameters, tab-by-tab logic

7. Views and PAW Books
   - Input views: row/column/context assignments
   - Reporting views: management summary structure
   - PAW book layout

8. Security Design
   - Role table with access levels per cube/dimension

9. Naming Conventions
   - Applied to all objects in the design

10. Implementation Roadmap
    - Phased plan with dependencies and checkpoints
```

---

## Design quality audit output format

When auditing an existing model:

```
DESIGN FINDING [n] — [CRITICAL | WARNING | INFO]
Component: <cube / dimension / rules / TI / PAW>
Location:  <specific object name>
Issue:     <what is wrong with the design decision>
Impact:    <performance / correctness / maintainability / usability>
Recommend: <what the design should be instead>
Reference: <which reference file supports this recommendation>
```

---

## Examples

### Example 1 — Designing a driver-based budget model

**Prompt:**
> "Design a driver-based budget model for a transport company. Include headcount, fuel, and maintenance costs."

**What the skill does:**
1. Classifies as **Driver-based budget / forecast**
2. Loads `02-driver-based-patterns.md` and `03-rules-and-feeder-architecture.md`
3. Maps each cost line to Rate × Quantity (e.g. Fuel Cost = Fuel Rate × Distance)
4. Produces cube inventory, dimension designs, rules architecture, and a phased implementation roadmap

**Sample cube inventory output:**

| Cube name | Purpose | Dimensions | Has Rules? | Type |
|---|---|---|---|---|
| `Transport_Rates` | Reference rates by cost type | Cost Type, Period, Version, Organisation | No | Read-only |
| `Transport_Detail` | Input actuals and budget quantities | Route, Cost Type, Period, Version, Organisation, Measures | Yes | Input |
| `Transport_Summary` | Rolled-up reporting view | Organisation, Cost Type, Period, Version, Measures | Yes | Read-only |

---

### Example 2 — Reviewing an existing model's architecture

**Prompt:**
> "Review the architecture of our current headcount planning model."

**What the skill does:**
1. Loads all reference files relevant to the model's components
2. Runs the design quality audit against each component
3. Produces a structured findings report

**Sample finding:**
```
DESIGN FINDING 1 — WARNING
Component: Rules
Location:  Headcount_Summary cube rules file
Issue:     Feeder targets the entire [Employee] dimension, not the specific
           leaf area covered by the rule
Impact:    Performance — over-broad feeders increase memory consumption
           unnecessarily
Recommend: Restrict the feeder to the {[Employee].[Active Employees]} subset
           that the rule actually populates
Reference: references/03-rules-and-feeder-architecture.md
```

---

### Example 3 — TurboIntegrator process design for a rate loader

**Prompt:**
> "Design a TI process to load rates from a CSV file into the Transport_Rates cube."

**What the skill does:**
1. Loads `04-ti-process-design.md`
2. Applies the atomic single-process pattern
3. Assigns logic to correct tabs with parameter design

**Sample tab assignment:**
| Tab | Logic |
|---|---|
| Prolog | Set `DataSourceType`, file path, delimiter; open error handling |
| Metadata | — (no dimension changes) |
| Data | Map CSV columns to cube dimensions; call `CellPutN` for each rate value |
| Epilog | Log record count; close error handling; trigger downstream refresh if needed |

---

## Troubleshooting

### The skill designs a model but the rules syntax looks wrong

Load `tm1-accuracy` alongside this skill and ask Bob to cross-check the generated rules against the verified reference files. The design skill focuses on architecture decisions; `tm1-accuracy` enforces syntax correctness.

### The generated design document is missing a section

Confirm you specified the model type clearly. Some sections (e.g. Rate Reference Table) are only produced for driver-based models. State the model type explicitly: *"This is a driver-based budget model for..."*

### The implementation roadmap doesn't show the correct build order

Dimensions must precede cubes; cubes must precede rules; rules must precede views. If the skill produces a different order, reference `references/07-implementation-sequencing.md` and ask Bob to revise the sequencing explicitly.

### The skill is producing overly broad feeders in its examples

This is a known accuracy risk. After generation, run the self-check checklist and verify each feeder targets only the leaf-level area covered by its corresponding rule. Ask: *"Verify that all feeders in this design are as narrow as their corresponding rules."*

### Naming conventions are inconsistent across the design

Ask Bob to apply `references/06-naming-conventions.md` explicitly to the full object list: *"Apply the TM1 naming conventions from the reference file to all object names in this design."*

---

## Reference files

| File | Covers |
|---|---|
| `references/01-dimensional-modelling.md` | Cube inventory, Measures dimension, sparsity, dimension ordering, hierarchy design |
| `references/02-driver-based-patterns.md` | Rate × Quantity pattern, Rates/Detail/Summary cube triad, data flow design |
| `references/03-rules-and-feeder-architecture.md` | Rule scope decisions, feeder strategy, cross-cube `DB()`, SKIPCHECK/FEEDERS |
| `references/04-ti-process-design.md` | Atomic process pattern, tab assignments, parameter design, error handling |
| `references/05-paw-book-and-view-design.md` | Input view design, reporting view design, PAW book layout |
| `references/06-naming-conventions.md` | Naming standards for all TM1 object types |
| `references/07-implementation-sequencing.md` | Build order, dependency graph, phased roadmap template |

---

## License and source

This skill is part of the **IBM Bob** skill library for IBM Planning Analytics.

- **Source:** `.bob/skills/tm1-model-design/SKILL.md` 
- **Documentation basis:** [IBM Planning Analytics documentation](https://www.ibm.com/docs/en/planning-analytics/latest) (public, `ibm.com/docs`)
- **License:** No warranty is provided for use outside of IBM Bob sessions.
- **Related skills:** [`tm1-accuracy`](../tm1-accuracy/README.md) · [`tm1-model-validation`](../tm1-model-validation/README.md)
