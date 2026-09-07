# Rules and Feeder Architecture — TM1 Design Reference

> **Accuracy foundation:** All syntax in this file is verified against
> `tm1-accuracy/references/rules-and-feeders.md`. That file is the authoritative
> source for SKIPCHECK/FEEDERS order, FEEDSTRINGS placement, feeder breadth rules,
> and DB() syntax. Always cross-check generated code against it.

---

## 1. When to use rules — the design decision

Not every calculation belongs in a rules file. Apply this decision table first:

| Calculation type | Where it belongs | Reason |
|---|---|---|
| Amount = Rate × Quantity | Rules file | Real-time, always correct, no TI needed |
| Cross-cube rate lookup (DB()) | Rules file | Live reference — always current |
| Aggregating trips to monthly total | TM1 native consolidation (no rule) | Consolidation dimensions handle this automatically |
| Loading data from CSV/ERP | TurboIntegrator (not rules) | Rules are for calculation, TI is for ETL |
| Copying rates to detail cube | TurboIntegrator | Batch operation, not real-time |
| Year-to-date calculation | Rules file (C: level rule) | Dynamic — recalculates as months close |

**Guiding principle:** Rules are for calculations that must always be current. TI is for
data movement and structural changes.

---

## 2. Rule scope decisions — N:, C:, or neither?

| Qualifier | Applies to | Use when |
|---|---|---|
| `N:` | Numeric leaf cells only | Calculation is only meaningful at leaf level (e.g., Amount = Rate × Quantity per trip) |
| `C:` | Consolidated cells only | Calculation is only meaningful at an aggregation level (e.g., YTD % calculated from totals) |
| *(neither)* | Both N and C | Rule is valid at any level — rare; ensure this is intentional |

**For driver-based models, use `N:` for the Amount rule:**
```
[Travel Measure:'Amount'] = N: [Travel Measure:'Rate'] * [Travel Measure:'Quantity'];
```
This prevents the rule from firing on the "Total Trips" consolidation row, where
Rate and Quantity consolidations would produce a meaningless result.

---

## 3. Rules file structure — correct order

This order is mandatory. Any deviation causes incorrect behaviour.

```
FEEDSTRINGS;     ← Line 1 ONLY if any rule produces a string value

SKIPCHECK;       ← Always present when feeders are used

# --- Calculation rules (above FEEDERS block) ---

[Travel Measure:'Amount'] = N: [Travel Measure:'Rate'] * [Travel Measure:'Quantity'];

# --- Cross-cube rate lookup (optional) ---

[Travel Measure:'Rate'] = N:
    DB('Travel Budget - Rates',
       !Travel Route,
       !Travel Cost Category,
       'Rate',
       !Travel Version,
       !Travel Month);

FEEDERS;

# --- Feeder statements (below FEEDERS declaration) ---

[Travel Measure:'Rate']     => [Travel Measure:'Amount'];
[Travel Measure:'Quantity'] => [Travel Measure:'Amount'];
```

---

## 4. Feeder architecture decisions

### The core principle: feeders must be as narrow as the rule they support

| Pattern | Verdict | Why |
|---|---|---|
| `[] => ['Amount']` (entire dimension) | ❌ Never | Feeds every cell in every dimension — massive memory overhead |
| `['Rate'] => ['Amount']` | ✅ Correct | Feeds only Amount cells where Rate is non-zero |
| `['Rate', 'Budget'] => ['Amount', 'Budget']` | ✅ Best (tightest) | Feeds only Budget-version Amount cells where Budget Rate is non-zero |

### Feeder design for Rate × Quantity models

Both inputs must feed the output:

```
FEEDERS;
[Travel Measure:'Rate']     => [Travel Measure:'Amount'];
[Travel Measure:'Quantity'] => [Travel Measure:'Amount'];
```

**Rationale:** If either Rate or Quantity is non-zero, the Amount rule should fire.
Feeding from both ensures Amount is recalculated when either input changes.

### Feeder design for DB() cross-cube rules

When Rate is pulled from the Rates cube via DB():

