---
name: TM1 Model Validation
description: Validate a newly built or modified IBM Planning Analytics (TM1) model — either against its design document, or on its own where no design document exists. Use when a PA/TM1 model has just been created or changed and needs verification, or when comparing two models built by different agents or configurations. Checks dimensions, hierarchies, cube structure, rules, SKIPCHECK/FEEDSTRINGS, feeders, unfed cells, consolidation consistency, TurboIntegrator processes, chores, calculation correctness, views, security and performance. Triggers on "validate the model", "check the TM1 model", "is the cube built correctly", "verify the PA model", "no design document", "review this model", "unfed cells", "feeder trace", "rules error", "model handover", "post-build check", "TI process didn't load", "consolidation is zero", "compare these two models".
---

# TM1 Model Validation

Verify that a Planning Analytics model **as built on the server** is correct. This skill is for the gap between "the agent says it built the model" and "a human would sign this off".

## Pick the mode first

| | **Conformance mode** | **Intrinsic mode** |
|---|---|---|
| Requires | A design document | Nothing but the connection |
| Question | Does the model match what it was supposed to be? | Is the model internally consistent and built to TM1 practice? |
| Oracle | The design document | TM1's own aggregation, plus engineering practice |
| Best verdict | SIGN-OFF | **NO DEFECTS DETECTED — intent not assessed** |
| Command | `--mode conformance --spec spec.json` | `--mode intrinsic` |

**Intrinsic mode can prove a model is broken. It cannot prove a model is right.** A model that computes `rate × distance` where the requirement said `rate × weight` passes every intrinsic check — rules compile, feeders complete, consolidations balance — and is still wrong. Intrinsic mode therefore never issues a sign-off, however clean the run, and its report states what it did not assess.

Choose intrinsic mode when there is no design document, when the document is known to be unreliable, or when **comparing two models built by different agents** — because a design document written by one arm is a biased oracle for the other. Read `references/intrinsic-checks.md` before interpreting any intrinsic result.

If a design document exists, use conformance mode and run intrinsic mode as well. They catch different things: conformance catches "not what we asked for", intrinsic catches "broken regardless of what we asked for".

## Non-negotiable rules

1. **Evidence, not inspection.** Every check is PASS / FAIL / NOT_VERIFIED. A check may only be marked PASS when you have run something against the live database and can quote the result. Reading the design document, or re-reading the TI code you just wrote, is never evidence. When you cannot run a check, mark it `NOT_VERIFIED` and say why — never silently drop it.
2. **The design document is the oracle — where there is one.** In conformance mode, object names, dimension order, element counts and calculation logic are judged against the design doc, not against what looks reasonable; if the doc is ambiguous, record the ambiguity as a finding rather than resolving it yourself. In intrinsic mode there is no oracle for intent, so **never infer one**: do not reconstruct what the model "was probably meant to do" from its own contents and then validate against your reconstruction. That reasoning is circular and produces confident nonsense. Report only what the model contradicts about itself.
3. **Restore every test write.** Sections 3 and 7 write cell values. Read and record the existing value first, write the test value, assert, then write the original value back. Never leave test data in the model. Log every cell you touched in the report.
4. **Do not fix while validating.** Record findings; do not repair. A validation run that also edits the model cannot be trusted or repeated. Fixes are a separate pass, followed by a fresh validation run.
5. **Never mark the model "validated" with open BLOCKERs.** Report the verdict honestly.

## Phase 0 — Scope and connect

Establish, and state in the report header:

- **Deployment version.** PA v11 / TM1 Server (filesystem access to `tm1server.log`, `TM1ProcessError_*.log`, Architect available) versus **PA v12 / PAaaS** (no filesystem; the message log is only reachable over REST, and Architect feeder trace does not exist — use `check_cell_feeders`). Several checks branch on this. If unknown, ask, or probe: attempt a message-log REST call and note which path worked.
- **Access route.** Prefer the Planning Analytics MCP tools if this session has them; fall back to `scripts/tm1_validate.py` (TM1py over the REST API). State which was used for each finding.
- **Model scope.** The exact list of cubes, dimensions, processes and chores that this build was supposed to produce, taken from the design document. Everything outside that list is out of scope; anything in the database but not in that list is itself a finding (`unexpected object`).
- **Baseline.** If a pre-build object manifest exists, diff against it so you report on what this build created, not on pre-existing model debt.

Write the scope into `spec.json` (see `scripts/README-spec.md` shape) so the run is repeatable.

