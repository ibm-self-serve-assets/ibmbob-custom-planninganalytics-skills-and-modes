#!/usr/bin/env python3
"""
TM1 / Planning Analytics post-build validation harness.

Runs the mechanically checkable gates from references/checklist.md against a live
database and emits findings.json + report.md.

Design principles:
  * Every check is independently guarded. One failing API never aborts the run.
  * A check that cannot be executed is recorded as NOT_VERIFIED with the reason,
    never silently skipped and never optimistically passed.
  * Read-only. This script does not write cells, create objects, or repair anything.
    The write-path gates (3 and 7) are deliberately left to the operator.

Usage:
    python tm1_validate.py --spec spec.json --out report/
    python tm1_validate.py --spec spec.json --out report/ --gates 1,2,4,5
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

try:
    from TM1py import TM1Service
except ImportError:  # pragma: no cover
    sys.exit("TM1py is required:  pip install TM1py")


# --------------------------------------------------------------------------- #
# Finding model
# --------------------------------------------------------------------------- #

PASS, FAIL, NOT_VERIFIED = "PASS", "FAIL", "NOT_VERIFIED"
BLOCKER, MAJOR, MINOR, INFO = "BLOCKER", "MAJOR", "MINOR", "INFO"


class Findings:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def add(
        self,
        gate: int,
        check: str,
        result: str,
        severity: str | None = None,
        obj: str = "",
        expected: Any = "",
        observed: Any = "",
        evidence: str = "",
    ) -> None:
        self.items.append(
            {
                "gate": gate,
                "check": check,
                "result": result,
                "severity": severity if result == FAIL else (severity or INFO),
                "object": obj,
                "expected": expected,
                "observed": observed,
                "evidence": evidence,
            }
        )

    def unverified(self, gate: int, check: str, reason: str, obj: str = "") -> None:
        self.add(gate, check, NOT_VERIFIED, INFO, obj=obj, observed=reason)

    def counts(self) -> dict[str, int]:
        c = Counter(i["result"] for i in self.items)
        s = Counter(i["severity"] for i in self.items if i["result"] == FAIL)
        return {
            "total": len(self.items),
            "pass": c[PASS],
            "fail": c[FAIL],
            "not_verified": c[NOT_VERIFIED],
            "blocker": s[BLOCKER],
            "major": s[MAJOR],
            "minor": s[MINOR],
        }


def guarded(f: Findings, gate: int, check: str, obj: str = "") -> Callable:
    """Decorator-ish context: run fn, convert any exception into NOT_VERIFIED."""

    class _Ctx:
        def __enter__(self_inner):
            return None

        def __exit__(self_inner, exc_type, exc, tb):
            if exc is not None:
                f.unverified(gate, check, f"{type(exc).__name__}: {exc}", obj=obj)
                return True  # suppress
            return False

    return _Ctx()


# --------------------------------------------------------------------------- #
# Gate 1 — Dimensions
# --------------------------------------------------------------------------- #

def gate_1_dimensions(tm1: TM1Service, spec: dict, f: Findings) -> None:
    expected = spec.get("dimensions", {})
    convention = spec.get("naming_convention", {}).get("dimension_regex")

    with guarded(f, 1, "enumerate dimensions"):
        actual = set(tm1.dimensions.get_all_names(skip_control_dimensions=True))
        for name in expected:
            if name in actual:
                f.add(1, "dimension exists", PASS, obj=name,
                      expected=name, observed="present",
                      evidence="dimensions.get_all_names()")
            else:
                f.add(1, "dimension exists", FAIL, BLOCKER, obj=name,
                      expected=name, observed="missing",
                      evidence="dimensions.get_all_names()")
        if spec.get("_mode") != "intrinsic":
            for name in sorted(actual - set(expected)):
                f.add(1, "unexpected dimension", FAIL, MINOR, obj=name,
                      expected="not in design document", observed="present on server",
                      evidence="dimensions.get_all_names()")

    if convention:
        rx = re.compile(convention)
        for name in expected:
            ok = bool(rx.match(name))
            f.add(1, "naming convention", PASS if ok else FAIL,
                  None if ok else MINOR, obj=name,
                  expected=convention, observed=name, evidence=f"re.match({convention!r})")

    for dim, dspec in expected.items():
        hier = dspec.get("hierarchy", dim)

        with guarded(f, 1, "element types / duplicates / orphans", obj=dim):
            types = tm1.elements.get_element_types(dim, hier)
            names = list(types.keys())

            # duplicates (case-insensitive, TM1 treats names case-insensitively)
            dupes = [n for n, c in Counter(n.lower() for n in names).items() if c > 1]
            f.add(1, "no duplicate element names", PASS if not dupes else FAIL,
                  None if not dupes else MAJOR, obj=dim,
                  expected="0 duplicates", observed=f"{len(dupes)} -> {dupes[:10]}",
                  evidence="elements.get_element_types()")

            # element count vs design doc
            if "element_count" in dspec:
                got = len(names)
                ok = got == dspec["element_count"]
                f.add(1, "element count matches design", PASS if ok else FAIL,
                      None if ok else MAJOR, obj=dim,
                      expected=dspec["element_count"], observed=got,
                      evidence="len(get_element_types())")

            # orphans: numeric elements that are not a child of any edge
            hierarchy = tm1.dimensions.hierarchies.get(dim, hier)
            edges = dict(hierarchy.edges)  # {(parent, child): weight}
            children = {c.lower() for (_p, c) in edges}
            leaves = [n for n, t in types.items() if str(t).lower().startswith("n")]
            orphans = [n for n in leaves if n.lower() not in children]
            # a flat dimension with no consolidations legitimately has no edges
            if edges:
                f.add(1, "no orphaned leaf elements", PASS if not orphans else FAIL,
                      None if not orphans else MAJOR, obj=dim,
                      expected="every N element has a parent",
                      observed=f"{len(orphans)} orphans -> {orphans[:10]}",
                      evidence="hierarchies.get().edges")
            else:
                f.add(1, "no orphaned leaf elements", PASS, obj=dim,
                      expected="n/a — flat dimension", observed="no consolidations defined",
                      evidence="hierarchies.get().edges == {}")

            # negative / non-unit weights are worth surfacing explicitly
            odd_weights = {f"{p}->{c}": w for (p, c), w in edges.items() if w not in (1, 1.0)}
            if odd_weights:
                f.add(1, "non-unit edge weights present", PASS, INFO, obj=dim,
                      expected="review against design document",
                      observed=dict(list(odd_weights.items())[:15]),
                      evidence="hierarchies.get().edges")

            # top consolidation child coverage
            top = dspec.get("top_element")
            if top:
                direct = [c for (p, c) in edges if p.lower() == top.lower()]
                exp_children = dspec.get("top_element_children")
                if exp_children is not None:
                    ok = len(direct) == exp_children
                    f.add(1, "top consolidation child count", PASS if ok else FAIL,
                          None if ok else MAJOR, obj=f"{dim}:{top}",
                          expected=exp_children, observed=len(direct),
                          evidence="edges where parent == top_element")
                else:
                    f.add(1, "top consolidation children", PASS, INFO, obj=f"{dim}:{top}",
                          observed=f"{len(direct)} direct children",
                          evidence="edges where parent == top_element")

        # attribute population
        for attr in dspec.get("attributes", []):
            with guarded(f, 1, f"attribute populated: {attr}", obj=dim):
                values = tm1.elements.get_attribute_of_elements(dim, hier, attr)
                total = len(values)
                filled = sum(1 for v in values.values() if v not in (None, "", 0))
                rate = filled / total if total else 0
                ok = rate >= dspec.get("attribute_min_population", 1.0)
                f.add(1, "attribute populated", PASS if ok else FAIL,
                      None if ok else MAJOR, obj=f"{dim}.{attr}",
                      expected=f">= {dspec.get('attribute_min_population', 1.0):.0%} populated",
                      observed=f"{filled}/{total} ({rate:.0%})",
                      evidence="elements.get_attribute_of_elements()")


# --------------------------------------------------------------------------- #
# Gate 2 — Cube structure
# --------------------------------------------------------------------------- #

def gate_2_cubes(tm1: TM1Service, spec: dict, f: Findings) -> None:
    expected = spec.get("cubes", {})

    with guarded(f, 2, "enumerate cubes"):
        actual = set(tm1.cubes.get_all_names(skip_control_cubes=True))
        for name in expected:
            present = name in actual
            f.add(2, "cube exists", PASS if present else FAIL,
                  None if present else BLOCKER, obj=name,
                  expected=name, observed="present" if present else "missing",
                  evidence="cubes.get_all_names()")
        if spec.get("_mode") != "intrinsic":
            for name in sorted(actual - set(expected)):
                f.add(2, "unexpected cube", FAIL, MINOR, obj=name,
                      expected="not in design document", observed="present on server",
                      evidence="cubes.get_all_names()")

    for cube, cspec in expected.items():
        with guarded(f, 2, "dimension order", obj=cube):
            dims = tm1.cubes.get_dimension_names(cube)
            exp_dims = cspec.get("dimensions")
            if exp_dims:
                ok = [d.lower() for d in dims] == [d.lower() for d in exp_dims]
                f.add(2, "dimension order matches design",
                      PASS if ok else FAIL, None if ok else MAJOR, obj=cube,
                      expected=exp_dims, observed=dims,
                      evidence="cubes.get_dimension_names()")
            else:
                f.add(2, "dimension order", NOT_VERIFIED, INFO, obj=cube,
                      observed=f"no expected order in spec; actual = {dims}")

        with guarded(f, 2, "sparsity estimate", obj=cube):
            dims = tm1.cubes.get_dimension_names(cube)
            space = 1
            for d in dims:
                space *= max(tm1.elements.get_number_of_elements(d, d), 1)
            populated = _populated_cell_estimate(tm1, cube)
            density = (populated / space) if space else 0
            sev = INFO if density < 0.25 else MINOR
            f.add(2, "sparsity", PASS, sev, obj=cube,
                  expected="dense cubes on high-cardinality dimensions are a design warning",
                  observed=f"~{populated:,} populated / {space:,} cell space = {density:.4%}",
                  evidence="element counts x populated cell count")


def _populated_cell_estimate(tm1: TM1Service, cube: str) -> int:
    """Best-effort populated cell count; falls back to 0 rather than raising."""
    try:
        stats = tm1.cells.execute_mdx_cellcount(
            f"SELECT NON EMPTY {{[{tm1.cubes.get_measure_dimension(cube)}].Members}} ON 0 FROM [{cube}]"
        )
        return int(stats)
    except Exception:
        return 0


# --------------------------------------------------------------------------- #
# Gate 4 — Rules
# --------------------------------------------------------------------------- #

RX_COMMENT = re.compile(r"^\s*#")


def _significant_lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip() and not RX_COMMENT.match(ln)]


def gate_4_rules(tm1: TM1Service, spec: dict, f: Findings) -> None:
    for cube in spec.get("cubes", {}):
        with guarded(f, 4, "rules compile", obj=cube):
            errors = tm1.cubes.check_rules(cube)
            payload = errors.json() if hasattr(errors, "json") else errors
            has_err = bool(payload) and bool(payload.get("value") if isinstance(payload, dict) else payload)
            f.add(4, "rules compile without error", PASS if not has_err else FAIL,
                  None if not has_err else BLOCKER, obj=cube,
                  expected="no rule errors", observed=str(payload)[:500],
                  evidence="cubes.check_rules()")

        with guarded(f, 4, "rule statement ordering", obj=cube):
            cube_obj = tm1.cubes.get(cube)
            rules = getattr(cube_obj, "rules", None)
            if not rules or not getattr(rules, "text", "").strip():
                f.add(4, "rules present", PASS, INFO, obj=cube,
                      expected="per design document", observed="no rules attached",
                      evidence="cubes.get().rules")
                continue

            text = rules.text
            lines = _significant_lines(text)
            upper = "\n".join(lines).upper()

            has_feeders = "FEEDERS;" in upper
            has_skipcheck = any(ln.upper().startswith("SKIPCHECK") for ln in lines)
            has_feedstrings = any(ln.upper().startswith("FEEDSTRINGS") for ln in lines)

            # SKIPCHECK required whenever feeders exist
            if has_feeders:
                f.add(4, "SKIPCHECK present with FEEDERS",
                      PASS if has_skipcheck else FAIL,
                      None if has_skipcheck else MAJOR, obj=cube,
                      expected="SKIPCHECK when FEEDERS defined",
                      observed=f"FEEDERS={has_feeders}, SKIPCHECK={has_skipcheck}",
                      evidence="rule text scan")

            # FEEDSTRINGS must be the very first significant line, before SKIPCHECK
            produces_string = bool(re.search(r"=\s*S\s*:", text, re.IGNORECASE))
            if produces_string or has_feedstrings:
                first_ok = bool(lines) and lines[0].upper().startswith("FEEDSTRINGS")
                f.add(4, "FEEDSTRINGS is first line",
                      PASS if first_ok else FAIL,
                      None if first_ok else MAJOR, obj=cube,
                      expected="FEEDSTRINGS as first significant line, before SKIPCHECK",
                      observed=f"first line = {lines[0] if lines else '<empty>'!r}; "
                               f"string rules detected = {produces_string}",
                      evidence="rule text scan")

            # ordering: FEEDSTRINGS < SKIPCHECK < rules < FEEDERS
            def idx(pred):
                for i, ln in enumerate(lines):
                    if pred(ln.upper()):
                        return i
                return None

            i_fs = idx(lambda s: s.startswith("FEEDSTRINGS"))
            i_sc = idx(lambda s: s.startswith("SKIPCHECK"))
            i_fd = idx(lambda s: s.startswith("FEEDERS"))
            order = [i for i in (i_fs, i_sc, i_fd) if i is not None]
            ok = order == sorted(order)
            f.add(4, "statement order FEEDSTRINGS/SKIPCHECK/FEEDERS",
                  PASS if ok else FAIL, None if ok else MAJOR, obj=cube,
                  expected="FEEDSTRINGS -> SKIPCHECK -> rules -> FEEDERS",
                  observed=f"line indices FEEDSTRINGS={i_fs} SKIPCHECK={i_sc} FEEDERS={i_fd}",
                  evidence="rule text scan")

            # C: level rules without SKIPCHECK force dense consolidation (gate 10 overlap)
            c_level = bool(re.search(r"=\s*C\s*:", text, re.IGNORECASE))
            if c_level and not has_skipcheck:
                f.add(10, "C-level rules without SKIPCHECK", FAIL, MAJOR, obj=cube,
                      expected="SKIPCHECK present when C: rules exist",
                      observed="C: rules found, no SKIPCHECK — forces dense consolidation",
                      evidence="rule text scan")

            _feeder_breadth(cube, text, spec, f)


def _feeder_breadth(cube: str, text: str, spec: dict, f: Findings) -> None:
    """Heuristic: flag feeder sources that leave a dimension wide open."""
    body = text.upper().split("FEEDERS;", 1)
    if len(body) < 2:
        return
    feeders = body[1]
    broad = re.findall(r"\[[^\]]*\]\s*=>", feeders)
    wide = [b for b in broad if re.search(r"\[\s*\]", b) or b.count("'") == 0]
    if wide:
        f.add(5, "feeder breadth heuristic", FAIL, MINOR, obj=cube,
              expected="feeder sources scoped as narrowly as correctness allows",
              observed=f"{len(wide)} feeder source(s) with an unrestricted dimension: {wide[:5]}",
              evidence="FEEDERS section scan — heuristic, confirm before acting")
    else:
        f.add(5, "feeder breadth heuristic", PASS, obj=cube,
              expected="no unrestricted feeder sources",
              observed=f"{len(broad)} feeder statement(s), none unrestricted",
              evidence="FEEDERS section scan")


# --------------------------------------------------------------------------- #
# Gate 5 — Feeders on sample cells
# --------------------------------------------------------------------------- #

def gate_5_feeders(tm1: TM1Service, spec: dict, f: Findings) -> None:
    samples = spec.get("sample_cells", [])
    if not samples:
        f.unverified(5, "cell feeder check", "no sample_cells supplied in spec")
        return

    for s in samples:
        cube, elements = s["cube"], s["elements"]
        label = f"{cube}[{','.join(elements)}]"

        with guarded(f, 5, "cell is fed", obj=label):
            res = tm1.cells.check_cell_feeders(cube_name=cube, elements=elements)
            fed = _interpret_feeder_result(res)
            if fed is None:
                f.unverified(5, "cell is fed", f"unrecognised response: {str(res)[:300]}", obj=label)
            else:
                f.add(5, "cell is fed", PASS if fed else FAIL,
                      None if fed else BLOCKER, obj=label,
                      expected="fed" if s.get("expect_fed", True) else "not fed",
                      observed="fed" if fed else "NOT FED",
                      evidence="cells.check_cell_feeders()")

        if "expected_value" in s:
            with guarded(f, 7, "value matches independent calculation", obj=label):
                val = tm1.cells.get_value(cube, elements)
                exp = s["expected_value"]
                tol = s.get("tolerance", 0.01)
                ok = val is not None and abs(float(val) - float(exp)) <= tol
                f.add(7, "value matches expected", PASS if ok else FAIL,
                      None if ok else BLOCKER, obj=label,
                      expected=exp, observed=val,
                      evidence=f"cells.get_value(), tolerance={tol}")


def _interpret_feeder_result(res: Any) -> bool | None:
    """check_cell_feeders shape varies by version; be liberal."""
    if isinstance(res, bool):
        return res
    if isinstance(res, dict):
        for key in ("Fed", "fed", "IsFed", "value"):
            if key in res:
                v = res[key]
                if isinstance(v, bool):
                    return v
                if isinstance(v, list):
                    return len(v) > 0
        if "Feeders" in res:
            return bool(res["Feeders"])
    if isinstance(res, list):
        return len(res) > 0
    return None


# --------------------------------------------------------------------------- #
# Gate 6 — TI processes
# --------------------------------------------------------------------------- #

RX_LOCK = re.compile(r"\bCubeLockOn\s*\(", re.IGNORECASE)
RX_UNLOCK = re.compile(r"\bCubeLockOff\s*\(", re.IGNORECASE)


def gate_6_processes(tm1: TM1Service, spec: dict, f: Findings) -> None:
    expected = spec.get("processes", [])

    with guarded(f, 6, "enumerate processes"):
        actual = set(tm1.processes.get_all_names())
        for name in expected:
            present = name in actual
            f.add(6, "process exists", PASS if present else FAIL,
                  None if present else BLOCKER, obj=name,
                  expected=name, observed="present" if present else "missing",
                  evidence="processes.get_all_names()")

    for name in expected:
        with guarded(f, 6, "error log clean", obj=name):
            logs = tm1.processes.get_error_log_filenames(name)
            recent = [l for l in logs]
            ok = not recent
            f.add(6, "no TM1ProcessError log", PASS if ok else FAIL,
                  None if ok else MAJOR, obj=name,
                  expected="no error log after a clean run",
                  observed=f"{len(recent)} log(s): {recent[:5]}",
                  evidence="processes.get_error_log_filenames()")
            if recent:
                head = tm1.processes.get_error_log_file_content(recent[0])[:800]
                f.add(6, "error log excerpt", FAIL, MAJOR, obj=name,
                      expected="", observed=head,
                      evidence=f"get_error_log_file_content({recent[0]})")

        with guarded(f, 6, "lock balance and documentation", obj=name):
            p = tm1.processes.get(name)
            prolog = getattr(p, "prolog_procedure", "") or ""
            epilog = getattr(p, "epilog_procedure", "") or ""
            locks = len(RX_LOCK.findall(prolog + epilog))
            unlocks = len(RX_UNLOCK.findall(prolog + epilog))
            ok = locks == unlocks
            f.add(6, "CubeLockOn/Off balanced", PASS if ok else FAIL,
                  None if ok else MAJOR, obj=name,
                  expected="equal counts", observed=f"On={locks} Off={unlocks}",
                  evidence="prolog/epilog scan")

            has_block = prolog.strip().startswith("#")
            f.add(12, "Prolog comment block present",
                  PASS if has_block else FAIL, None if has_block else MINOR, obj=name,
                  expected="purpose, parameters, dependencies documented in Prolog",
                  observed="present" if has_block else "absent",
                  evidence="prolog_procedure first line")


# --------------------------------------------------------------------------- #
# Gate 9 — Security defaults
# --------------------------------------------------------------------------- #

def gate_9_security(tm1: TM1Service, spec: dict, f: Findings) -> None:
    with guarded(f, 9, "cube security defaults"):
        groups = [g for g in tm1.security.get_all_groups() if g.upper() != "ADMIN"]
        if not groups:
            f.unverified(9, "cube security defaults", "no non-admin user groups defined")
            return
        mdx = (
            "SELECT NON EMPTY {[}Groups].Members} ON 0, "
            "NON EMPTY {[}Cubes].Members} ON 1 FROM [}CubeSecurity]"
        )
        try:
            cells = tm1.cells.execute_mdx(mdx)
        except Exception as exc:
            f.unverified(9, "cube security defaults", f"}}CubeSecurity unreadable: {exc}")
            return

        granted = defaultdict(list)
        for coords, cell in cells.items():
            val = cell.get("Value")
            if val:
                cube = coords[1].split("].[")[-1].rstrip("]")
                grp = coords[0].split("].[")[-1].rstrip("]")
                granted[cube].append(f"{grp}={val}")

        for cube in spec.get("cubes", {}):
            grants = granted.get(cube, [])
            ok = not grants or cube in spec.get("security", {}).get("intentionally_granted", [])
            f.add(9, "new cube defaults to None for non-admin groups",
                  PASS if ok else FAIL, None if ok else BLOCKER, obj=cube,
                  expected="no non-admin grants unless explicitly designed",
                  observed=grants or "no grants",
                  evidence="MDX over }CubeSecurity")


# --------------------------------------------------------------------------- #
# Gate 10/11 — message log, memory, chores
# --------------------------------------------------------------------------- #

def gate_10_11_server(tm1: TM1Service, spec: dict, f: Findings) -> None:
    since_hours = spec.get("message_log_window_hours", 24)

    with guarded(f, 10, "message log scan"):
        since = datetime.now(timezone.utc) - timedelta(hours=since_hours)
        entries = tm1.server.get_message_log_entries(reverse=True, since=since)
        text = [e.get("Message", "") for e in entries]
        rule_errs = [m for m in text if "RULES ERROR" in m.upper()]
        ti_errs = [m for m in text if "TM1.PROCESS" in m.upper() and "ERROR" in m.upper()]
        f.add(4, "no RULES ERROR in message log",
              PASS if not rule_errs else FAIL, None if not rule_errs else BLOCKER,
              expected="0 RULES ERROR entries",
              observed=f"{len(rule_errs)}: {rule_errs[:5]}",
              evidence=f"server.get_message_log_entries(since={since.isoformat()})")
        f.add(6, "no TI errors in message log",
              PASS if not ti_errs else FAIL, None if not ti_errs else MAJOR,
              expected="0 process error entries",
              observed=f"{len(ti_errs)}: {ti_errs[:5]}",
              evidence=f"server.get_message_log_entries(since={since.isoformat()})")

    with guarded(f, 10, "server memory"):
        mdx = ("SELECT {[}StatsStatsByCube].[Total Memory Used]} ON 0, "
               "NON EMPTY {[}Cubes].Members} ON 1 FROM [}StatsByCube]")
        try:
            df = tm1.cells.execute_mdx_dataframe(mdx)
            total = float(df.iloc[:, -1].sum())
        except Exception:
            total = None
        budget = spec.get("memory_budget_bytes")
        if total is None:
            f.unverified(10, "server memory", "}StatsByCube not available (performance monitor off?)")
        elif budget:
            ok = total <= budget
            f.add(10, "memory within expected range", PASS if ok else FAIL,
                  None if ok else MAJOR,
                  expected=f"<= {budget:,} bytes", observed=f"{total:,.0f} bytes",
                  evidence="MDX over }StatsByCube")
        else:
            f.add(10, "memory footprint", PASS, INFO,
                  observed=f"{total:,.0f} bytes", evidence="MDX over }StatsByCube")

    for chore in spec.get("chores", {}):
        with guarded(f, 11, "chore definition", obj=chore):
            c = tm1.chores.get(chore)
            steps = [t.process_name for t in c.tasks]
            exp = spec["chores"][chore].get("process_order")
            if exp:
                ok = steps == exp
                f.add(11, "chore process order", PASS if ok else FAIL,
                      None if ok else MAJOR, obj=chore,
                      expected=exp, observed=steps, evidence="chores.get().tasks")
            else:
                f.add(11, "chore process order", NOT_VERIFIED, INFO, obj=chore,
                      observed=f"no expected order in spec; actual = {steps}")
            f.add(11, "chore active", PASS if c.active else FAIL,
                  None if c.active else MINOR, obj=chore,
                  expected="active per design", observed=f"active={c.active}",
                  evidence="chores.get().active")


# --------------------------------------------------------------------------- #
# INTRINSIC MODE — no design document
#
# The oracle here is the model's own internal consistency plus TM1 engineering
# practice. These checks can prove a model is BROKEN. They cannot prove it is
# RIGHT, because nothing here knows what the model was supposed to compute.
# Read references/intrinsic-checks.md before interpreting a clean run.
# --------------------------------------------------------------------------- #

def discover_spec(tm1: TM1Service, base: dict | None = None) -> dict:
    """Build a spec from the server itself. No expectations, only inventory."""
    spec = dict(base or {})
    spec["_mode"] = "intrinsic"
    spec.setdefault("model_name", spec.get("database", "<discovered>"))

    cubes = tm1.cubes.get_all_names(skip_control_cubes=True)
    dims = tm1.dimensions.get_all_names(skip_control_dimensions=True)

    spec["cubes"] = {c: {} for c in cubes}
    spec["dimensions"] = {}
    for d in dims:
        attrs = []
        try:
            attrs = [a.name for a in tm1.elements.get_element_attributes(d, d)]
        except Exception:
            pass
        spec["dimensions"][d] = {"attributes": attrs, "attribute_min_population": 0.0}

    spec["processes"] = list(tm1.processes.get_all_names())
    spec["chores"] = {c: {} for c in tm1.chores.get_all_names()}
    return spec


def gate_i1_structure(tm1: TM1Service, spec: dict, f: Findings) -> None:
    """Structural defects that are wrong regardless of intent."""
    cubes = list(spec.get("cubes", {}))
    dims = list(spec.get("dimensions", {}))

    with guarded(f, 13, "dimensions used by at least one cube"):
        used: set[str] = set()
        for c in cubes:
            try:
                used.update(x.lower() for x in tm1.cubes.get_dimension_names(c))
            except Exception:
                continue
        for d in dims:
            in_use = d.lower() in used
            f.add(13, "dimension is used by a cube", PASS if in_use else FAIL,
                  None if in_use else MINOR, obj=d,
                  expected="referenced by >= 1 cube",
                  observed="in use" if in_use else "orphan dimension — no cube uses it",
                  evidence="cubes.get_dimension_names() across all cubes")

    for d in dims:
        with guarded(f, 13, "hierarchy shape", obj=d):
            types = tm1.elements.get_element_types(d, d)
            n_leaf = sum(1 for t in types.values() if str(t).lower().startswith("n"))
            n_cons = sum(1 for t in types.values() if str(t).lower().startswith("c"))
            if len(types) == 0:
                f.add(13, "dimension is not empty", FAIL, MAJOR, obj=d,
                      expected="> 0 elements", observed="0 elements",
                      evidence="elements.get_element_types()")
                continue
            f.add(13, "dimension is not empty", PASS, obj=d,
                  observed=f"{len(types)} elements ({n_leaf} N, {n_cons} C)",
                  evidence="elements.get_element_types()")

            hierarchy = tm1.dimensions.hierarchies.get(d, d)
            edges = dict(hierarchy.edges)
            cyc = _find_cycle(edges)
            f.add(13, "no circular consolidation", PASS if not cyc else FAIL,
                  None if not cyc else BLOCKER, obj=d,
                  expected="acyclic hierarchy",
                  observed=cyc or "acyclic", evidence="edge graph walk")

            # a C element with a single child is almost always an accident
            childcount: dict[str, int] = defaultdict(int)
            for (p, _c) in edges:
                childcount[p.lower()] += 1
            singles = [p for p, n in childcount.items() if n == 1]
            if singles:
                f.add(13, "consolidation with a single child", FAIL, MINOR, obj=d,
                      expected="consolidations aggregate >1 child",
                      observed=f"{len(singles)}: {singles[:10]}",
                      evidence="edge child counts")


def _find_cycle(edges: dict) -> str | None:
    graph: dict[str, list[str]] = defaultdict(list)
    for (p, c) in edges:
        graph[p.lower()].append(c.lower())
    WHITE, GREY, BLACK = 0, 1, 2
    colour: dict[str, int] = defaultdict(int)

    def walk(node: str, path: list[str]) -> str | None:
        colour[node] = GREY
        for nxt in graph.get(node, []):
            if colour[nxt] == GREY:
                return " -> ".join(path + [node, nxt])
            if colour[nxt] == WHITE:
                found = walk(nxt, path + [node])
                if found:
                    return found
        colour[node] = BLACK
        return None

    sys.setrecursionlimit(10000)
    for n in list(graph):
        if colour[n] == WHITE:
            hit = walk(n, [])
            if hit:
                return hit
    return None


def gate_i2_consolidation(tm1: TM1Service, spec: dict, f: Findings) -> None:
    """
    The strongest doc-free correctness check.

    For a consolidated cell that is NOT rule-derived, TM1's own default aggregation
    means the cell must equal the weighted sum of its children. A mismatch is a real
    defect — usually a missing feeder or a wrong edge weight — and detecting it needs
    no knowledge of what the model was supposed to compute.
    """
    limit = spec.get("intrinsic", {}).get("consolidation_samples", 12)
    tol = spec.get("intrinsic", {}).get("tolerance", 0.01)
    checked = 0

    for cube in spec.get("cubes", {}):
        if checked >= limit:
            break
        with guarded(f, 14, "consolidation equals sum of children", obj=cube):
            dims = tm1.cubes.get_dimension_names(cube)
            sample = _sample_consolidations(tm1, cube, dims, limit - checked)
            if not sample:
                f.unverified(14, "consolidation equals sum of children",
                             "no consolidated intersection with populated children found",
                             obj=cube)
                continue
            for coords, parent_dim, children in sample:
                checked += 1
                label = f"{cube}[{','.join(coords)}]"
                parent_val = tm1.cells.get_value(cube, list(coords)) or 0

                total = 0.0
                for child, weight in children:
                    kid = list(coords)
                    kid[dims.index(parent_dim)] = child
                    total += (tm1.cells.get_value(cube, kid) or 0) * weight

                rule_derived = _is_rule_derived(tm1, cube, list(coords))
                delta = abs(float(parent_val) - total)

                if rule_derived:
                    f.add(14, "consolidation is rule-derived", PASS, INFO, obj=label,
                          expected="arithmetic check not applicable",
                          observed=f"cell={parent_val}, sum(children)={total}",
                          evidence="cells.trace_cell_calculation()")
                elif delta <= tol:
                    f.add(14, "consolidation equals sum of children", PASS, obj=label,
                          expected=f"{total}", observed=f"{parent_val}",
                          evidence="cells.get_value() over parent and children")
                else:
                    sev = BLOCKER if (parent_val or 0) == 0 and total != 0 else MAJOR
                    f.add(14, "consolidation equals sum of children", FAIL, sev, obj=label,
                          expected=f"sum(children) = {total}",
                          observed=f"cell = {parent_val} (delta {delta})",
                          evidence="cells.get_value(); zero parent with non-zero children "
                                   "is the classic missing-feeder signature")


def _sample_consolidations(tm1: TM1Service, cube: str, dims: list[str], want: int):
    """Yield (coords, parent_dim, [(child, weight)]) for populated consolidated cells."""
    out = []
    for pdim in dims:
        if len(out) >= want:
            break
        try:
            types = tm1.elements.get_element_types(pdim, pdim)
            cons = [e for e, t in types.items() if str(t).lower().startswith("c")]
            if not cons:
                continue
            edges = dict(tm1.dimensions.hierarchies.get(pdim, pdim).edges)
        except Exception:
            continue
        for parent in cons[:3]:
            kids = [(c, w) for (p, c), w in edges.items() if p.lower() == parent.lower()]
            if len(kids) < 2:
                continue
            coords = []
            ok = True
            for d in dims:
                if d == pdim:
                    coords.append(parent)
                    continue
                try:  # hold every other dimension at a leaf
                    leaves = tm1.elements.get_leaf_element_names(d, d)
                    if not leaves:
                        ok = False
                        break
                    coords.append(leaves[0])
                except Exception:
                    ok = False
                    break
            if ok:
                out.append((tuple(coords), pdim, kids))
            if len(out) >= want:
                break
    return out


def _is_rule_derived(tm1: TM1Service, cube: str, coords: list) -> bool:
    try:
        trace = tm1.cells.trace_cell_calculation(cube_name=cube, elements=coords, depth=1)
        blob = json.dumps(trace).lower()
        return "rule" in blob or "statement" in blob
    except Exception:
        return False


def gate_i3_unfed_sweep(tm1: TM1Service, spec: dict, f: Findings) -> None:
    """Rules without feeders, and feeders without rules — both are defects."""
    for cube in spec.get("cubes", {}):
        with guarded(f, 15, "rules have feeders", obj=cube):
            cube_obj = tm1.cubes.get(cube)
            rules = getattr(cube_obj, "rules", None)
            text = getattr(rules, "text", "") if rules else ""
            if not text.strip():
                continue
            upper = text.upper()
            n_rules = len(re.findall(r"=\s*[NCS]\s*:", text, re.IGNORECASE))
            has_feeders = "FEEDERS;" in upper
            n_feeders = len(re.findall(r"=>", upper.split("FEEDERS;", 1)[-1])) if has_feeders else 0

            if n_rules and not has_feeders:
                f.add(15, "rules have a FEEDERS section", FAIL, BLOCKER, obj=cube,
                      expected="FEEDERS section present when rules calculate values",
                      observed=f"{n_rules} rule statement(s), no FEEDERS section — "
                               "with SKIPCHECK these values vanish from consolidations",
                      evidence="rule text scan")
            elif has_feeders and n_feeders == 0:
                f.add(15, "FEEDERS section is populated", FAIL, MAJOR, obj=cube,
                      expected="feeder statements inside FEEDERS section",
                      observed="FEEDERS section present but empty",
                      evidence="rule text scan")
            elif n_rules:
                ratio = n_feeders / n_rules
                low = ratio < 0.5
                f.add(15, "feeder coverage plausible", PASS if not low else FAIL,
                      None if not low else MAJOR, obj=cube,
                      expected="roughly one feeder per rule target area",
                      observed=f"{n_rules} rules / {n_feeders} feeders (ratio {ratio:.2f})",
                      evidence="rule text scan — heuristic, confirm with a cell feeder check")


def gate_i4_hygiene(tm1: TM1Service, spec: dict, f: Findings) -> None:
    """TI and object hygiene that is judgeable without a design document."""
    for name in spec.get("processes", []):
        with guarded(f, 16, "process hygiene", obj=name):
            p = tm1.processes.get(name)
            body = "\n".join(filter(None, [
                getattr(p, "prolog_procedure", ""), getattr(p, "metadata_procedure", ""),
                getattr(p, "data_procedure", ""), getattr(p, "epilog_procedure", ""),
            ]))

            handled = bool(re.search(r"\b(ItemReject|ProcessError|ProcessQuit|ItemSkip)\b",
                                     body, re.IGNORECASE))
            f.add(16, "error handling present", PASS if handled else FAIL,
                  None if handled else MAJOR, obj=name,
                  expected="ItemReject / ProcessError / ProcessQuit somewhere in the process",
                  observed="present" if handled else "no error handling found — "
                           "a bad row loads silently",
                  evidence="process body scan")

            params = [x.get("Name") for x in (getattr(p, "parameters", []) or [])]
            if params:
                validated = all(
                    re.search(rf"\b{re.escape(str(pm))}\b\s*@?=\s*''|"
                              rf"IF\s*\(\s*\w*{re.escape(str(pm))}", body, re.IGNORECASE)
                    for pm in params)
                f.add(16, "parameters validated", PASS if validated else FAIL,
                      None if validated else MAJOR, obj=name,
                      expected="every parameter checked before use",
                      observed=f"parameters {params}; validation "
                               f"{'found' if validated else 'not found for all'}",
                      evidence="process body scan")

            hard = re.findall(r"['\"](?:[A-Za-z]:\\\\|/(?:home|mnt|data)/)[^'\"]{3,}['\"]", body)
            if hard:
                f.add(16, "no hardcoded filesystem paths", FAIL, MINOR, obj=name,
                      expected="paths supplied as parameters or from a control cube",
                      observed=f"{len(hard)}: {hard[:3]}", evidence="process body scan")

            secret = re.search(r"\b(password|passwd|apikey|api_key|secret|token)\b\s*=\s*['\"]",
                               body, re.IGNORECASE)
            if secret:
                f.add(16, "no embedded credentials", FAIL, BLOCKER, obj=name,
                      expected="credentials never literal in TI source",
                      observed=f"possible literal credential near {secret.group(0)!r}",
                      evidence="process body scan")

    with guarded(f, 16, "processes reachable"):
        chore_procs: set[str] = set()
        for ch in spec.get("chores", {}):
            try:
                chore_procs.update(t.process_name.lower() for t in tm1.chores.get(ch).tasks)
            except Exception:
                continue
        for name in spec.get("processes", []):
            if name.lower() not in chore_procs:
                f.add(16, "process is scheduled or manual by design", PASS, INFO, obj=name,
                      expected="informational",
                      observed="not referenced by any chore — confirm this is intentional",
                      evidence="chores.get().tasks")


def gate_i5_conventions(tm1: TM1Service, spec: dict, f: Findings) -> None:
    """Infer the model's own dominant naming convention, then flag the outliers."""
    for kind, names in (("dimension", list(spec.get("dimensions", {}))),
                        ("cube", list(spec.get("cubes", {}))),
                        ("process", list(spec.get("processes", [])))):
        if len(names) < 3:
            f.unverified(17, f"{kind} naming consistency",
                         f"only {len(names)} {kind}(s) — too few to infer a convention")
            continue
        patterns = Counter(_name_shape(n) for n in names)
        dominant, hits = patterns.most_common(1)[0]
        share = hits / len(names)
        outliers = [n for n in names if _name_shape(n) != dominant]
        if share >= 0.6 and outliers:
            f.add(17, f"{kind} naming consistency", FAIL, MINOR,
                  expected=f"dominant shape {dominant!r} ({share:.0%} of {kind}s)",
                  observed=f"{len(outliers)} outlier(s): {outliers[:8]}",
                  evidence="inferred from the model's own names")
        else:
            f.add(17, f"{kind} naming consistency", PASS,
                  expected="a single dominant shape",
                  observed=f"shapes: {dict(patterns)}",
                  evidence="inferred from the model's own names")


