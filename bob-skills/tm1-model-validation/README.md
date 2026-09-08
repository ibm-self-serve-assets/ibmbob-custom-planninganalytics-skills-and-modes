# tm1-model-validation




A Bob skill for validating a newly built or modified IBM Planning Analytics (TM1) model — either against its design document (conformance mode) or on its own structural merits (intrinsic mode). Covers dimensions, hierarchies, cube structure, rules, feeders, TurboIntegrator processes, chores, calculation correctness, views, security, and performance.

---

## Table of Contents

1. [When to use this skill](#when-to-use-this-skill)
2. [Install](#install)
3. [Requirements and scope](#requirements-and-scope)
4. [Choose a validation mode first](#choose-a-validation-mode-first)
5. [Non-negotiable rules](#non-negotiable-rules)
6. [Validation phases](#validation-phases)
7. [Findings severity](#findings-severity)
8. [Verdicts](#verdicts)
9. [Quick triage order](#quick-triage-order)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)
12. [Reference files](#reference-files)
13. [License and source](#license-and-source)

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
cp -r tm1-model-design ~/.bob/skills/
```
 Bob loads it automatically when a matching trigger phrase is detected.

To activate manually in a conversation, say:

> "Use the tm1-model-validation skill"

or reference a trigger phrase from the list above.

**Automated validation script:** The skill references `scripts/tm1_validate.py`, which requires Python 3.8+ and the `TM1py` library:

```bash
pip install TM1py
```

Configure your server connection in `scripts/conn.json` before running. See `scripts/README-spec.md` for the full `spec.json` shape.

---

## Requirements and scope

| Requirement | Detail |
|---|---|
| **IBM Bob** | Any version with skills support |
| **IBM Planning Analytics** | PA v11 (on-prem/TM1 Server) or PA v12/PAaaS — validation paths differ between the two |
| **Live TM1 server connection** | Required for all live checks (Phase 1 and Phase 2) — MCP tools or REST API via TM1py |
| **Python 3.8+** | Required for `scripts/tm1_validate.py` (automated sweep) |
| **TM1py** | `pip install TM1py` — used by the validation script |
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
| Log access | Filesystem (`tm1server.log`, `TM1ProcessError_*.log`) | REST API only |
| Feeder trace | Architect UI | `check_cell_feeders` via REST |
| Architect | Available | Not available |

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

## Examples

### Example 1 — Post-build conformance validation

**Scenario:** An agent has just built a transport budget model. A design document exists.

**Prompt:**
> "Validate the transport budget model against the design document."

**What the skill does:**
1. Runs Phase 0 — establishes PA version, access route, model scope, and baseline
2. Runs conformance sweep: `tm1_validate.py --mode conformance --spec spec.json --out report/`
3. Runs judgment checks (Phases 1–2): silent rule override test, feeder check, independent recalculation
4. Produces a structured report

**Sample finding:**
```
FINDING 1 — MAJOR
Gate:      5 (Feeder completeness)
Severity:  MAJOR
Object:    Transport_Summary cube
Expected:  [Organisation].[Total] consolidation populates from leaf feeders (design doc §5.3)
Observed:  Consolidation returns 0; check_cell_feeders returns empty set for
           ([Total Org], [Fuel Cost], [Jan], [Budget], [Amount])
Command:   check_cell_feeders cube=Transport_Summary tuple=([Total Org],[Fuel Cost],[Jan],[Budget],[Amount])
```

---

### Example 2 — Intrinsic validation with no design document

**Scenario:** A model was handed over with no design document. You need to assess whether it is internally consistent.

**Prompt:**
> "Validate this model — we have no design document."

**What the skill does:**
1. Selects intrinsic mode automatically
2. Runs: `tm1_validate.py --mode intrinsic --spec conn.json --out report/`
3. Checks consolidation-equals-sum-of-children, rule/feeder pairing, process hygiene, naming consistency
4. Issues a verdict of **NO DEFECTS DETECTED — intent not assessed** or **DEFECTS FOUND**

**Key reminder from the report:**
```
VERDICT: NO DEFECTS DETECTED — INTENT NOT ASSESSED
NOT ASSESSED: Whether the model computes the correct business logic. Intrinsic
mode cannot evaluate intent. A conformance run against a design document is
required for a full sign-off.
NOT_VERIFIED checks: 3 (feeder trace unavailable on PAaaS — Architect not present)
```

---

### Example 3 — Comparing two models built by different agents

**Scenario:** Two Bob agents built the same model independently. You need to compare them objectively.

**Prompt:**
> "Compare these two TM1 models built by different agents."

**What the skill does:**
1. Runs intrinsic mode against each model with **identical settings**
2. Compares defect counts by gate and severity (not raw totals)
3. Normalises per cube and per rule statement to avoid rewarding the thinner model
4. Produces a side-by-side comparison report — does not issue sign-offs for either

**Sample comparison table:**
| Gate | Model A defects | Model B defects | Notes |
|---|---|---|---|
| 14 — Consolidation sum | 0 | 2 | Model B has 2 missing feeders |
| 15 — Rule/feeder pairing | 1 | 0 | Model A has 1 orphaned rule |
| 16 — Process hygiene | 0 | 1 | Model B has a hardcoded file path |

---

## Troubleshooting

### The automated sweep script can't connect to the server

1. Verify `conn.json` has the correct host, port, and credentials.
2. Confirm TM1py is installed: `pip show TM1py`
3. For PAaaS, ensure you are using the REST endpoint (port 443 with SSL), not the legacy TM1 port.
4. Check that your user has at least Read access to the target cubes and dimensions.

### A consolidation returns zero but the feeder check shows feeders are present

This is the silent rule override pattern (gate 3/4). The rule may be overwriting the consolidated value with zero. Write a known non-zero value to a leaf, re-read the parent, and confirm the rule is not targeting the same intersection.

### The validation script reports `NOT_VERIFIED` for feeder trace checks on PAaaS

Architect-based feeder tracing is not available on PA v12/PAaaS. Use `check_cell_feeders` via the REST API instead. If MCP tools are available in the session, ask Bob to run `check_cell_feeders` directly for specific intersections.

### A finding references an unexpected object not in the design document

This is itself a finding (`unexpected object`) — it means the build created objects outside the agreed scope. Record it as a MAJOR finding and investigate whether those objects are orphaned, left over from a prior build, or indicate scope creep.

### The verdict is SIGN-OFF WITH CONDITIONS — what does that mean?

The model passes all BLOCKER and MAJOR gates but has open MINOR findings or a non-trivial `NOT_VERIFIED` count. The conditions must be documented explicitly in the report. A follow-up validation run is required after the MINOR findings are addressed.

### Rules errors appear in the message log but the rules file looks correct

1. Confirm `FEEDSTRINGS` is the **first line** if any rule produces string values
2. Confirm `SKIPCHECK` precedes `FEEDERS`
3. Check for invisible characters or encoding issues in the rules file (common when copy-pasted from a document)
4. Verify the rule area statement targets a valid intersection — an invalid member reference causes a silent compile failure

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

---

## License and source

This skill is part of the **IBM Bob** skill library for IBM Planning Analytics.

- **Source:** `.bob/skills/tm1-model-validation/SKILL.md` in this workspace
- **Documentation basis:** [IBM Planning Analytics documentation](https://www.ibm.com/docs/en/planning-analytics/latest) (public, `ibm.com/docs`)
- **License:** For internal IBM use. No warranty is provided for use outside of IBM Bob sessions.
- **Related skills:** [`tm1-accuracy`](../tm1-accuracy/README.md) · [`tm1-model-design`](../tm1-model-design/README.md)
