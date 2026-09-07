# Validation gates

Ordered by cost. Each item is marked:

- `[auto]` — covered by `scripts/tm1_validate.py`
- `[semi]` — script produces the evidence, you make the call
- `[human]` — requires judgment or an out-of-TM1 comparison

and, for mode:

- `[doc]` — **needs the design document.** Skipped in intrinsic mode; do not attempt to substitute a guess at intent
- unmarked — works in both modes

Record every item as PASS / FAIL / NOT_VERIFIED with the observed value.

Gates 13–17 at the end are intrinsic-only additions: they need no design document and run
in both modes.

---

## Gate 1 — Dimensions

- `[auto]` `[doc]` All dimensions in the design doc exist on the server, spelled exactly as designed
- `[auto]` `[doc]` Naming convention followed (prefix/case rules from the design doc)
- `[auto]` No duplicate element names within a dimension
- `[auto]` No orphaned elements — every N element is a child in at least one edge
- `[semi]` `[doc]` Hierarchy correct — each C element rolls up the leaves the design says it should. The script dumps parent→child edges; compare against the doc
- `[semi]` `[doc]` Top-level consolidation sums all expected children (check the child count and the weights — a `-1` weight where the doc says `+1` is a classic silent defect)
- `[auto]` Attributes defined and populated: aliases, codes, sort orders. Report population rate, not just existence — a defined-but-empty alias attribute is a FAIL
- `[human]` Alias attribute displays correctly in a PAW view

**Weights matter.** An element can be in the right place with the wrong weight and every structural check still passes. Dump edge weights explicitly.

## Gate 2 — Cube structure

- `[auto]` `[doc]` Cube exists with the correct dimension order (order, not just membership — it drives sparsity and MDX)
- `[auto]` `[doc]` Dimension count and names match the design doc
- `[auto]` Cube is not locked
- `[semi]` Sparsity is plausible. Compute `populated cells / product of dimension cardinalities`. A near-100% dense cube across high-cardinality dimensions means the design is wrong, not that the load worked well. Record the number as INFO even when it passes

## Gate 3 — Data entry and basic writes

Every check here writes. **Record the original value, restore it afterwards, and list the touched cells in the report.**

- `[semi]` Leaf-level (N:N) cells accept manual input
- `[semi]` Input persists after re-read — not immediately overwritten by a rule
- `[semi]` Consolidated (C-level) cells are read-only where they are rule-calculated

## Gate 4 — Rules

- `[auto]` Rules file compiles — no `RULES ERROR` in the message log at load
- `[auto]` `SKIPCHECK` present whenever feeders are defined
- `[auto]` `FEEDSTRINGS` is the **first line**, before `SKIPCHECK`, whenever any rule produces a string
- `[auto]` Statement ordering: `FEEDSTRINGS` → `SKIPCHECK` → rules → `FEEDERS`
- `[semi]` `[doc]` A sample N-level calculation returns the correct value at a known intersection
- `[semi]` `[doc]` A sample C-level consolidation returns the correct rollup
- `[semi]` `STET` areas consolidate using default TM1 aggregation — not returning zero
- `[semi]` `[doc]` `DB()` cross-cube lookups return the right value; test against a known rate or driver
- `[semi]` No rule silently overrides user input at a cell where input should be preserved

## Gate 5 — Feeders

- `[semi]` Rule-calculated cells are actually fed. Use `check_cell_feeders` on the specific intersection (v12 and recent v11); Architect → Rules → Feeder Trace on older v11
- `[semi]` No consolidated cell shows zero where the design says it carries a rule-derived value
- `[human]` Zero-suppression hides genuinely empty cells but does not hide fed cells that legitimately hold zero
- `[auto]` Feeder breadth heuristic — flag feeders whose source references `[]` across a whole high-cardinality dimension where a narrower scope would do. Over-broad feeders are the usual cause of memory blowup and slow consolidations

## Gate 6 — TurboIntegrator processes

- `[semi]` Process executes cleanly on first run
- `[auto]` No `TM1ProcessError_*.log` produced by a clean run
- `[human]` `[doc]` Loaded data reconciles to source — compare at least one aggregate **and** the record count against the source file line count
- `[semi]` Dimension-maintenance TIs create elements with the correct type (N/C/S) and parent assignment
- `[semi]` Parameter validation — an empty or invalid parameter produces a clean error, not a silent bad load. Test this explicitly; it is the most commonly skipped check and the most commonly regretted
- `[auto]` Prolog locks and Epilog unlocks balance — no orphaned locks after execution
- `[semi]` Process runs correctly when invoked from its chore, not only when run manually

## Gate 7 — Calculation correctness

The only gate that can catch a model that is structurally perfect and numerically wrong. Compare against something computed **outside** TM1.