def _name_shape(name: str) -> str:
    s = re.sub(r"[A-Z]", "A", name)
    s = re.sub(r"[a-z]", "a", s)
    s = re.sub(r"[0-9]", "9", s)
    s = re.sub(r"a+", "a", s)
    s = re.sub(r"A+", "A", s)
    s = re.sub(r"9+", "9", s)
    return s[:12]


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

INTRINSIC_GATES: dict[int, Callable] = {
    13: gate_i1_structure,
    14: gate_i2_consolidation,
    15: gate_i3_unfed_sweep,
    16: gate_i4_hygiene,
    17: gate_i5_conventions,
}

GATES: dict[int, Callable] = {
    1: gate_1_dimensions,
    2: gate_2_cubes,
    4: gate_4_rules,
    5: gate_5_feeders,
    6: gate_6_processes,
    9: gate_9_security,
    10: gate_10_11_server,
}

ALL_GATES: dict[int, Callable] = {**GATES, **INTRINSIC_GATES}

GATE_NAMES = {
    1: "Dimensions", 2: "Cube structure", 3: "Data entry (manual)",
    4: "Rules", 5: "Feeders", 6: "TI processes",
    7: "Calculation correctness", 8: "Views and PAW", 9: "Security",
    10: "Performance", 11: "Chores", 12: "Documentation",
    13: "Structural integrity", 14: "Consolidation consistency",
    15: "Rule/feeder pairing", 16: "Process hygiene", 17: "Naming consistency",
}

