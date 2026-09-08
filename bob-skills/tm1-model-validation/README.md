# tm1-model-validation

A Bob skill for validating a newly built or modified IBM Planning Analytics (TM1) model — either against its design document (conformance mode) or on its own structural merits (intrinsic mode). Covers dimensions, hierarchies, cube structure, rules, feeders, TurboIntegrator processes, chores, calculation correctness, views, security, and performance.

**No Planning Analytics credentials are required.** All live server checks are performed through the Planning Analytics MCP server tools already configured in the Bob session.

---

## Table of Contents

1. [When to use this skill](#when-to-use-this-skill)
2. [Install](#install)
3. [Requirements and scope](#requirements-and-scope)
4. [How the skill connects to Planning Analytics](#how-the-skill-connects-to-planning-analytics)
5. [Choose a validation mode first](#choose-a-validation-mode-first)
6. [Non-negotiable rules](#non-negotiable-rules)
7. [Validation phases](#validation-phases)
8. [Findings severity](#findings-severity)
9. [Verdicts](#verdicts)
10. [Quick triage order](#quick-triage-order)
11. [Examples](#examples)
12. [Troubleshooting](#troubleshooting)
13. [Reference files](#reference-files)
14. [License and source](#license-and-source)

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

## Install

```bash
cp -r tm1-model-validation ~/.bob/skills/
```

Bob loads it automatically when a matching trigger phrase is detected.

To activate manually in a conversation, say:

> "Use the tm1-model-validation skill"

or reference a trigger phrase from the list above.

**No additional software is required for interactive use.** The skill connects to Planning Analytics through the MCP tools already in the session.

**Optional — CI pipeline script:** `scripts/tm1_validate.py` is available for automated runs in pipelines where no Bob session is present. It requires Python 3.8+ and TM1py:

```bash
pip install TM1py
```

For CI use, configure a `connection` block in `spec.json` and supply the password via `$TM1_PASSWORD`. See `scripts/README-spec.md`.

---

## Requirements and scope

| Requirement | Detail |
|---|---|
| **IBM Bob** | Any version with skills support |
| **IBM Planning Analytics** | PA v11 (on-prem/TM1 Server) or PA v12/PAaaS — validation paths differ between the two |
| **Planning Analytics MCP tools** | Required for all live checks in an interactive Bob session — no credentials needed from the user |
| **Python 3.8+ and TM1py** | Optional — only required for `scripts/tm1_validate.py` in CI pipelines without Bob |
| **Design document** | Required for conformance mode; not required for intrinsic mode |

**In scope:**
- Dimension existence, element types, element counts, orphaned/duplicate elements
- Cube structure: dimension order, attribute population, rule compilation
- Rules file: `SKIPCHECK` / `FEEDERS` / `FEEDSTRINGS` ordering, feeder breadth
- TurboIntegrator processes: error handling, parameter validation, hardcoded paths, credentials
- Consolidation correctness: consolidation = sum of children
- Cell-level calculation accuracy: spot-check against external reference
- Security defaults per object type
- Performance indicators: sparsity, memory footprint

**Out of scope:**
- Model architecture design (use `tm1-model-design`)
- Syntax generation or content creation (use `tm1-accuracy`)
- Non-TM1 planning models or external data sources

**PA version differences:**

| Feature | PA v11 / TM1 Server | PA v12 / PAaaS |
|---|---|---|
| Log access | Filesystem (`tm1server.log`, `TM1ProcessError_*.log`) | REST API only — use `get_tm1_server_process_execution_error_logs` |
| Feeder trace | Architect UI | Query parent vs children via `execute_mdx_and_get_view` |
| Server metrics | Not available via Metrics API | `get_tm1_metrics` (v12.5.0+) |

---


## Choose a validation mode first

| | **Conformance mode** | **Intrinsic mode** |
|---|---|---|
| Requires | A design document | Nothing but the server name |
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

1. **Evidence, not inspection.** Every check is `PASS` / `FAIL` / `NOT_VERIFIED`. A check may only be marked PASS when you have called an MCP tool against the live server and can quote the result. Reading code you just wrote is never evidence.
2. **Design document is the oracle.** In conformance mode, object names, dimension order, element counts, and calculation logic are judged against the design doc — not against what looks reasonable.
3. **Restore every test write.** Sections that write cell values must read the existing value first, write the test value, assert, then write the original value back. Log every cell touched in the report.
4. **Do not fix while validating.** Record findings; do not repair. A validation run that also edits the model cannot be trusted or repeated.
5. **Never mark a model validated with open BLOCKERs.**

---

## Validation phases

### Phase 0 — Scope and connect

Establish and state in the report header:

- **Server name** — call `get_available_tm1_servers` to confirm the target server is reachable and record its exact name
- **Deployment version** — PA v11/TM1 Server vs PA v12/PAaaS. Probe by calling `get_tm1_metrics` — a result confirms v12 Metrics API support; a 404 indicates v11
- **Model scope** — exact list of cubes, dimensions, processes, and chores the build was supposed to produce, taken from the design document
- **Baseline** — diff against a pre-build manifest so the report covers only what this build created

Write the scope into `spec.json` (omit the `connection` block when using MCP tools) so the run is repeatable.

### Phase 1 — Automated sweep via MCP tools

Work gate by gate using MCP tool calls. For each check, quote the exact tool call and the returned value as evidence.

**Conformance checks (needs design document):** object existence and naming, dimension order, element counts, attribute population, rule compilation, SKIPCHECK/FEEDSTRINGS ordering, feeder breadth, process error logs, chore configuration, security defaults, cell feeder checks for `sample_cells` in `spec.json`, server memory.

**Intrinsic checks (no design document needed):** all of the above except doc-gated items, plus gates 13–17: structural integrity, consolidation-equals-sum-of-children, rule/feeder pairing, process hygiene, naming consistency.

> Gate 14 (consolidation = sum of children) earns its keep — a parent returning zero while its children hold values is a missing feeder, caught with no design document at all. Use `execute_mdx_and_get_view` to pull the parent and all direct children in a single MDX query and compare.

**CI pipeline fallback:** `scripts/tm1_validate.py --mode conformance --spec spec.json --out report/` — only when running outside a Bob session with the `connection` block and `$TM1_PASSWORD` configured.

### Phase 2 — Judgment checks

Three checks that most often hide real defects:

1. **Silent rule override of input** — write to a leaf cell that a rule also targets, re-read it, confirm the input survived
2. **Undetected missing feeder** — a consolidated cell returning zero where the design says it should carry value; use `execute_mdx_and_get_view` to compare the consolidated cell against its children
3. **Independent recalculation** — spot-check at least three calculated values against a source computed *outside* TM1 (Excel, source system, or hand calculation); retrieve values via `execute_mdx_and_get_view`

---

## Findings severity

| Severity | Meaning |
|---|---|
| **BLOCKER** | Model produces wrong numbers, loses user input, or exposes data to the wrong users. No sign-off. |
| **MAJOR** | Design document not met, or a defect that will surface under normal use (missing feeder, unhandled TI error path). |
| **MINOR** | Convention, documentation, or maintainability gap. Does not affect correctness. |
| **INFO** | Observation worth recording — sparsity, memory footprint, deferred scope. |

Each finding carries: gate number, severity, the object, what was expected (with design-doc reference), what was observed, and the exact MCP tool call or MDX used to observe it.

---

## Verdicts

| Mode | Possible verdicts |
|---|---|
| Conformance | `SIGN-OFF` / `SIGN-OFF WITH CONDITIONS` / `REJECTED` |
| Intrinsic | `NO DEFECTS DETECTED — intent not assessed` / `DEFECTS FOUND` / `DEFECTS FOUND — REJECTED` |

A high `NOT_VERIFIED` count invalidates a sign-off regardless of how few failures there were. Never upgrade an intrinsic result to a sign-off.

### Comparing two models

Run intrinsic mode against each with **identical settings** — same sample count, tolerance, gate list, and MCP tool calls. Compare defect counts by gate and severity, not raw totals. Normalise per cube and per rule statement to avoid rewarding the thinner model.

---

## Quick triage order

When something looks wrong, work in this order:

1. Call `get_tm1_server_process_execution_error_logs` for any TI that ran during the build and scan for `RULES ERROR` — a rules file that failed to compile makes every downstream check meaningless
2. Use `execute_mdx_and_get_view` to query a consolidated cell returning zero unexpectedly — compare parent against the sum of children to confirm a missing feeder
3. Reconcile the load TI's record count (from process logs) against the source row count — a partial load looks exactly like a calculation defect
4. Call `get_tm1_process_details` on the cube's rules and verify `FEEDSTRINGS` → `SKIPCHECK` → rules → `FEEDERS` ordering
5. Only then investigate performance via `get_tm1_metrics` — slow consolidation is almost always a missing or over-broad feeder

---

## Examples

### Example 1 — Post-build conformance validation

**Scenario:** An agent has just built a transport budget model. A design document exists.

**Prompt:**
> "Validate the transport budget model against the design document."

**What the skill does:**
1. Calls `get_available_tm1_servers` to confirm the server, then `get_tm1_cubes` to list all cubes
2. Checks each cube and dimension in the design doc using `get_cube_dimensions_with_metadata`
3. Runs judgment checks (Phase 2): silent rule override test, feeder check via `execute_mdx_and_get_view`, independent recalculation
4. Produces a structured report using `references/report-template.md`

**Sample finding:**
```
FINDING 1 — MAJOR
Gate:      5 (Feeder completeness)
Severity:  MAJOR
Object:    Transport_Summary cube
Expected:  [Organisation].[Total] consolidation populates from leaf feeders (design doc §5.3)
Observed:  Parent cell returns 0; children [Jan], [Feb], [Mar] each hold non-zero values
Evidence:  execute_mdx_and_get_view — SELECT {[Org].[Total],[Org].[East],[Org].[West]}
           ON COLUMNS FROM [Transport_Summary]
           WHERE ([Measure].[Fuel Cost],[Period].[Jan],[Version].[Budget])
           Result: Total=0, East=12400, West=8900
```

---

### Example 2 — Intrinsic validation with no design document

**Scenario:** A model was handed over with no design document. You need to assess whether it is internally consistent.

**Prompt:**
> "Validate this model — we have no design document."

**What the skill does:**
1. Calls `get_available_tm1_servers` then `get_tm1_cubes` to discover the full model inventory
2. Runs consolidation-equals-sum-of-children checks via `execute_mdx_and_get_view`
3. Inspects all processes via `get_tm1_process_details` for hygiene (gate 16) and rule/feeder pairing (gate 15)
4. Issues a verdict of **NO DEFECTS DETECTED — intent not assessed** or **DEFECTS FOUND**

**Key reminder from the report:**
```
VERDICT: NO DEFECTS DETECTED — INTENT NOT ASSESSED
NOT ASSESSED: Whether the model computes the correct business logic. Intrinsic
mode cannot evaluate intent. A conformance run against a design document is
required for a full sign-off.
NOT_VERIFIED checks: 2 (cell security check requires non-admin test user)
```

---

### Example 3 — Comparing two models built by different agents

**Scenario:** Two Bob agents built the same model independently. You need to compare them objectively.

**Prompt:**
> "Compare these two TM1 models built by different agents."

**What the skill does:**
1. Runs intrinsic mode against each model using identical MCP tool calls and MDX patterns
2. Compares defect counts by gate and severity (not raw totals)
3. Normalises per cube and per rule statement to avoid rewarding the thinner model
4. Produces a side-by-side comparison — does not issue sign-offs for either

**Sample comparison table:**
| Gate | Model A defects | Model B defects | Notes |
|---|---|---|---|
| 14 — Consolidation sum | 0 | 2 | Model B has 2 missing feeders |
| 15 — Rule/feeder pairing | 1 | 0 | Model A has 1 orphaned rule |
| 16 — Process hygiene | 0 | 1 | Model B has a hardcoded file path |

---

## Troubleshooting

### The MCP tools can't reach the server

1. Confirm the server is listed: call `get_available_tm1_servers` — if the target server is not in the response, the MCP connection is not configured for it.
2. Verify the Planning Analytics MCP server is running and connected in `.bob/mcp.json`.
3. Check that your MCP session has at least Read access to the target cubes and dimensions.

### The CI script can't connect to the server

1. Verify `spec.json` has the correct `base_url` in the `connection` block.
2. Confirm `$TM1_PASSWORD` is set in the environment: `echo $TM1_PASSWORD`.
3. Confirm TM1py is installed: `pip show TM1py`.
4. For PAaaS, ensure you are using the REST endpoint (port 443 with SSL), not the legacy TM1 port.

### A consolidation returns zero but children hold values

This is the missing-feeder signature (gate 14). Run `execute_mdx_and_get_view` with the parent and all direct children in one MDX SELECT to confirm the gap. If the parent is rule-derived, check whether a rule is overwriting the consolidated value with zero (gate 3/4 — silent rule override).

### The skill reports `NOT_VERIFIED` for feeder trace checks on PAaaS

Architect-based feeder tracing is not available on PA v12/PAaaS. Use `execute_mdx_and_get_view` to compare the consolidated cell with its children — a zero parent alongside non-zero children is the definitive missing-feeder signature.

### A finding references an unexpected object not in the design document

This is itself a finding (`unexpected object`) — the build created objects outside the agreed scope. Record it as a MAJOR finding and investigate whether those objects are orphaned, left over from a prior build, or indicate scope creep.

### The verdict is SIGN-OFF WITH CONDITIONS — what does that mean?

The model passes all BLOCKER and MAJOR gates but has open MINOR findings or a non-trivial `NOT_VERIFIED` count. The conditions must be documented explicitly in the report. A follow-up validation run is required after the MINOR findings are addressed.

### Rules errors appear in the log but the rules file looks correct

1. Call `get_tm1_server_process_execution_error_logs` and read the full error text.
2. Confirm `FEEDSTRINGS` is the **first line** if any rule produces string values.
3. Confirm `SKIPCHECK` precedes `FEEDERS`.
4. Check for invisible characters or encoding issues in the rules file (common when copy-pasted from a document).
5. Verify the rule area statement targets a valid intersection — an invalid member reference causes a silent compile failure.

---

## Reference files

| File | Covers |
|---|---|
| `references/intrinsic-checks.md` | Gate definitions and interpretation guide for intrinsic mode |
| `references/checklist.md` | Full gate-by-gate checklist with the specific MCP tool call for each `[auto]` item |
| `references/rules-and-feeders.md` | Rule-file ordering requirements and failure signatures |
| `references/report-template.md` | Structured report template (includes MCP server name field) |
| `scripts/spec.example.json` | Example spec file (no `connection` block — MCP-ready) |
| `scripts/README-spec.md` | Full `spec.json` documentation for both MCP and CI pipeline usage |
| `scripts/tm1_validate.py` | CI pipeline validation script (TM1py / REST API — no MCP session needed) |

---

## License and source

This skill is part of the **IBM Bob** skill library for IBM Planning Analytics.

- **Source:** `.bob/skills/tm1-model-validation/SKILL.md` in this workspace
- **Documentation basis:** [IBM Planning Analytics documentation](https://www.ibm.com/docs/en/planning-analytics/latest) (public, `ibm.com/docs`)
- **License:** For internal IBM use. No warranty is provided for use outside of IBM Bob sessions.
- **Related skills:** [`tm1-accuracy`](../tm1-accuracy/README.md) · [`tm1-model-design`](../tm1-model-design/README.md)
