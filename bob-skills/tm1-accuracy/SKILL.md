---
name: tm1-accuracy
description: >-
  Use when generating, reviewing, or verifying IBM Planning Analytics (TM1)
  technical content for accuracy — including training materials, TM1 Academy
  modules, developer guides, model documentation, or any content that describes
  TM1 rules, feeders, TurboIntegrator processes, MDX, dimensions, security, or
  cube design. Activate before generating any TM1 training content, or to
  review existing content for correctness against the latest IBM Planning
  Analytics documentation, or against the specific version stated in the prompt.
  Trigger phrases: "check this for accuracy", "verify this TM1 content",
  "review this training module", "is this correct TM1 syntax", "generate
  accurate TM1 content", "TM1 Academy", "training course", "learning materials".
metadata:
  enabled: true
  author: IBM Bob — grounded in IBM Planning Analytics public documentation (latest unless version specified)
  version: 1.1.0
  disable-model-invocation: false
---

# TM1 Content Accuracy — Verified Reference for IBM Planning Analytics

Use this skill whenever generating or reviewing TM1 technical content to ensure
correctness. All facts must be grounded in IBM's public Planning Analytics
documentation at `ibm.com/docs/en/planning-analytics/`.

> **Version discipline — read this first before generating any content:**
>
> 1. **If the prompt explicitly names a Planning Analytics version** (e.g. "PA 2.1",
>    "Planning Analytics 2.1.0", "PA 3.x", "version 2.0.9"), use **only** that
>    version's documentation. Substitute that version string wherever `<VERSION>`
>    appears in the URL patterns in Step 5. Do not mix in behaviour from other
>    versions.
>
> 2. **If no version is mentioned**, default to the **latest generally available
>    release** of IBM Planning Analytics. Use the `latest` URL alias
>    (`ibm.com/docs/en/planning-analytics/latest`) so the links always resolve to
>    current content. Note the resolved version in any generated document so readers
>    know which release was targeted.
>
> 3. **Where behaviour differs between versions**, call it out explicitly — do not
>    silently apply one version's rules to content scoped to another.
>
> 4. **Mark every code example** with a comment identifying the target version,
>    e.g. `# PA latest` or `# PA 2.1.0`.

---

## How to use this skill

### When GENERATING TM1 content (training modules, guides, examples)

1. **Determine the target version** using the Version discipline rule above.
2. Load the relevant reference file(s) from the list below **before** writing content.
3. Write all code examples, syntax, and procedures against those verified facts.
4. After generating a section, run the **self-check** in Step 3 below.
5. Mark every code example with a version comment (`# PA latest` or `# PA <version>`) to signal scope.

### When REVIEWING existing TM1 content

1. Read the content to be reviewed.
2. Load all reference files that cover the topics in that content.
3. Run the **accuracy audit** in Step 4 below.
4. Output a structured finding report — do not silently correct errors.

---

## Step 1 — Identify the topic scope

Map the content topic(s) to the reference files below. Load only what is needed.

| Topic | Reference file |
|-------|---------------|
| TM1 Rules syntax — area statements, N:/C:, STET, CONTINUE | [`references/rules-and-feeders.md`](references/rules-and-feeders.md) |
| SKIPCHECK, FEEDERS, FEEDSTRINGS, feeder breadth | [`references/rules-and-feeders.md`](references/rules-and-feeders.md) |
| TurboIntegrator — tabs, variables, DataSourceType, functions | [`references/ti-processes.md`](references/ti-processes.md) |
| **TI function availability (SaaS vs On-Prem), AttrPut split rule, CellPutN leaf rule, Now() string rule, pre-flight probe** | [`references/ti-processes.md`](references/ti-processes.md) — *SaaS section* |
| MDX — syntax, TM1-specific functions, NON EMPTY, subsets | [`references/mdx-and-subsets.md`](references/mdx-and-subsets.md) |
| Dimensions, hierarchies, element types (N/C/S), attributes | [`references/dimensions-and-modelling.md`](references/dimensions-and-modelling.md) |
| Cube design, sparse data, feeder performance | [`references/dimensions-and-modelling.md`](references/dimensions-and-modelling.md) |
| Security — groups, object rights, cell security, CAM | [`references/security.md`](references/security.md) |
| Review workflow and output format | [`references/review-workflow.md`](references/review-workflow.md) |

---

## Step 2 — Known errors the KPMG team encountered

These are confirmed mistakes found in earlier Bob-generated TM1 training content.
Check for each one explicitly before declaring content accurate.