# What conformance mode checks that intrinsic mode structurally cannot.
UNCHECKABLE_WITHOUT_DOC = [
    "Whether the model computes what it was asked to compute — no oracle exists for intent",
    "Element and member counts (nothing to compare against)",
    "Dimension ORDER (any order is internally consistent; only the design says which is right)",
    "Whether an object that exists should exist, or one that is missing is missing",
    "Sign conventions (Actual − Budget vs Budget − Actual are both self-consistent)",
    "Whether security grants are intentional",
    "Whether a rule's business logic is correct, as opposed to syntactically valid",
    "Whether loaded data reconciles to a source system",
]

MANUAL_GATES = {
    3: "writes to cells — run manually, restore original values",
    7: "requires an independent recalculation outside TM1",
    8: "requires PAW interaction",
}


def render_markdown(findings: Findings, spec: dict, counts: dict) -> str:
    intrinsic = spec.get("_mode") == "intrinsic"

    if intrinsic:
        # Intrinsic mode must never issue a sign-off. Nothing here knows what the
        # model was meant to compute, so "no defects found" is the ceiling.
        verdict = ("DEFECTS FOUND — REJECTED" if counts["blocker"]
                   else "DEFECTS FOUND" if counts["fail"]
                   else "NO DEFECTS DETECTED — intent NOT assessed")
    else:
        verdict = ("REJECTED" if counts["blocker"]
                   else "SIGN-OFF WITH CONDITIONS" if counts["fail"] or counts["not_verified"]
                   else "SIGN-OFF")

    out = [
        f"# TM1 Model Validation Report — {spec.get('model_name', '<unnamed>')}",
        "",
        f"**Mode:** {'INTRINSIC (no design document)' if intrinsic else 'CONFORMANCE'}",
        f"**Verdict:** {verdict}",
        "",
        "| | |", "|---|---|",
        f"| Database | {spec.get('database', '')} |",
        f"| PA version | {spec.get('pa_version', 'unspecified')} |",
        f"| Design document | {spec.get('design_document', '') or 'NONE — intrinsic mode'} |",
        f"| Run at | {datetime.now(timezone.utc).isoformat(timespec='seconds')} |",
        "| Harness | tm1_validate.py (read-only) |",
        "",
    ]

    if intrinsic:
        out += [
            "> **This is not a sign-off and cannot become one.** Intrinsic mode checks the "
            "model against its own internal consistency and against TM1 engineering practice. "
            "It can show that a model is broken; it cannot show that it is correct, because "
            "no design document was supplied and nothing here knows what the model was "
            "supposed to compute.",
            "",
            "Not assessed in this mode:",
            "",
        ] + [f"- {x}" for x in UNCHECKABLE_WITHOUT_DOC] + [""]

    out += [
        "## Summary", "",
        "| | Count |", "|---|---|",
        f"| Checks run | {counts['total']} |",
        f"| PASS | {counts['pass']} |",
        f"| FAIL — BLOCKER | {counts['blocker']} |",
        f"| FAIL — MAJOR | {counts['major']} |",
        f"| FAIL — MINOR | {counts['minor']} |",
        f"| NOT_VERIFIED | {counts['not_verified']} |",
        "",
    ]

    if counts["not_verified"]:
        out += ["> NOT_VERIFIED checks are not passes. Resolve or explain each one "
                "before treating this run as a sign-off.", ""]

    order = {BLOCKER: 0, MAJOR: 1, MINOR: 2, INFO: 3}
    fails = sorted((i for i in findings.items if i["result"] == FAIL),
                   key=lambda i: order.get(i["severity"], 9))
    if fails:
        out += ["## Findings", "",
                "| # | Gate | Sev | Object | Expected | Observed | Evidence |",
                "|---|---|---|---|---|---|---|"]
        for n, i in enumerate(fails, 1):
            out.append(
                f"| F-{n:02d} | {i['gate']} {GATE_NAMES.get(i['gate'], '')} | {i['severity']} | "
                f"`{i['object']}` | {_cell(i['expected'])} | {_cell(i['observed'])} | "
                f"`{_cell(i['evidence'])}` |"
            )
        out.append("")

    nv = [i for i in findings.items if i["result"] == NOT_VERIFIED]
    if nv:
        out += ["## Not verified", "", "| Gate | Check | Object | Reason |", "|---|---|---|---|"]
        for i in nv:
            out.append(f"| {i['gate']} | {i['check']} | `{i['object']}` | {_cell(i['observed'])} |")
        out.append("")

    out += ["## Gates requiring manual execution", "",
            "| Gate | Name | Why |", "|---|---|---|"]
    for g, why in MANUAL_GATES.items():
        out.append(f"| {g} | {GATE_NAMES[g]} | {why} |")
    out += ["", "See `references/checklist.md` for the item-level list, and record the "
            "results in `references/report-template.md`.", ""]
    return "\n".join(out)


