# TM1 Content Review Workflow

Use this reference when running an accuracy audit on existing TM1 training content
or technical documentation.

---

## Review process

### Phase 1 — Scope the content

Identify which topic areas the content covers. Map to reference files in this skill:

- Rules/feeders → `rules-and-feeders.md`
- TurboIntegrator → `ti-processes.md`
- MDX/subsets → `mdx-and-subsets.md`
- Dimensions/modelling → `dimensions-and-modelling.md`
- Security → `security.md`

### Phase 2 — Run known-error checks

Check every item in the "Known errors" table in `SKILL.md` against the content.
These are the errors confirmed to appear in KPMG's earlier Bob-generated content.

### Phase 3 — Run topic-specific checks

For each loaded reference file, check the content against the verified facts.
Flag any discrepancy as a finding.

### Phase 4 — Output the findings report

---

## Finding report template

```
═══════════════════════════════════════════════
TM1 ACCURACY REVIEW — [Document / Module Name]
Reviewed against: IBM Planning Analytics [latest | <version>] documentation
Date: [date]
═══════════════════════════════════════════════

SUMMARY
  Critical findings : [n]
  Warnings          : [n]
  Info              : [n]
  Total findings    : [n]

───────────────────────────────────────────────
FINDINGS
───────────────────────────────────────────────

FINDING 1 — CRITICAL
Topic:    [Module name / Section heading]
Location: [Exact location — heading, paragraph, code block line]
Issue:    [What is wrong — be specific]
Correct:  [What it should say — include corrected code or text if applicable]
Source:   [IBM docs URL]

FINDING 2 — WARNING
Topic:    ...
Location: ...
Issue:    ...
Correct:  ...
Source:   ...

[Continue for all findings]

───────────────────────────────────────────────
VERIFIED CORRECT
───────────────────────────────────────────────
The following sections were checked and found accurate:
- [Section name] — [brief note on what was verified]

───────────────────────────────────────────────
RECOMMENDED ACTIONS
───────────────────────────────────────────────
Priority 1 (fix before use):
  [ ] [Fix description for each CRITICAL finding]

Priority 2 (fix before publication):
  [ ] [Fix description for each WARNING finding]

Priority 3 (optional improvement):
  [ ] [Fix description for each INFO finding]
```

---

## Severity definitions

| Severity | Definition | Example |
|----------|-----------|---------|
| **CRITICAL** | Factually wrong — would cause a developer to write broken or unsafe TM1 code | "FEEDSTRINGS is optional even when string rules exist" — FALSE, missing it causes invisible string cells |
| **WARNING** | Misleading, incomplete, or likely to cause production problems | Describing feeder breadth without mentioning performance implications |
| **INFO** | Minor inaccuracy, slightly outdated phrasing, or missing best practice | Using `C:\` hardcoded paths in TI examples without noting this is environment-specific |

---

## Accuracy confidence rating

At the end of the review, assign one of three ratings to the document:

| Rating | Criteria |
|--------|----------|
| ✅ **Accurate** | Zero Critical findings; Warnings are minor and do not affect learning outcomes |
| ⚠️ **Needs revision** | One or more Critical findings, OR three or more Warnings |
| ❌ **Do not use** | Multiple Critical findings that would teach developers incorrect TM1 patterns |
