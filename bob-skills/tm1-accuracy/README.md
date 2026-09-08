# tm1-accuracy

**Author:** IBM Bob — grounded in IBM Planning Analytics public documentation  
**Version:** 1.1.0

A Bob skill for generating, reviewing, and verifying IBM Planning Analytics (TM1) technical content for accuracy. All facts are grounded in IBM's public Planning Analytics documentation at `ibm.com/docs/en/planning-analytics/`.

---

## Table of Contents

1. [When to use this skill](#when-to-use-this-skill)
2. [Install](#install)
3. [Requirements and scope](#requirements-and-scope)
4. [Version discipline](#version-discipline)
5. [What this skill checks](#what-this-skill-checks)
6. [How the skill works](#how-the-skill-works)
7. [Accuracy audit output format](#accuracy-audit-output-format)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)
10. [Reference files](#reference-files)
11. [IBM documentation](#ibm-documentation)
12. [License and source](#license-and-source)

---

## When to use this skill

Activate this skill when you need to:

- **Generate** TM1 training materials, TM1 Academy modules, developer guides, or model documentation
- **Review** existing TM1 content for correctness against a specific PA version or the latest release
- **Verify** TM1 syntax — rules, feeders, TurboIntegrator processes, MDX, dimensions, or security patterns

**Trigger phrases:** `check this for accuracy`, `verify this TM1 content`, `review this training module`, `is this correct TM1 syntax`, `generate accurate TM1 content`, `TM1 Academy`, `training course`, `learning materials`

---

## Install

```bash
cp -r tm1-accuracy ~/.bob/skills/
```
Bob loads it automatically when a matching trigger phrase is detected.

To activate manually in a conversation, say:

> "Use the tm1-accuracy skill"

or reference a trigger phrase from the list above.

---

## Requirements and scope

| Requirement | Detail |
|---|---|
| **IBM Bob** | Any version with skills support |
| **IBM Planning Analytics** | PA 2.0 or later (latest GA recommended); earlier versions supported when explicitly named in the prompt |
| **IBM documentation access** | Bob queries `ibm.com/docs/en/planning-analytics/` — an internet connection is required for live doc lookups |
| **No TM1 server connection needed** | This skill operates on content and syntax only — it does not connect to a live TM1 server |

**In scope:**
- TM1 rules syntax (area statements, N:/C:, STET, CONTINUE, SKIPCHECK, FEEDERS, FEEDSTRINGS)
- TurboIntegrator processes (tabs, variables, DataSourceType, functions, SaaS constraints)
- MDX queries and TM1-specific MDX functions
- Dimension and cube design patterns
- TM1 security model (groups, object rights, cell security, CAM)
- Training and documentation content review

**Out of scope:**
- Live model execution or data validation 
- Model architecture design decisions 
- Non-TM1 IBM products

---

## Version discipline

| Scenario | Behaviour |
|---|---|
| Prompt names a specific PA version (e.g. "PA 2.1") | Use **only** that version's documentation; do not mix in other versions |
| No version mentioned | Default to the **latest GA release** — use the `latest` URL alias |
| Behaviour differs between versions | Call it out explicitly — never silently apply one version's rules to another |

Every code example must be annotated with its target version, e.g. `# PA latest` or `# PA 2.1.0`.

---

## What this skill checks

### Known error patterns (always verify these)

| Error pattern | Correct behaviour |
|---|---|
| Feeders omitted or invented without `SKIPCHECK` | `SKIPCHECK;` must precede the `FEEDERS;` block |
| Feeder scope too broad | Feeders must target the specific leaf-level area that drives the rule |
| `FEEDSTRINGS` missing when rules derive string values | `FEEDSTRINGS;` must be the **first line** of the rule file |
| TI variable type stated as "Boolean" | TM1 TI has no Boolean type — only **Numeric** and **String** |
| TI described as having 3 tabs | TurboIntegrator has **4 tabs**: Prolog, Metadata, Data, Epilog |
| `DataSourceType` with unsupported values | Valid types: `CHARACTERDELIMITED`, `POSITIONDELIMITED`, `VIEW`, `SUBSET`, `ODBC`, `OLEDBOLAP`, `NULL` |
| `NON EMPTY` placed on wrong axis | `NON EMPTY` applies independently per axis |
| TM1-specific MDX functions attributed to standard MDX | `TM1DISTINCT`, `TM1FILTERBYLEVEL`, `TM1FILTERBYPATTERN`, `TM1SORTBYINDEX`, `TM1SUBSETALL` are TM1-specific |
| Security default stated as "Read" for new objects | New objects default to **None** — exception: application folders default to Read |
| Rules stated as "last match wins" | **First statement takes precedence** when multiple rules apply to the same area |

### SaaS-specific checks

- `AttrPut` calls must be in a **separate process** from `DimensionCreate`
- All `CellPutN` targets must be N-type (leaf) elements — no consolidations
- `Now()` return value must be converted via `NumberToString(INT(Now(1)))` before string concatenation
- Cube rules are applied via REST API `PATCH /Cubes('{name}')/Rules` — not via a TI function

---

## How the skill works

### Generating content

1. Determine the target version using the version discipline rule above
2. Load the relevant reference file(s) from the topic map below
3. Write all code examples and procedures against verified facts
4. Run the self-check checklist before finalising
5. Annotate every code example with its target version

### Reviewing existing content

1. Read the content to be reviewed
2. Load all reference files that cover the topics present
3. Run the accuracy audit
4. Output a structured finding report — do not silently correct errors

---

## Accuracy audit output format

Each finding uses this structure:

```
FINDING [n] — [CRITICAL | WARNING | INFO]
Topic:    <module name or section>
Location: <heading / line / paragraph reference>
Issue:    <what is wrong>
Correct:  <what it should say>
Source:   <IBM docs URL>
```

| Severity | Meaning |
|---|---|
| **CRITICAL** | Factually wrong; would cause a developer to write broken or dangerous TM1 code |
| **WARNING** | Misleading, incomplete, or likely to cause confusion in production use |
| **INFO** | Minor inaccuracy, outdated phrasing, or missing best practice |

---

## Examples

### Example 1 — Reviewing a training module for accuracy

**Prompt:**
> "Review this TM1 rules training module for accuracy against PA latest."

**What the skill does:**
1. Loads `references/rules-and-feeders.md`
2. Checks every rule example against the known-error table
3. Verifies `SKIPCHECK` / `FEEDERS` / `FEEDSTRINGS` ordering
4. Outputs a structured finding report

**Sample output:**
```
FINDING 1 — CRITICAL
Topic:    Module 3 — Writing TM1 Rules
Location: Section "Feeders", paragraph 2
Issue:    FEEDERS block is shown without a preceding SKIPCHECK statement
Correct:  SKIPCHECK; must appear on its own line before FEEDERS;
Source:   https://www.ibm.com/docs/en/planning-analytics/latest?topic=feeders-skipcheck
```

---

### Example 2 — Generating a TI process code example for a specific version

**Prompt:**
> "Generate a TurboIntegrator process example for loading from a CSV file. Target PA 2.1.0."

**What the skill does:**
1. Locks to PA 2.1.0 documentation
2. Loads `references/ti-processes.md`
3. Generates code using only verified `DataSourceType` values and variable types
4. Annotates the example with `# PA 2.1.0`

**Sample output:**
```turbointegrator
# PA 2.1.0
# Prolog tab
DataSourceType = 'CHARACTERDELIMITED';
DataSourceNameForServer = 'C:\data\rates.csv';
DataSourceDelimiter = ',';
```

---

### Example 3 — Verifying MDX syntax

**Prompt:**
> "Is this MDX correct TM1 syntax? NON EMPTY {[Measures].[Revenue]} ON ROWS"

**What the skill does:**
1. Loads `references/mdx-and-subsets.md`
2. Checks `NON EMPTY` axis placement
3. Identifies any TM1-specific functions vs standard MDX

**Sample output:**
```
FINDING 1 — WARNING
Topic:    MDX syntax check
Issue:    NON EMPTY is applied to ROWS only — this is valid, but confirm
          whether COLUMNS also needs NON EMPTY suppression independently.
Correct:  NON EMPTY applies per-axis. Both axes can carry it independently:
          NON EMPTY {…} ON COLUMNS, NON EMPTY {…} ON ROWS
Source:   https://www.ibm.com/docs/en/planning-analytics/latest?topic=mfs-tm1-specific-mdx-functions
```

---

## Troubleshooting

### The skill doesn't activate automatically

Ensure your prompt contains one of the documented trigger phrases. If you are combining with model design work, also load `tm1-model-design` — the two skills complement each other.

### Bob generates content that still has errors after running this skill

1. Confirm the correct IBM documentation version was used (check the `# PA <version>` annotations on code examples).
2. Rerun the self-check checklist explicitly — ask Bob: *"Run the tm1-accuracy self-check on the content above."*
3. For SaaS-specific content, verify all four SaaS checks were applied.

### A documented `DataSourceType` value is reported as invalid

The valid set may have expanded in newer PA releases. Specify the target version explicitly and ask Bob to re-verify against that version's documentation.

### Findings reference an IBM docs URL that returns 404

The `latest` alias redirects to the current GA release. If a specific version URL (e.g. `/2.0.9.4/`) no longer resolves, use `latest` or a later supported version string. IBM may retire documentation for end-of-support releases.

---

## Reference files

| File | Covers |
|---|---|
| `references/rules-and-feeders.md` | Area statements, N:/C:, STET, CONTINUE, SKIPCHECK, FEEDERS, FEEDSTRINGS, feeder breadth |
| `references/ti-processes.md` | TI tabs, variables, DataSourceType, functions, SaaS constraints |
| `references/mdx-and-subsets.md` | MDX syntax, TM1-specific functions, NON EMPTY, subsets |
| `references/dimensions-and-modelling.md` | Dimensions, hierarchies, element types (N/C/S), attributes, sparsity |
| `references/security.md` | Groups, object rights, cell security, CAM authentication |
| `references/review-workflow.md` | Full accuracy audit template and workflow |

---

## IBM documentation

Base URL pattern: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=<topic-slug>`

Replace `<VERSION>` with `latest` (default) or the specific version string (e.g. `2.1.0`).

| Topic | URL slug |
|---|---|
| Rules statements guide | `data-guidelines-writing-tm1-rules-statements` |
| SKIPCHECK and feeders | `feeders-skipcheck` |
| TurboIntegrator overview | `processes-turbointegrator` |
| TI DataSourceType variable | `variables-datasourcetype` |
| TM1-specific MDX functions | `mfs-tm1-specific-mdx-functions` |
| Controlling access to TM1 objects | `developers-controlling-access-tm1-objects` |
| Element types (N/C/S) | `metadata-entity-types` |

---

## License and source



- **Author:** IBM Bob — grounded in IBM Planning Analytics public documentation 
- **Source:** `.bob/skills/tm1-accuracy/SKILL.md` in this workspace
- **Documentation basis:** [IBM Planning Analytics documentation](https://www.ibm.com/docs/en/planning-analytics/latest) (public, `ibm.com/docs`)
- **License:** . Content is grounded in publicly available IBM documentation. No warranty is provided for use outside of IBM Bob sessions.
