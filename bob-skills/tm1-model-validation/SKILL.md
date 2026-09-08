---
name: TM1 Model Validation
description: Validate a newly built or modified IBM Planning Analytics (TM1) model — either against its design document, or on its own where no design document exists. Use when a PA/TM1 model has just been created or changed and needs verification, or when comparing two models built by different agents or configurations. Checks dimensions, hierarchies, cube structure, rules, SKIPCHECK/FEEDSTRINGS, feeders, unfed cells, consolidation consistency, TurboIntegrator processes, chores, calculation correctness, views, security and performance. Triggers on "validate the model", "check the TM1 model", "is the cube built correctly", "verify the PA model", "no design document", "review this model", "unfed cells", "feeder trace", "rules error", "model handover", "post-build check", "TI process didn't load", "consolidation is zero", "compare these two models".
---

# TM1 Model Validation

Verify that a Planning Analytics model **as built on the server** is correct. This skill is for the gap between "the agent says it built the model" and "a human would sign this off".

## Connection — MCP tools first, no credentials needed

**All checks in this skill are performed through the Planning Analytics MCP server tools already configured in this session.** No connection credentials, base URL, API key, or password are needed from the user.

Use the MCP tools directly for every live server check:

| Need | MCP tool |
|---|---|
| List all cubes | `get_tm1_cubes` |
| Cube dimensions and order | `get_cube_dimensions` / `get_cube_dimensions_with_metadata` |
| Dimension members and hierarchy | `get_cube_sample_members` / `lookup_potential_members` |
| Query cell values | `execute_mdx_and_get_view` |
| Process details and code | `get_tm1_process_details` |
| All processes on server | `get_tm1_processes` |
| Process error logs | `get_tm1_server_process_execution_error_logs` |
| Server memory / metrics | `get_tm1_metrics` |
| Available servers | `get_available_tm1_servers` |

**Fallback — CI pipeline without Bob:** The script `scripts/tm1_validate.py` (TM1py over REST) may be used in automated pipelines where no MCP session is available. In that case the `connection` block in `spec.json` and the `$TM1_PASSWORD` environment variable are required. See `scripts/README-spec.md`. This is a CI-only path; do not ask the user for credentials when running interactively through Bob.

## Pick the mode first

| | **Conformance mode** | **Intrinsic mode** |
|---|---|---|
| Requires | A design document | Nothing but the server name |
| Question | Does the model match what it was supposed to be? | Is the model internally consistent and built to TM1 practice? |
| Oracle | The design document | TM1's own aggregation, plus engineering practice |
| Best verdict | SIGN-OFF | **NO DEFECTS DETECTED — intent not assessed** |

**Intrinsic mode can prove a model is broken. It cannot prove a model is right.** A model that computes `rate × distance` where the requirement said `rate × weight` passes every intrinsic check — rules compile, feeders complete, consolidations balance — and is still wrong. Intrinsic mode therefore never issues a sign-off, however clean the run, and its report states what it did not assess.

Choose intrinsic mode when there is no design document, when the document is known to be unreliable, or when **comparing two models built by different agents** — because a design document written by one arm is a biased oracle for the other. Read `references/intrinsic-checks.md` before interpreting any intrinsic result.

If a design document exists, use conformance mode and run intrinsic mode as well. They catch different things: conformance catches "not what we asked for", intrinsic catches "broken regardless of what we asked for".

## Non-negotiable rules

1. **Evidence, not inspection.** Every check is PASS / FAIL / NOT_VERIFIED. A check may only be marked PASS when you have called an MCP tool against the live server and can quote the result. Reading the design document, or re-reading the TI code you just wrote, is never evidence. When you cannot run a check, mark it `NOT_VERIFIED` and say why — never silently drop it.
2. **The design document is the oracle — where there is one.** In conformance mode, object names, dimension order, element counts and calculation logic are judged against the design doc, not against what looks reasonable; if the doc is ambiguous, record the ambiguity as a finding rather than resolving it yourself. In intrinsic mode there is no oracle for intent, so **never infer one**: do not reconstruct what the model "was probably meant to do" from its own contents and then validate against your reconstruction. That reasoning is circular and produces confident nonsense. Report only what the model contradicts about itself.
3. **Restore every test write.** Sections 3 and 7 write cell values. Read and record the existing value first, write the test value, assert, then write the original value back. Never leave test data in the model. Log every cell you touched in the report.
4. **Do not fix while validating.** Record findings; do not repair. A validation run that also edits the model cannot be trusted or repeated. Fixes are a separate pass, followed by a fresh validation run.
5. **Never mark the model "validated" with open BLOCKERs.** Report the verdict honestly.

## Phase 0 — Scope and connect

Establish, and state in the report header:

- **Server name.** Call `get_available_tm1_servers` to confirm the target server is reachable in this session and record its exact name. Everything that follows uses that server name in every MCP tool call.
- **Deployment version.** PA v11 / TM1 Server versus **PA v12 / PAaaS**. Several checks branch on this. If unknown, probe: call `get_tm1_metrics` — if it returns results the server supports the v12 Metrics API; if it fails with a 404 or not-found, treat as v11.
- **Model scope.** The exact list of cubes, dimensions, processes and chores that this build was supposed to produce, taken from the design document. Everything outside that list is out of scope; anything on the server but not in that list is itself a finding (`unexpected object`).
- **Baseline.** If a pre-build object manifest exists, diff against it so you report on what this build created, not on pre-existing model debt.

