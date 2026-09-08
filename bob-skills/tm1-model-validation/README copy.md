# tm1-model-validation

**Author:** IBM Bob — TM1 model validation methodology  
**Version:** 1.0.0

A Bob skill for validating a newly built or modified IBM Planning Analytics (TM1) model — either against its design document (conformance mode) or on its own structural merits (intrinsic mode). Covers dimensions, hierarchies, cube structure, rules, feeders, TurboIntegrator processes, chores, calculation correctness, views, security, and performance.

---

## When to use this skill

Activate this skill when you need to:

- **Validate a newly built model** after an agent or developer has finished construction
- **Post-build check** a model before handing it to users or UAT
- **Audit a modified model** after changes to rules, feeders, or TI processes
- **Compare two models** built by different agents or configurations
- **Triage unexpected results** — wrong numbers, zero consolidations, missing feeders, TI errors

**Trigger phrases:** `validate the model`, `check the TM1 model`, `is the cube built correctly`, `verify the PA model`, `no design document`, `review this model`, `unfed cells`, `feeder trace`, `rules error`, `model handover`, `post-build check`, `TI process didn't load`, `consolidation is zero`, `compare these two models`

---

## Choose a validation mode first

| | **Conformance mode** | **Intrinsic mode** |
|---|---|---|
| Requires | A design document | Nothing but the server connection |
| Question answered | Does the model match what it was supposed to be? | Is the model internally consistent and built to TM1 practice? |
| Oracle | The design document | TM1's own aggregation rules + engineering practice |
| Best verdict | **SIGN-OFF** | **NO DEFECTS DETECTED — intent not assessed** |

> **Intrinsic mode can prove a model is broken. It cannot prove a model is right.** A model that computes `rate × distance` where the requirement said `rate × weight` passes every intrinsic check and is still wrong. Intrinsic mode never issues a sign-off.

Use **intrinsic mode** when:
- There is no design document
- The design document is known to be unreliable
- Comparing two models built by different agents (a design document written by one arm is a biased oracle for the other)

If a design document exists, **run both modes** — conformance catches "not what we asked for", intrinsic catches "broken regardless of what we asked for".

---

## Non-negotiable rules

1. **Evidence, not inspection.** Every check is `PASS` / `FAIL` / `NOT_VERIFIED`. A check may only be marked PASS when you have run something against the live database and can quote the result. Reading code you just wrote is never evidence.
2. **Design document is the oracle.** In conformance mode, object names, dimension order, element counts, and calculation logic are judged against the design doc — not against what looks reasonable.
3. **Restore every test write.** Sections that write cell values must read the existing value first, write the test value, assert, then write the original value back. Log every cell touched in the report.
4. **Do not fix while validating.** Record findings; do not repair. A validation run that also edits the model cannot be trusted or repeated.
5. **Never mark a model validated with open BLOCKERs.**

---

## Validation phases

### Phase 0 — Scope and connect

Establish and state in the report header:

- **Deployment version** — PA v11/TM1 Server (filesystem log access, Architect available) vs PA v12/PAaaS (no filesystem; logs via REST only; feeder trace uses `check_cell_feeders`)
- **Access route** — Planning Analytics MCP tools (preferred) or `scripts/tm1_validate.py` via TM1py REST API
- **Model scope** — exact list of cubes, dimensions, processes, and chores the build was supposed to produce
- **Baseline** — diff against a pre-build manifest so the report covers only what this build created

### Phase 1 — Automated sweep

**Conformance:** `scripts/tm1_validate.py --mode conformance --spec spec.json --out report/`

Covers: object existence and naming, dimension order, element types and counts, orphaned/duplicate elements, attribute population, rule compilation, SKIPCHECK/FEEDSTRINGS presence and ordering, feeder breadth, process error logs, message-log scan, security defaults, cell feeder checks.

**Intrinsic:** `scripts/tm1_validate.py --mode intrinsic --spec conn.json --out report/`

Adds: circular consolidations, empty and orphan dimensions, single-child consolidations, **consolidation-equals-sum-of-children**, rule/feeder pairing, process hygiene (error handling, hardcoded paths, embedded credentials), naming consistency.

> Gate 14 (consolidation = sum of children) earns its keep — a parent returning zero while its children hold values is a missing feeder, caught with no design document at all.

### Phase 2 — Judgment checks

Three checks that most often hide real defects:

1. **Silent rule override of input** — write to a leaf cell that a rule also targets, re-read it, confirm the input survived
2. **Undetected missing feeder** — a consolidated cell returning zero where the design says it should carry value; use `check_cell_feeders` on the specific intersection
3. **Independent recalculation** — spot-check at least three calculated values against a source computed *outside* TM1 (Excel, source system, or hand calculation)

---

## Findings severity

| Severity | Meaning |
|---|---|
| **BLOCKER** | Model produces wrong numbers, loses user input, or exposes data to the wrong users. No sign-off. |
| **MAJOR** | Design document not met, or a defect that will surface under normal use (missing feeder, unhandled TI error path). |
| **MINOR** | Convention, documentation, or maintainability gap. Does not affect correctness. |
| **INFO** | Observation worth recording — sparsity, memory footprint, deferred scope. |

Each finding carries: gate number, severity, the object, what was expected (with design-doc reference), what was observed, and the exact command or MDX used to observe it.

---

## Verdicts

| Mode | Possible verdicts |
|---|---|
| Conformance | `SIGN-OFF` / `SIGN-OFF WITH CONDITIONS` / `REJECTED` |
| Intrinsic | `NO DEFECTS DETECTED — intent not assessed` / `DEFECTS FOUND` / `DEFECTS FOUND — REJECTED` |

A high `NOT_VERIFIED` count invalidates a sign-off regardless of how few failures there were. Never upgrade an intrinsic result to a sign-off.

### Comparing two models

Run intrinsic mode against each with **identical settings** — same sample count, tolerance, and gate list. Compare defect counts by gate and severity, not raw totals. Normalise per cube and per rule statement to avoid rewarding the thinner model.

---

## Quick triage order

When something looks wrong, work in this order:

1. Scan the message log for `RULES ERROR` and TI errors around the build timestamp
2. Run a feeder check on any consolidated cell returning zero unexpectedly
3. Reconcile the load TI's record count against the source row count (a partial load looks like a calculation defect)
4. Verify `FEEDSTRINGS` → `SKIPCHECK` → rules → `FEEDERS` ordering in the rules file
5. Only then investigate performance (slow consolidation is almost always a missing or over-broad feeder)

---

## Reference files

| File | Covers |
|---|---|
| `references/intrinsic-checks.md` | Gate definitions and interpretation guide for intrinsic mode |
| `references/checklist.md` | Full gate-by-gate judgment checklist (ordered by cost) |
| `references/rules-and-feeders.md` | Rule-file ordering requirements and failure signatures |
| `references/report-template.md` | Structured report template |
| `scripts/tm1_validate.py` | Automated validation script (TM1py / REST API) |
| `scripts/README-spec.md` | `spec.json` shape for repeatable runs |
