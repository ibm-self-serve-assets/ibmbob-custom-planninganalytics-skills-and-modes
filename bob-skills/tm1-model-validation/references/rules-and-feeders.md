# Rules and feeders — requirements and failure signatures

## Required statement order

```
FEEDSTRINGS;      # only if any rule produces a string value — must be the FIRST line, before SKIPCHECK
SKIPCHECK;        # required whenever FEEDERS are defined
UNDEFVALS;        # optional
['...'] = N: ... ;   # rule statements
FEEDERS;
['...'] => DB('...', ...);   # feeder statements
```

- `FEEDSTRINGS` must be the first line of the rule file, before `SKIPCHECK`. String rules without it produce cells that exist but never feed.
- `SKIPCHECK` turns on sparse consolidation. Without it, TM1 walks every cell in the consolidation, dense — the model is correct but can be orders of magnitude slower.
- **`SKIPCHECK` without complete feeders returns wrong answers, not slow answers.** Sparse consolidation skips unfed cells entirely, so a rule-calculated value that is not fed simply does not appear in its parent. This is the single most damaging defect class in TM1 and it is silent: no error, no log entry, just a number that is too low.

## Failure signatures

| Symptom | Most likely cause | Confirm with |
|---|---|---|
| Consolidated cell is zero, leaf cells have values | Missing feeder | `check_cell_feeders` on the consolidated intersection |
| Consolidation correct but very slow | `SKIPCHECK` missing, or feeders far too broad | Check rule text for `SKIPCHECK`; inspect feeder source scope |
| Memory far above estimate | Over-broad feeders — typically `[]` across a high-cardinality dimension | Count fed cells; narrow the feeder source |
| String cells blank in views though the rule looks right | `FEEDSTRINGS` absent or placed after `SKIPCHECK` | Read the first line of the rule file |
| User input disappears on refresh | A rule targets the same area as the input; rule wins over `N:` input | Write, re-read, compare |
| Value right at N level, wrong at C level | Rule fires at `C:` where the doc expects default aggregation, or a `STET` area is being overridden | `trace_cell_calculation` at the C intersection |
| Rules file appears to do nothing | Compile failure — the whole file is rejected, not just the bad line | `RULES ERROR` in the message log |

A rules file that fails to compile is rejected **in its entirety**. Always confirm compilation before investigating any calculation defect, or you will debug a rule the server never loaded.

## Feeder breadth heuristic

Flag a feeder for review when its source area leaves a high-cardinality dimension unrestricted (`[]` or an all-members reference) and the target could be reached from a narrower slice. Rough guide: a feeder whose source spans more than a few thousand cells per driver record deserves a second look. This is a heuristic, not a rule — report it as MINOR/INFO with the counts, and let the modeller decide.

## Feeder verification by version

- **PA v12 / recent v11** — `check_cell_feeders(cube_name, elements, dimensions)` returns the feeder status for a specific intersection. Definitive and scriptable. `trace_cell_calculation(...)` shows the calculation path for the same cell.
- **Older v11** — TM1 Architect → Rules → Feeder Trace, interactively. Not scriptable; record the screenshot or the trace output as evidence.

## Sources

- [IBM — TM1 server feeders guidelines and best practices](https://www.ibm.com/support/pages/tm1-server-feeders-guidelines-and-best-practices)
- [IBM — Skipcheck and Feeders](https://www.ibm.com/docs/SSD29G_2.0.0/com.ibm.swg.ba.cognos.tm1_rul.2.0.0.doc/t_skipcheckandfeeders_n800a7.html)
- [QueBIT — When and how to use FEEDSTRINGS](https://quebit.com/askquebit/feedstrings-rule-function-when-and-how-to-use-it/)
- [Ironside — Managing SKIPCHECK and feeders in TM1](https://www.ironsidegroup.com/blog/managing-skipcheck-and-feeders-in-ibm-cognos-tm1/)
- [Cubewise — FEEDERS function reference](https://cubewise.com/functions-library/tm1-function-for-rules-feeders/)
- [TM1py API reference](https://tm1py.readthedocs.io/en/latest/api.html)
