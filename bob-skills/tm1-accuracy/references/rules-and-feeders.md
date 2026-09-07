# TM1 Rules and Feeders — Verified Reference

> **Version note:** The facts in this file were validated against **PA 2.1**.
> When this skill is used for a different version, verify against the target version's docs.
> Replace `<VERSION>` with `latest` (default) or the explicit version from the prompt.

Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=data-guidelines-writing-tm1-rules-statements`
Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=feeders-skipcheck`

---

## Rules statement syntax

The canonical form of a TM1 rules statement is:

```
[Area] = Formula;
```

To restrict to **numeric leaf cells** only:
```
[Area] = N: Formula;
```

To restrict to **consolidated cells** only:
```
[Area] = C: Formula;
```

Omitting `N:` or `C:` applies the rule to **both** N and C levels.

### Area syntax

The Area identifies one or more cells in a cube. Elements are referenced by enclosing
them in single quotes within square brackets:

```
['Revenue', 'Jan', 'Actual'] = N: ['Units'] * ['Price'];
```

To scope a rule to a dimension element, qualify with the dimension name when the element
name appears in multiple dimensions:

```
[Measures:'Revenue'] = N: [Measures:'Units'] * [Measures:'Price'];
```

### Precedence rule

When more than one rules statement applies to the **same area**, the **first statement
takes precedence**. Rules are evaluated top-to-bottom; once a match is found, later
matching rules for the same area are ignored. This is a common source of bugs — teach it
explicitly.

### STET — bypassing a rule

Use `STET` to bypass a rule for a specific area and allow TM1 to use its default
consolidation behaviour:

```
['Budget'] = STET;
```

`STET` is valid as a formula in any rules statement. It forces the cell to be calculated
by normal TM1 consolidation rather than the rule.

### CONTINUE — fallthrough to next rule

`CONTINUE` causes TM1 to evaluate the **next** matching rules statement rather than
stopping at the first match. Use sparingly; it can make rule tracing difficult.

---

## SKIPCHECK and FEEDERS — exact procedure

Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=feeders-skipcheck`

### Step 1 — FEEDSTRINGS (conditional — must be first line if used)

If **any** rule in the file produces a **string value**, insert `FEEDSTRINGS;` as the
**very first line** of the rules file, before everything else:

```
FEEDSTRINGS;
```

Omitting `FEEDSTRINGS` when string rules exist causes:
- String-derived cells to be invisible when zero-suppression is applied to a view
- Unreliable cross-cube references to those string cells

### Step 2 — SKIPCHECK

Insert `SKIPCHECK;` in the rules file to force TM1 to use the **sparse consolidation
algorithm**:

```
SKIPCHECK;
```

Without `SKIPCHECK`, TM1 uses its default consolidation algorithm regardless of whether
feeders are defined. SKIPCHECK is what makes feeders meaningful — it tells TM1 to skip
cells that are not fed.

### Step 3 — Write calculation rules (above FEEDERS block)

Place all rules statements before the `FEEDERS;` declaration.

### Step 4 — FEEDERS declaration

```
FEEDERS;
```

All feeder statements follow this declaration.

### Step 5 — Feeder statements

A feeder statement has the form:

```
FeederArea => RulesCalculatedArea;
```

The **FeederArea** is the component that, when non-zero, signals that the rule-derived
cell should be included in consolidations. The **RulesCalculatedArea** is the cell the
rule calculates.

```
# Example: feed Gross Margin from Revenue
['Revenue'] => ['GrossMargin'];
```

### Complete skeleton (correct order)

```
FEEDSTRINGS;     # Only if string rules exist — must be first

SKIPCHECK;

['GrossMargin'] = N: ['Revenue'] - ['COGS'];

FEEDERS;
['Revenue'] => ['GrossMargin'];
```

---

## Feeder breadth — performance rules

| Pattern | Effect | Verdict |
|---------|--------|---------|
| Feed the entire dimension: `[] => ['Calc']` | Feeds every leaf in every dimension — massive memory overhead | ❌ Never do this |
| Feed the specific measure: `['Revenue'] => ['GrossMargin']` | Feeds only cells where Revenue is non-zero | ✅ Correct pattern |
| Feed with a scope restriction: `['Revenue', 'Actual'] => ['GrossMargin', 'Actual']` | Feeds only the Actual version of GrossMargin | ✅ Tightest, best performance |

Over-broad feeders are the most common performance issue in TM1 rule files. A feeder
should be as narrow as the rule it supports.

---

## DB() function — cross-cube references

```
['GrossMargin'] = N: DB('RatesTable', !Product, !Time, 'Rate') * ['Quantity'];
```

- First argument: cube name (string)
- Subsequent arguments: elements for each dimension of the target cube, in dimension order
- `!DimensionName` refers to the current element in that dimension

The target cube's dimension order must match the argument order exactly.
