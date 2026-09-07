# TM1 Model Validation Report — <MODEL NAME>

**Verdict:** SIGN-OFF | SIGN-OFF WITH CONDITIONS | REJECTED

| | |
|---|---|
| Database / instance | |
| PA version | v11 / v12 |
| Design document | <title, version, date> |
| Validated by | |
| Date | |
| Access route | PA MCP tools / TM1py REST / mixed |

## Summary

| | Count |
|---|---|
| Checks run | |
| PASS | |
| FAIL — BLOCKER | |
| FAIL — MAJOR | |
| FAIL — MINOR | |
| NOT_VERIFIED | |

> A sign-off is not valid while any BLOCKER is open, nor while NOT_VERIFIED covers a gate the design document treats as material. State the reason for every NOT_VERIFIED below.

## Scope

Objects in scope, from the design document:

| Type | Name | Present | Notes |
|---|---|---|---|
| Cube | | | |
| Dimension | | | |
| Process | | | |
| Chore | | | |

Objects found on the server but **not** in the design document:

| Type | Name | Assessment |
|---|---|---|

## Findings

One row per finding. Order: BLOCKER, MAJOR, MINOR, INFO.

### F-01 — <short title>

| | |
|---|---|
| Gate | <n — name> |
| Severity | BLOCKER / MAJOR / MINOR / INFO |
| Object | |
| Expected | <what the design doc says, with section reference> |
| Observed | <the actual value returned> |
| Evidence | <exact MDX, TM1py call, or log excerpt> |
| Impact | |
| Suggested fix | <do not apply it during validation> |

## Gate results

| Gate | Result | NOT_VERIFIED items |
|---|---|---|
| 1 Dimensions | | |
| 2 Cube structure | | |
| 3 Data entry | | |
| 4 Rules | | |
| 5 Feeders | | |
| 6 TI processes | | |
| 7 Calculation correctness | | |
| 8 Views and PAW | | |
| 9 Security | | |
| 10 Performance | | |
| 11 Chores | | |
| 12 Documentation | | |

## Independent recalculation evidence

At least three values recomputed outside TM1.

| # | Intersection | TM1 value | Independent value | Source of independent value | Match |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

## Test writes performed and restored

| Cube | Intersection | Original value | Test value | Restored | Confirmed by re-read |
|---|---|---|---|---|---|

## Conditions for sign-off

If the verdict is SIGN-OFF WITH CONDITIONS, list each condition, its owner and its due date. Anything without an owner is not a condition, it is a wish.

| # | Condition | Owner | Due |
|---|---|---|---|
