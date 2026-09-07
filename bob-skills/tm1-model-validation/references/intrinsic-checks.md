# Intrinsic mode — validating without a design document

Conformance mode asks: *does this model match what it was supposed to be?*
Intrinsic mode asks: *is this model internally consistent and built to TM1 practice?*

They are different questions, and only the first one is about correctness.

## The one thing to understand

**Intrinsic mode can prove a model is broken. It cannot prove a model is right.**

Nothing in this mode knows what the model was supposed to compute. A model that
calculates freight cost as `rate × distance` when the requirement said
`rate × weight` is internally flawless: the rules compile, the feeders are complete,
the consolidations add up, the naming is consistent. Every intrinsic check passes.
The model is wrong.

So the best available verdict is **NO DEFECTS DETECTED — intent not assessed**, and
the harness will not emit a sign-off in this mode no matter how clean the run. If
someone needs a sign-off, they need a design document, or an acceptance test written
from the original requirement.

## What still works without a document

These are defects under any intent, which is what makes them checkable.

| Gate | Check | Why it holds without a design doc |
|---|---|---|
| 13 | Circular consolidation | A cycle is invalid in every possible design |
| 13 | Empty dimension | A dimension with no elements serves no design |
| 13 | Orphan dimension (no cube uses it) | Dead weight or a forgotten cube |
| 13 | Consolidation with one child | Almost always an accident of a dimension-build TI |
| 13 | Orphaned leaf elements | An N element outside every rollup is invisible to reporting |
| 14 | **Consolidation ≠ sum of children** | TM1's own aggregation defines the expected value. Self-checking |
| 15 | Rules present, FEEDERS absent | With SKIPCHECK the calculated values vanish from consolidations |
| 15 | FEEDERS section empty | Same defect, differently spelled |
| 15 | Feeder-to-rule ratio far below 1 | Heuristic — some rule areas are probably unfed |
| 4 | Rules fail to compile | Syntax is intent-independent |
| 4 | FEEDSTRINGS / SKIPCHECK ordering | Fixed language requirement |
| 16 | No error handling in a TI | A bad row loads silently under any design |
| 16 | Parameters used without validation | Silent bad load under any design |
| 16 | Hardcoded paths, embedded credentials | Wrong in every model |
| 16 | Unbalanced CubeLockOn / CubeLockOff | Leaves orphaned locks under any design |
| 17 | Naming outliers | Convention inferred from the model's own dominant pattern |
| 9 | Non-admin grants on a fresh object | Suspicious by default; only a document can bless it |

### Gate 14 is the one that earns its keep

For a consolidated cell that is **not** rule-derived, TM1's default aggregation means
the cell must equal the weighted sum of its children. That expected value comes from
the engine, not from a document — which makes it the only real correctness check
available in this mode.

It catches the highest-damage defect class in TM1: a parent reading zero (or short)
while its children hold values is the signature of a **missing feeder**, and it is
otherwise silent — no error, no log entry, just a number that is too low. A wrong
edge weight shows up here too.

The harness samples rather than sweeping exhaustively (`intrinsic.consolidation_samples`,
default 12). Raise it when a run is cheap; a sample that finds nothing is weaker evidence
than a sweep that finds nothing, and the report should say which you ran.

## What is structurally unavailable

Do not let a clean intrinsic run stand in for these. State them explicitly in any
report or comparison:

- Whether the model computes what it was asked to compute
- Element and member counts — nothing to compare against
- Dimension **order** — every order is internally consistent; only the design says which is right
- Whether a missing object is missing, or an extra object is extra
- Sign conventions — `Actual − Budget` and `Budget − Actual` are both self-consistent
- Whether security grants are intentional
- Whether a rule's business logic is right, as opposed to syntactically valid
- Whether loaded data reconciles to a source system

Note what this implies for **unexpected objects**: in conformance mode an object absent
from the design document is a finding. In intrinsic mode it cannot be, so those checks
are suppressed rather than silently passing. Discovery builds the object list *from the
server*, which means the inventory can never disagree with itself — that is why a
discovered spec carries no expectations at all.

## Using intrinsic mode to compare two models

This is the mode to use when comparing models built by different agents or
configurations, because a design document supplied by one arm is a biased oracle for
the other.

1. Run intrinsic mode against each model with **identical settings** — same sample
   count, same tolerance, same gate list. A comparison across different settings is not
   a comparison.
2. Compare **defect counts by gate and severity**, not verdicts. Verdicts compress away
   the information you need.
3. Report the NOT_VERIFIED count per model alongside the defect count. A model whose
   APIs failed half the checks looks clean for the wrong reason.
4. Intrinsic mode measures build quality, not requirement satisfaction. To rank two
   models on whether they did the job, you still need an acceptance test written from
   the **original requirement** both arms shared — not from either arm's design document.

Defect counts alone can invert the true ranking: an arm that built less has less surface
to be wrong on. Report object counts next to defect counts, or normalise (defects per
cube, per rule statement) so a thin model does not win by omission.