Write the scope into `spec.json` (see `scripts/README-spec.md` for the shape — omit the `connection` block when using MCP tools) so the run is repeatable.

## Phase 1 — Automated sweep via MCP tools

Work gate by gate using MCP tool calls. For each check, quote the exact tool call and the returned value as evidence.

**Conformance checks (needs design document):** object existence and naming (gates 1–2), dimension order, element counts, attribute population, rule compilation (gate 4), SKIPCHECK/FEEDSTRINGS presence and ordering, feeder breadth (gate 5), process error logs (gate 6), chore configuration (gate 11), security defaults (gate 9), cell feeder checks for the intersections in `spec.json` (gate 5), server memory (gate 10).

**Intrinsic checks (no design document needed):** all of the above except doc-gated items, plus gates 13–17: structural integrity, consolidation-equals-sum-of-children, rule/feeder pairing, process hygiene, and naming consistency.

**Useful MDX patterns for MCP checks:**

```mdx
-- Check a specific cell value (gate 7 sample)
SELECT
  { [Measure].[Measure].[Amount] } ON COLUMNS,
  { [Route].[Route].[MUM-DXB] } ON ROWS
FROM [FreightCost]
WHERE ([Period].[Period].[2026-Q1], [Version].[Version].[Budget])

-- Check consolidation equals sum of children (gate 14)
SELECT
  { [Period].[Period].[2026-Q1],
    [Period].[Period].[Jan-2026],
    [Period].[Period].[Feb-2026],
    [Period].[Period].[Mar-2026] } ON COLUMNS,
  { [Measure].[Measure].[Amount] } ON ROWS
FROM [FreightCost]
WHERE ([Route].[Route].[MUM-DXB], [Version].[Version].[Budget])
```

Pass these to `execute_mdx_and_get_view` with the server name and cube name. No credentials needed.

**CI pipeline fallback:** `scripts/tm1_validate.py --mode conformance --spec spec.json --out report/` (requires `connection` block and `$TM1_PASSWORD`). Only use this path when running outside a Bob session.

Read the emitted `findings.json` if using the script. When using MCP tools, record findings inline as you go.

## Phase 2 — Judgment checks

These need a human-shaped decision and cannot be fully automated. Work `references/checklist.md` gate by gate, in order. It is ordered by cost: structure fails fast and cheap; performance last, because a performance symptom is usually a feeder defect you will already have caught.

The three that most often hide real defects:

- **Silent rule override of input** (gate 3/4). Write to a leaf cell that a rule also targets, re-read it, and confirm the input survived. A model can pass every structural check and still be unusable because a rule quietly eats user input.
- **Undetected missing feeder** (gate 5). A consolidated cell returning zero where the design says it should carry value. Use `execute_mdx_and_get_view` to query the specific intersection; zero-suppression hiding the row is the symptom you will actually notice first.
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

Each finding carries: gate number, severity, the object, what was expected (with the design-doc reference), what was observed, and the exact MCP tool call or MDX that observed it.

End with an explicit verdict, plus the count of NOT_VERIFIED checks. A high NOT_VERIFIED count invalidates a sign-off regardless of how few failures there were.

- Conformance mode: **SIGN-OFF** / **SIGN-OFF WITH CONDITIONS** / **REJECTED**
- Intrinsic mode: **NO DEFECTS DETECTED — intent not assessed** / **DEFECTS FOUND** / **DEFECTS FOUND — REJECTED**. Never upgrade an intrinsic result to a sign-off, and always carry the "not assessed" list into the report.

### Comparing two models

Run intrinsic mode against each with **identical settings** — same sample count, tolerance and gate list — then compare defect counts by gate and severity rather than verdicts. Report object counts alongside defect counts, or normalise per cube and per rule statement: a model that built less has less surface to be wrong on, and raw defect counts will otherwise reward the thinner model. Verdicts compress away exactly the information a comparison needs.

## Quick triage when something looks wrong

Work this order — it resolves most defects in the first two steps:

1. Call `get_tm1_server_process_execution_error_logs` for any TI that ran during the build, and scan for `RULES ERROR` entries. A rules file that failed to compile makes every downstream check meaningless, so this runs first.
2. Use `execute_mdx_and_get_view` to query a consolidated cell returning zero unexpectedly — compare parent against sum of children to confirm a missing feeder.
3. Reconcile the load TI's record count (from process logs) against the source row count. A partial load looks exactly like a calculation defect.
4. Call `get_tm1_process_details` on the cube's rules — verify `FEEDSTRINGS` → `SKIPCHECK` → rules → `FEEDERS` ordering.
5. Only then look at performance via `get_tm1_metrics`. A consolidation that is slow at this stage is nearly always a missing or over-broad feeder, not a sizing problem.