- `[human]` `[doc]` At least 3 calculated values spot-checked against Excel or the source system
- `[human]` `[doc]` Driver-based: Rate × Quantity = Amount, verified for at least one route/product/period
- `[human]` `[doc]` Variance: Actual − Budget = Variance, with the sign convention confirmed against the design doc
- `[semi]` Time rollups: months sum to quarters, quarters to year
- `[semi]` Cross-cube lookups match the value stored in the source cube

## Gate 8 — Views and PAW

- `[semi]` Default views load without error
- `[human]` Zero-suppression behaves — no unexpectedly empty rows, no missing data
- `[semi]` Subset selections return the correct members
- `[semi]` MDX-based dynamic subsets re-evaluate correctly after a data change (change data, re-evaluate, confirm membership moved)
- `[human]` Drill-through navigates to the correct detail cube or source

## Gate 9 — Security

- `[semi]` Admin can read and write all cubes
- `[human]` `[doc]` A non-admin test user has exactly the intended access — can read where intended, **cannot** write where restricted. Test as that user; inspecting `}CubeSecurity` is not the same as trying it
- `[auto]` New objects default to `None` for non-admin groups until explicitly granted
- `[semi]` Cell-level security overrides apply — a restricted cell rejects a write from a non-privileged user

Any security finding is a BLOCKER by default. Downgrade only with an explicit statement from the design doc.

## Gate 10 — Performance sanity

- `[semi]` A full-model consolidation view loads in acceptable time. A severe slowdown here is a feeder defect until proven otherwise — go back to gate 5 rather than tuning
- `[auto]` Server memory after full load is within the expected range for the model size
- `[auto]` No rules firing at `C:` level without a corresponding `SKIPCHECK` (forces dense consolidation)

## Gate 11 — Chores and automation

- `[auto]` `[doc]` Chore scheduled with the correct process order and parameter values
- `[semi]` Manual chore run produces the same outcome as running the processes individually
- `[semi]` Error handling configured — a failed process does not let the chore continue loading downstream processes with bad data. Test by deliberately failing the first process

## Gate 12 — Documentation and handover

- `[semi]` `[doc]` Design doc matches what was built: cube names, dimension names, member counts. Where they diverge, the divergence is a finding — do not retro-edit the doc to match the build
- `[auto]` Each TI has a Prolog comment block stating purpose, parameters and dependencies
- `[human]` Known issues and deferred scope are recorded rather than left undocumented

---

# Intrinsic gates (13–17)

No design document needed. These run in **both** modes — in conformance mode they add
defect detection on top of conformance; in intrinsic mode they are most of the run.
See `references/intrinsic-checks.md` for what a clean result here does and does not mean.

## Gate 13 — Structural integrity

- `[auto]` No circular consolidation (a cycle is invalid under every possible design)
- `[auto]` No empty dimension
- `[auto]` No orphan dimension — every dimension is used by at least one cube
- `[auto]` No consolidation with exactly one child (almost always a dimension-build accident)
- `[auto]` No orphaned leaf elements

## Gate 14 — Consolidation consistency

**The strongest check available without a design document.**

- `[auto]` For every sampled consolidated cell that is *not* rule-derived, the cell equals
  the weighted sum of its children. TM1's own aggregation supplies the expected value, so
  no document is required
- `[auto]` Rule-derived consolidations are identified and excluded from the arithmetic
  assertion rather than being failed
- A parent reading **zero while children hold values** is the missing-feeder signature —
  raised as BLOCKER
- A parent that is non-zero but short usually means a wrong edge weight
- `[semi]` Record whether you sampled or swept. A sample that finds nothing is weaker
  evidence than a sweep that finds nothing

## Gate 15 — Rule and feeder pairing

- `[auto]` A cube with rule statements has a `FEEDERS` section (BLOCKER if absent — with
  `SKIPCHECK` those values disappear from consolidations)
- `[auto]` The `FEEDERS` section is not empty
- `[auto]` Feeder-to-rule ratio is plausible (heuristic; confirm with a cell feeder check)

## Gate 16 — Process hygiene

- `[auto]` Error handling present — `ItemReject` / `ProcessError` / `ProcessQuit` / `ItemSkip`
- `[auto]` Every parameter validated before use
- `[auto]` No hardcoded filesystem paths
- `[auto]` No embedded credentials (BLOCKER)
- `[auto]` `CubeLockOn` / `CubeLockOff` balanced
- `[auto]` Processes not referenced by any chore are surfaced for confirmation

## Gate 17 — Naming consistency

- `[auto]` Convention inferred from the model's **own** dominant name shape, then outliers
  flagged. Needs ≥3 objects of a kind; reports NOT_VERIFIED below that
- Reported as MINOR. An inferred convention is not an authority — if a design document
  exists, gate 1 `[doc]` supersedes this
