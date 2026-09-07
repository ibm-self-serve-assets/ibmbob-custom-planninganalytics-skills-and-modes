---
name: tm1-model-design
description: >-
  Use when designing or creating a new IBM Planning Analytics (TM1) model from
  scratch, or when reviewing and improving an existing model's architecture.
  Covers dimensional modelling principles, driver-based budget/forecast patterns,
  rules and feeder architecture decisions, TurboIntegrator process design,
  PAW book and view design, naming conventions, and implementation sequencing.
  Activate for requests like "design a TM1 model", "create a budget model",
  "how should I structure this cube", "design dimensions for", "what cubes do
  I need", "rules architecture", "feeder strategy", "TI process design",
  "PAW book design", "implementation plan for TM1", "model design document",
  "driver-based model", "rate times quantity", "planning model".
metadata:
  enabled: true
  author: IBM Bob — TM1 model design methodology
  version: 1.0.0
  disable-model-invocation: false
---

# TM1 Model Design — Methodology Skill

This skill provides the **design methodology** layer for IBM Planning Analytics (TM1)
model work. It sits above `tm1-accuracy` (which enforces technical correctness of rules,
feeders, TI syntax, and security) and complements the Planning Analytics mode's
implementation workflows.

> **Accuracy foundation:** All TM1 syntax, rules, feeders, TI code, and security
> patterns in this skill and its reference files are grounded in the `tm1-accuracy`
> skill's verified reference files. When generating any code or syntax, cross-check
> against those references. Load `tm1-accuracy` alongside this skill for full coverage.

---

## How to use this skill

### When DESIGNING a new model

1. **Classify the model type** — use the decision table in Step 1 below.
2. **Load the relevant reference files** for the topics the design covers.
3. **Follow the design methodology** for each component in order (Step 2).
4. **Apply the accuracy self-check** (Step 3) before finalising any output.
5. **Produce a design document** using the output format in Step 4.

### When REVIEWING an existing model

1. Load all reference files relevant to the model's components.
2. Run the **design quality audit** (Step 5) against each component.
3. Produce a structured findings report — do not silently correct decisions.

---

## Step 1 — Classify the model type

| Model type | Key characteristic | Primary reference files |
|---|---|---|
| **Driver-based budget / forecast** | All costs = Rate × Quantity | `02-driver-based-patterns.md`, `03-rules-and-feeder-architecture.md` |
| **Financial consolidation** | Legal/management hierarchies, inter-company elimination | `01-dimensional-modelling.md`, `03-rules-and-feeder-architecture.md` |
| **Operational planning** | Headcount, workforce, capacity, project | `01-dimensional-modelling.md`, `02-driver-based-patterns.md` |
| **Reporting / analytics only** | Read from source, no planning input | `01-dimensional-modelling.md`, `05-paw-book-and-view-design.md` |
| **ETL / data integration** | Loading from source systems, transformations | `04-ti-process-design.md` |

---

## Step 2 — Design methodology (ordered)

Work through these seven areas in sequence. Each maps to a reference file.

### 2.1 Dimensional modelling
Load [`references/01-dimensional-modelling.md`](references/01-dimensional-modelling.md).
- Determine the cube inventory (how many cubes, what each holds)
- Apply the Measures dimension pattern
- Determine dimension ordering for performance
- Design hierarchy and consolidation structure
- Identify sparse vs dense dimensions

### 2.2 Driver-based patterns (if applicable)
Load [`references/02-driver-based-patterns.md`](references/02-driver-based-patterns.md).
- Map every cost/revenue line to Rate × Quantity
- Design the Rates reference cube
- Design the Trip/Detail input cube
- Design the Summary/reporting cube
- Define the data flow: Rates → Detail → Summary

### 2.3 Rules and feeder architecture
Load [`references/03-rules-and-feeder-architecture.md`](references/03-rules-and-feeder-architecture.md).
- Identify which cells are calculated vs input
- Choose rule scope (N: leaf only, C: consolidated only, or both)
- Design feeder strategy (narrow feeders, not broad)
- Identify cross-cube DB() references
- Check: SKIPCHECK + FEEDERS order; FEEDSTRINGS if string rules exist

### 2.4 TurboIntegrator process design
Load [`references/04-ti-process-design.md`](references/04-ti-process-design.md).
- Identify all required TI processes (load rates, aggregate, clear, export)
- Apply the atomic single-process pattern for dimension/cube creation
- Assign logic to correct tabs (Prolog / Metadata / Data / Epilog)
- Define parameters and error handling

### 2.5 PAW book and view design
Load [`references/05-paw-book-and-view-design.md`](references/05-paw-book-and-view-design.md).
- Design input views (what goes on rows/columns/context)
- Design reporting views (management summary, drill-through)
- Design PAW books (tabs, page layout, navigation)
- Define cell security and write-back rules for input sheets

### 2.6 Naming conventions
Load [`references/06-naming-conventions.md`](references/06-naming-conventions.md).
- Apply consistent prefixes for cubes, dimensions, processes, views, chores
- Name consolidation members and leaf members consistently
- Name TI processes using Module.ActionName pattern

### 2.7 Implementation sequencing
Load [`references/07-implementation-sequencing.md`](references/07-implementation-sequencing.md).
- Order the build phases correctly (dimensions before cubes, cubes before rules)
- Identify dependencies between components
- Define UAT checkpoints

---

## Step 3 — Design accuracy self-check

Before finalising any design output, verify:

- [ ] Every cube has a dedicated Measures dimension (not separate cubes per metric)
- [ ] Dimension ordering follows: low-cardinality first, Measures last
- [ ] Every calculated cell has a corresponding feeder — no orphaned rules
- [ ] SKIPCHECK precedes FEEDERS; FEEDSTRINGS is first line if string rules exist
- [ ] Feeders are as narrow as the rule — no full-dimension feeders
- [ ] No TI process uses Boolean variable types (Numeric 0/1 only)
- [ ] TI tabs are correctly assigned: Prolog=setup, Metadata=dimension maintenance, Data=row processing, Epilog=teardown
- [ ] Driver-based models: Amount is **never** a manual input — always Rule-derived
- [ ] Rates cube is separate from the detail/input cube
- [ ] Security defaults are None for new objects (not Read)
- [ ] Naming conventions are applied consistently throughout

---

## Step 4 — Design document output format

Produce design documents with this structure:

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

## Step 5 — Design quality audit output format

When auditing an existing model, produce a structured report:

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

## Reference files in this skill

| File | Covers |
|------|--------|
| [`references/01-dimensional-modelling.md`](references/01-dimensional-modelling.md) | Cube inventory, Measures dimension, sparsity, dimension ordering, hierarchy design |
| [`references/02-driver-based-patterns.md`](references/02-driver-based-patterns.md) | Rate × Quantity pattern, Rates/Detail/Summary cube triad, data flow design |
| [`references/03-rules-and-feeder-architecture.md`](references/03-rules-and-feeder-architecture.md) | Rule scope decisions, feeder strategy, cross-cube DB(), SKIPCHECK/FEEDERS |
| [`references/04-ti-process-design.md`](references/04-ti-process-design.md) | Atomic process pattern, tab assignments, parameter design, error handling |
| [`references/05-paw-book-and-view-design.md`](references/05-paw-book-and-view-design.md) | Input view design, reporting view design, PAW book layout |
| [`references/06-naming-conventions.md`](references/06-naming-conventions.md) | Naming standards for all TM1 object types |
| [`references/07-implementation-sequencing.md`](references/07-implementation-sequencing.md) | Build order, dependency graph, phased roadmap template |