def _cell(v: Any) -> str:
    s = str(v).replace("|", "\\|").replace("\n", " ")
    return s[:220] + ("…" if len(s) > 220 else "")


# --------------------------------------------------------------------------- #

def connect(spec: dict) -> TM1Service:
    conn = dict(spec.get("connection", {}))
    for key, env in (("user", "TM1_USER"), ("password", "TM1_PASSWORD"),
                     ("address", "TM1_ADDRESS"), ("base_url", "TM1_BASE_URL")):
        if not conn.get(key) and os.getenv(env):
            conn[key] = os.getenv(env)
    if not conn.get("password"):
        sys.exit("No password: set TM1_PASSWORD or put connection.password in the spec.")
    return TM1Service(**conn)


def main() -> int:
    ap = argparse.ArgumentParser(description="TM1 post-build validation harness (read-only)")
    ap.add_argument("--spec", type=Path,
                    help="design document as JSON. Required for conformance mode; in "
                         "intrinsic mode supply it for connection details only.")
    ap.add_argument("--mode", choices=("conformance", "intrinsic"), default="conformance",
                    help="conformance: judge against the design document. "
                         "intrinsic: no design document — internal consistency and TM1 "
                         "engineering practice only. Cannot produce a sign-off.")
    ap.add_argument("--out", default=Path("report"), type=Path)
    ap.add_argument("--gates", help="comma-separated gate numbers, default all automatable")
    args = ap.parse_args()

    spec: dict = {}
    if args.spec:
        if not args.spec.exists():
            sys.exit(f"Spec not found: {args.spec}  (see scripts/README-spec.md)")
        try:
            spec = json.loads(args.spec.read_text())
        except json.JSONDecodeError as exc:
            sys.exit(f"Spec is not valid JSON: {exc}")
    elif args.mode == "conformance":
        sys.exit("Conformance mode needs --spec. For a model with no design document use "
                 "--mode intrinsic (see references/intrinsic-checks.md for what that mode "
                 "can and cannot tell you).")

    findings = Findings()

    with connect(spec) as tm1:
        if args.mode == "intrinsic":
            # Discovery replaces the design document. Expectations are deliberately absent:
            # a discovered spec must never be able to "confirm" the model matches itself.
            spec = discover_spec(tm1, base=spec)
            default_gates = sorted(set(GATES) | set(INTRINSIC_GATES))
        else:
            spec.setdefault("_mode", "conformance")
            default_gates = sorted(GATES)

        selected = ([int(g) for g in args.gates.split(",")] if args.gates else default_gates)

        for g in selected:
            fn = ALL_GATES.get(g)
            if not fn:
                findings.unverified(g, "gate", "not automatable — run manually")
                continue
            try:
                fn(tm1, spec, findings)
            except Exception:
                findings.unverified(g, "gate aborted", traceback.format_exc(limit=3))

    counts = findings.counts()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "findings.json").write_text(
        json.dumps({"counts": counts, "findings": findings.items}, indent=2, default=str))
    (args.out / "report.md").write_text(render_markdown(findings, spec, counts))

    print(json.dumps(counts, indent=2))
    print(f"\nWrote {args.out/'findings.json'} and {args.out/'report.md'}")
    return 1 if counts["blocker"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
