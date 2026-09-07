# spec.json — the design document, machine-readable

The harness compares the server against this file, so the spec **is** the design
document expressed as data. Fill it from the design doc before the build, not
after — a spec derived from the finished model validates nothing.

```jsonc
{
  "model_name": "Freight Cost Planning",
  "database": "PLANNING_DEV",
  "pa_version": "v12",
  "design_document": "PA Freight Model Design v1.3, 2026-08-28",

  "connection": {                    // password from $TM1_PASSWORD, never here
    "base_url": "https://<tenant>.planninganalytics.cloud.ibm.com/api/<db>/v0",
    "user": "apikey",
    "ssl": true
  },

  "naming_convention": { "dimension_regex": "^(Dim|dm)[A-Z]" },

  "dimensions": {
    "Period": {
      "hierarchy": "Period",
      "element_count": 65,
      "top_element": "Total Year",
      "top_element_children": 4,
      "attributes": ["Alias", "SortOrder"],
      "attribute_min_population": 1.0
    },
    "Route":   { "attributes": ["Alias", "Code"], "attribute_min_population": 0.95 },
    "Measure": {}
  },

  "cubes": {
    "FreightCost": {
      "dimensions": ["Period", "Route", "Product", "Version", "Measure"]
    },
    "FreightRates": { "dimensions": ["Period", "Route", "RateMeasure"] }
  },

  "processes": ["Load.FreightActuals", "Maint.RouteDimension"],

  "chores": {
    "Nightly.FreightLoad": {
      "process_order": ["Maint.RouteDimension", "Load.FreightActuals"]
    }
  },

  "sample_cells": [
    {
      "cube": "FreightCost",
      "elements": ["2026-Q1", "MUM-DXB", "Total Product", "Budget", "Amount"],
      "expect_fed": true,
      "expected_value": 184250.0,     // computed OUTSIDE TM1
      "tolerance": 0.5
    }
  ],

  "security": { "intentionally_granted": [] },
  "memory_budget_bytes": 8000000000,
  "message_log_window_hours": 24
}
```

## Choosing sample cells

Three or four well-chosen intersections catch more than fifty arbitrary ones.
Pick, at minimum:

1. One **N-level rule-calculated** cell where you can compute the answer by hand.
2. One **C-level consolidation** that depends on a feeder — this is where missing
   feeders surface.
3. One cell reached through a **`DB()` cross-cube lookup**, so the rate cube is
   exercised.
4. One cell where **user input must survive** — the rule area and the input area
   overlap.

`expected_value` must come from outside TM1. A value copied out of the cube and
pasted back into the spec turns the check into a tautology.

## Notes

- The harness is **read-only**. Gates 3, 7 and 8 write cells or need PAW, so they
  are executed manually against `references/checklist.md`.
- Exit code is `1` when any BLOCKER is found, so it drops into CI unchanged.
- `attribute_min_population` below `1.0` is a deliberate allowance — record why in
  the design doc, or a partially populated alias will pass quietly.

---

## Intrinsic mode — no design document

When there is no design document, skip the expectations entirely. The spec then carries
only connection details, and everything else is discovered from the server:

```jsonc
{
  "model_name": "M2",
  "database": "PA_SAAS_M2",
  "pa_version": "v12",
  "connection": {
    "base_url": "https://TENANT.planninganalytics.cloud.ibm.com/api/DATABASE/v0",
    "user": "apikey",
    "ssl": true
  },
  "intrinsic": {
    "consolidation_samples": 12,   // gate 14 sample size; raise when a run is cheap
    "tolerance": 0.01
  }
}
```

```bash
python tm1_validate.py --mode intrinsic --spec conn.json --out report_M2/
```

Discovery deliberately produces a spec with **no expectations** — no element counts, no
dimension order, no expected values. If it recorded what it found as what it expected, the
model would be validated against itself and every check would pass by construction.

Two consequences worth understanding:

- "Unexpected object" checks are **suppressed**, not passed. Without a document there is no
  such thing as an unexpected object.
- The best available verdict is `NO DEFECTS DETECTED — intent not assessed`. The harness
  will not emit a sign-off in this mode.

### Comparing two models

```bash
python tm1_validate.py --mode intrinsic --spec conn_M1.json --out report_M1/
python tm1_validate.py --mode intrinsic --spec conn_M2.json --out report_M2/
```

Keep `intrinsic.consolidation_samples`, `tolerance` and the gate list identical across
both, or the comparison is not a comparison. Then compare `findings.json` by gate and
severity — and put object counts next to defect counts, since a model that built less has
less surface to be wrong on.