| Error pattern | Correct behaviour |
|---------------|------------------|
| Feeders omitted or invented without `SKIPCHECK` | `SKIPCHECK;` must precede the `FEEDERS;` block. Without SKIPCHECK, sparse consolidation uses the default algorithm even if feeders exist. |
| Feeder scope too broad (feeding entire dimension) | Feeders should target the **specific leaf-level area** that drives the rule, not the full dimension. Over-broad feeders cause unnecessary memory consumption. |
| `FEEDSTRINGS` missing when rules derive string values | Any rule that produces a string value requires `FEEDSTRINGS;` as the **first line** of the rule file, before `SKIPCHECK`. |
| TI variable type stated as "Boolean" | TM1 TI has no Boolean variable type. Valid types: **Numeric** and **String** only. |
| TI described as having 3 tabs | TurboIntegrator has **4 tabs**: Prolog, Metadata, Data, Epilog. Never 3. |
| `DataSourceType` described with unsupported values | Valid types for PA 2.1: `CHARACTERDELIMITED`, `POSITIONDELIMITED`, `VIEW`, `SUBSET`, `ODBC`, `OLEDBOLAP`, `NULL`. |
| MDX `NON EMPTY` placed on wrong axis | `NON EMPTY` applies per axis — `NON EMPTY {…} ON COLUMNS` and/or `NON EMPTY {…} ON ROWS` independently. |
| TM1-specific MDX functions attributed to standard MDX | Functions like `TM1DISTINCT`, `TM1FILTERBYLEVEL`, `TM1FILTERBYPATTERN`, `TM1SORTBYINDEX`, `TM1SUBSETALL` are **TM1-specific** — not available in generic MDX engines. |
| Security default stated as "Read" for new objects | New TM1 objects (cubes, dimensions, processes, chores) default to **None** access for all groups. Exception: application folders default to **Read**. |
| N: and C: described as optional qualifiers | They are optional in syntax but have precise meaning: `N:` restricts the rule to numeric leaf cells; `C:` restricts to consolidated cells. Omitting them applies the rule to **both levels**. |
| Rules stated as "first match wins" | Correct — when multiple rules apply to the same area, **the first statement takes precedence**. This is a common misunderstanding: teach it explicitly. |

---

## Step 3 — Self-check after generating content

After generating any TM1 content section, verify each item:

- [ ] Every rules example uses correct `[Area] = N: Formula;` or `[Area] = C: Formula;` syntax
- [ ] Every feeder block is preceded by `SKIPCHECK;` and then `FEEDERS;`
- [ ] `FEEDSTRINGS;` appears as the first line when string rules are present
- [ ] No TI examples describe a "Boolean" variable type
- [ ] All TI process descriptions mention exactly 4 tabs (Prolog, Metadata, Data, Epilog)
- [ ] `DataSourceType` values match the verified list
- [ ] MDX examples use `NON EMPTY` correctly per-axis
- [ ] TM1-specific MDX functions are labelled as TM1-specific
- [ ] Security defaults (None for objects, Read for app folders) are stated correctly
- [ ] All content is scoped to the correct target version — **latest** if no version was specified in the prompt, or the **explicitly named version** if one was given
- [ ] Every code example is annotated with its target version (`# PA latest` or `# PA <version>`)
- [ ] **SaaS target:** `AttrPut` calls are in a **separate process** from `DimensionCreate` (not combined)
- [ ] **SaaS target:** All `CellPutN` targets are N-type (leaf) elements — no consolidations
- [ ] **SaaS target:** `Now()` return value is converted via `NumberToString(INT(Now(1)))` before string concatenation
- [ ] **SaaS target:** Cube rules are applied via REST API `PATCH /Cubes('{name}')/Rules` — not via a TI function
- [ ] **SaaS target:** Pre-flight probe has been run (or server is a known-good baseline) before committing to a full build

---

## Step 4 — Accuracy audit output format

When reviewing existing content, always produce a structured report. Use
[`references/review-workflow.md`](references/review-workflow.md) for the
full template. Summary format per finding:

```
FINDING [n] — [CRITICAL | WARNING | INFO]
Topic:    <module name or section>
Location: <heading / line / paragraph reference>
Issue:    <what is wrong>
Correct:  <what it should say>
Source:   <IBM docs URL>
```

Severity levels:
- **CRITICAL** — factually wrong; would cause a developer to write broken or dangerous TM1 code
- **WARNING** — misleading, incomplete, or likely to cause confusion in production use
- **INFO** — minor inaccuracy, outdated phrasing, or missing best practice

---

## Step 5 — IBM documentation anchor URLs

### Version resolution rule for URLs

Replace `<VERSION>` in every URL below with:
- **`latest`** — when no PA version is specified in the prompt (default)
- **The exact version string** (e.g. `2.1.0`, `2.0.9.4`) — when the prompt names a specific version

**URL pattern:** `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=<topic-slug>`

**Latest alias (use by default):** `https://www.ibm.com/docs/en/planning-analytics/latest?topic=<topic-slug>`

### Reference URLs (substitute `<VERSION>` per rule above)

| Topic | URL template |
|-------|-------------|
| Rules statements guide | `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=data-guidelines-writing-tm1-rules-statements` |
| SKIPCHECK and feeders | `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=feeders-skipcheck` |
| TurboIntegrator overview | `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=processes-turbointegrator` |
| TI DataSourceType variable | `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=variables-datasourcetype` |
| TM1-specific MDX functions | `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=mfs-tm1-specific-mdx-functions` |
| Controlling access to TM1 objects | `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=developers-controlling-access-tm1-objects` |
| Element types (N/C/S) | `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=metadata-entity-types` |
| TM1 source specification (TI structure) | `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=git-tm1-model-source-specification` |

### Known errors table — version scope

The known errors in Step 2 were validated against **PA 2.1**. When targeting a
different version, verify each item against the target version's documentation —
behaviour may have changed (e.g. new `DataSourceType` values added in later releases,
or TI tab structure clarifications).