```
FEEDERS;
# Feed Amount from Quantity (the user-entered value)
[Travel Measure:'Quantity'] => [Travel Measure:'Amount'];
# Feed Rate (and therefore Amount) from the Rates cube
[Travel Measure:'Quantity'] => [Travel Measure:'Rate'];
```

**Why feed Rate from Quantity?** The DB() rule for Rate produces a value whenever
the Rates cube has data, but TM1 needs a feeder in the *source* cube to know the
Rate cell is non-empty. Feeding Rate from Quantity ensures Rate cells are included
in consolidations when trips have quantities entered.

---

## 5. SKIPCHECK placement — always required

`SKIPCHECK;` tells TM1 to use the **sparse consolidation algorithm**, skipping cells
that are not fed. Without it, feeders have no effect.

```
SKIPCHECK;     ← Must come BEFORE the calculation rules and BEFORE FEEDERS;
```

**Common mistake:** Adding feeders but forgetting SKIPCHECK. The feeders exist but
TM1's default (dense) consolidation ignores them — rule-calculated cells may be skipped.

---

## 6. FEEDSTRINGS — when it is required

`FEEDSTRINGS;` must be the **very first line** of the rules file when any rule produces
a string value. Omitting it causes string-derived cells to be invisible under zero
suppression and unreliable in cross-cube DB() references.

```
FEEDSTRINGS;   ← First line — only if string rules exist

SKIPCHECK;
...
```

**For driver-based travel budget models:** typically not needed (all rules produce
numeric values). Include only if adding rules that produce string values (e.g., a
"Status" cell derived from a string attribute).

---

## 7. Rule precedence — first match wins

When multiple rules apply to the same cell, **the first statement wins**. Later rules
for the same area are ignored.

```
# This rule fires first for Amount cells
[Travel Measure:'Amount'] = N: [Travel Measure:'Rate'] * [Travel Measure:'Quantity'];

# This rule would NEVER fire for Amount — the first rule already matched
[Travel Measure:'Amount'] = N: 0;   ← Dead rule — remove it
```

**Design implication:** Order rules from most-specific to least-specific. The most
common case should be first. Use `STET` to explicitly fall through to consolidation
for exceptions.

---

## 8. Architecture decision summary for common model types

### Driver-based budget (Rate × Quantity)

```
SKIPCHECK;

[Measure:'Amount'] = N: [Measure:'Rate'] * [Measure:'Quantity'];

FEEDERS;
[Measure:'Rate']     => [Measure:'Amount'];
[Measure:'Quantity'] => [Measure:'Amount'];
```

### Driver-based with cross-cube rate lookup

```
SKIPCHECK;

[Measure:'Rate'] = N:
    DB('Rates Cube', !Dim1, !Dim2, 'Rate', !Version, !Month);

[Measure:'Amount'] = N: [Measure:'Rate'] * [Measure:'Quantity'];

FEEDERS;
[Measure:'Quantity'] => [Measure:'Rate'];
[Measure:'Quantity'] => [Measure:'Amount'];
[Measure:'Rate']     => [Measure:'Amount'];
```

### Consolidated percentage (C: level rule)

```
SKIPCHECK;

# Gross Margin % only meaningful at total level
[Measure:'GM%'] = C:
    ZSAVE([Measure:'Gross Margin'] \ [Measure:'Revenue'] * 100, 0);

FEEDERS;
[Measure:'Gross Margin'] => [Measure:'GM%'];
[Measure:'Revenue']      => [Measure:'GM%'];
```

---

## 9. Rules anti-patterns to avoid

| Anti-pattern | Problem | Fix |
|---|---|---|
| Rule with no matching feeder | Rule-calculated cells skipped in consolidation | Always add a corresponding feeder for every rule |
| Feeder that feeds an entire dimension `[]` | Memory explosion — every cell is marked as non-zero | Scope feeders to the specific measure or area |
| FEEDERS before rules | TM1 syntax error — rules must precede FEEDERS | Always: SKIPCHECK → rules → FEEDERS → feeders |
| `N:` qualifier on a consolidation-level formula | Rule never fires (N: means leaf only) | Use `C:` for consolidation-level calculations |
| Hardcoded values in rules | Inflexible — changes require rules file edit | Use attributes (`ATTRN()`) or cross-cube DB() for variable values |