## Phase 1 — Automated sweep

**Conformance:** `scripts/tm1_validate.py --mode conformance --spec spec.json --out report/`
Covers object existence and naming, dimension order, element types and counts, orphaned and duplicate elements, attribute population, rule compilation, SKIPCHECK/FEEDSTRINGS presence and ordering, feeder breadth, process error logs, message-log scan, security defaults, and cell feeder checks for the intersections you supply.

**Intrinsic:** `scripts/tm1_validate.py --mode intrinsic --spec conn.json --out report/`
Discovers the model from the server, then adds gates 13–17: structural integrity (circular consolidations, empty and orphan dimensions, single-child consolidations), **consolidation-equals-sum-of-children**, rule/feeder pairing, process hygiene (error handling, parameter validation, hardcoded paths, embedded credentials), and naming consistency inferred from the model's own dominant pattern. `--spec` here supplies only connection details; pass `intrinsic.consolidation_samples` to widen the sample.

Gate 14 is the one that earns its keep — for a cell that is not rule-derived, TM1's own aggregation supplies the expected value, so a parent reading zero while its children hold values is a missing feeder, caught with no document at all.

Read the emitted `findings.json`. Do not paraphrase it — carry the actual values into the report.

## Phase 2 — Judgment checks

These need a human-shaped decision and cannot be fully automated. Work `references/checklist.md` gate by gate, in order. It is ordered by cost: structure fails fast and cheap; performance last, because a performance symptom is usually a feeder defect you will already have caught.

The three that most often hide real defects:

- **Silent rule override of input** (gate 3/4). Write to a leaf cell that a rule also targets, re-read it, and confirm the input survived. A model can pass every structural check and still be unusable because a rule quietly eats user input.
- **Undetected missing feeder** (gate 5). A consolidated cell returning zero where the design says it should carry value. `check_cell_feeders` on the specific intersection is definitive; zero-suppression hiding the row is the symptom you will actually notice first.
- **Independent recalculation** (gate 7). Spot-check at least three calculated values against a source computed *outside* TM1 — Excel, the source system, or a hand calculation. Recomputing with the same rule that produced the number proves nothing.

`references/rules-and-feeders.md` has the rule-file ordering requirements and the specific failure signatures to match against.

## Phase 3 — Report

Use `references/report-template.md`. Severity:

| Severity | Meaning |
|---|---|
| **BLOCKER** | Model produces wrong numbers, loses user input, or exposes data to the wrong users. No sign-off. |
| **MAJOR** | Design document not met, or a defect that will surface under normal use (missing feeder, unhandled TI error path). |
| **MINOR** | Convention, documentation or maintainability gap. Does not affect correctness. |
| **INFO** | Observation worth recording — sparsity, memory footprint, deferred scope. |

Each finding carries: gate number, severity, the object, what was expected (with the design-doc reference), what was observed, and the exact command or MDX that observed it.

End with an explicit verdict, plus the count of NOT_VERIFIED checks. A high NOT_VERIFIED count invalidates a sign-off regardless of how few failures there were.

- Conformance mode: **SIGN-OFF** / **SIGN-OFF WITH CONDITIONS** / **REJECTED**
- Intrinsic mode: **NO DEFECTS DETECTED — intent not assessed** / **DEFECTS FOUND** / **DEFECTS FOUND — REJECTED**. Never upgrade an intrinsic result to a sign-off, and always carry the "not assessed" list into the report.

### Comparing two models

Run intrinsic mode against each with **identical settings** — same sample count, tolerance and gate list — then compare defect counts by gate and severity rather than verdicts. Report object counts alongside defect counts, or normalise per cube and per rule statement: a model that built less has less surface to be wrong on, and raw defect counts will otherwise reward the thinner model. Verdicts compress away exactly the information a comparison needs.

## Quick triage when something looks wrong

Work this order — it resolves most defects in the first two steps:

1. Scan the message log for `RULES ERROR` and TI errors around the build timestamp. A rules file that failed to compile makes every downstream check meaningless, so this runs first.
2. Run a feeder check on any consolidated cell returning zero unexpectedly.
3. Reconcile the load TI's record count against the source row count. A partial load looks exactly like a calculation defect.
4. Verify `FEEDSTRINGS` → `SKIPCHECK` → rules → `FEEDERS` ordering in the rules file.
5. Only then look at performance. A consolidation that is slow at this stage is nearly always a missing or over-broad feeder, not a sizing problem.
