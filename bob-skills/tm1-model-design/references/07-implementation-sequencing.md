# Implementation Sequencing — TM1 Design Reference

TM1 objects have hard dependencies. Build them in the wrong order and TI processes
will fail, rules will error, and cubes cannot be created. This file defines the
correct sequence and a phased roadmap template.

---

## 1. Dependency graph — why order matters

```
Security Groups
      │
      ▼
Dimensions ──────────────────────────────┐
  (elements, attributes, hierarchies)    │
      │                                  │
      ▼                                  │
Cubes                                    │
  (require dimensions to exist first)   │
      │                                  │
      ▼                                  │
Rules files                              │
  (reference cube and dimension names)  │
      │                                  │
      ▼                                  │
TI Processes                             │
  (reference cubes and dimensions;       │
   load data into cubes)                │
      │                                  │
      ▼                                  │
Chores                                  │
  (schedule TI processes)               │
      │                                  │
      ▼                                  │
Views ◄──────────────────────────────────┘
  (require cubes + dimensions)
      │
      ▼
PAW Books
  (embed views; require views to exist)
      │
      ▼
Security assignments
  (grant groups access to objects)
```

---

## 2. Phased implementation roadmap template

### Phase 1 — Foundation (Week 1–2)

**Goal:** All dimensions and cubes exist with correct structure; rates loaded.

| Step | Task | Dependency | Verify |
|------|------|-----------|--------|
| 1.1 | Create security groups | None | Groups visible in TM1 security |
| 1.2 | Create all dimensions (elements, attributes, hierarchies) | Security groups | Dimension members visible in PAW |
| 1.3 | Create `[Module].BuildModel` TI process | Dimensions designed | Process exists; syntax validates |
| 1.4 | Execute `BuildModel` — creates cubes | All dimensions exist | Cubes visible in PAW; correct dimension count |
| 1.5 | Write and save rules file for Trip Detail cube | Cube exists | No syntax errors; rules file saved |
| 1.6 | Create `[Module].LoadRates` TI process | Rates cube exists | Process exists |
| 1.7 | Prepare rates CSV file | — | File exists; correct column order |
| 1.8 | Execute `LoadRates` | Rates cube + rates CSV | Data visible in Rate Maintenance view |
| 1.9 | Test `Amount = Rate × Quantity` rule | Rules file + rates | Enter test Quantity; Amount calculates correctly |

**Phase 1 exit criteria:**
- [ ] All cubes created with correct dimensions
- [ ] Rules file active — Amount calculates from Rate × Quantity
- [ ] Rates loaded for all 5 cost categories
- [ ] No TM1 error logs

---

### Phase 2 — Input and Reporting (Week 3)

**Goal:** Users can enter trip data; management can view summaries.

| Step | Task | Dependency | Verify |
|------|------|-----------|--------|
| 2.1 | Create `[Module].DefaultRatesToTrips` TI process | Trip Detail cube + Rates cube | Process exists |
| 2.2 | Execute `DefaultRatesToTrips` | Phase 1 complete | Rate cells populated in Trip Detail for all trips |
| 2.3 | Build Trip Entry view in PAW | Trip Detail cube | View displays correct rows/columns; Amount is read-only |
| 2.4 | Build Monthly Summary view in PAW | Trip Detail cube | View aggregates trips to monthly totals correctly |
| 2.5 | Build Rate Maintenance view | Rates cube | Admin can update rates |
| 2.6 | Test end-to-end: enter Quantity → view Amount → check Monthly Summary | All of above | Monthly total matches sum of trip Amounts |
| 2.7 | Validate monthly consolidation | — | "Total Trips" rolls up correctly across all trips |

**Phase 2 exit criteria:**
- [ ] Trip entry works end-to-end for at least one route and one trip
- [ ] Monthly Summary correctly aggregates from Trip Detail
- [ ] Amount cell cannot be edited in PAW (read-only enforced)
- [ ] Rate Maintenance view updates rates correctly

---

### Phase 3 — Process Automation (Week 4)

**Goal:** Full TI process suite in place; chores scheduled.

| Step | Task | Dependency | Verify |
|------|------|-----------|--------|
| 3.1 | Complete `[Module].ClearTripData` process | Trip Detail cube | Clears only target version/month/department |
| 3.2 | Complete `[Module].ExportMonthlyBudget` process | Summary view/cube | CSV export matches Monthly Summary view |
| 3.3 | Create chore for nightly rate refresh (if rates change) | `LoadRates` process | Chore scheduled; runs without error |
| 3.4 | Create chore for monthly summary aggregation (if separate Summary cube used) | `AggregateSummary` process | Chore scheduled |
| 3.5 | Test `ClearTripData` — verify it clears only the target scope | — | Other departments/versions unaffected |
| 3.6 | Test `ExportMonthlyBudget` — verify file output | — | CSV correct; matches PAW view |

---

### Phase 4 — Security and UAT (Week 5)

**Goal:** Security enforced; users validated; model signed off.

| Step | Task | Dependency | Verify |
|------|------|-----------|--------|
| 4.1 | Assign groups to cubes (None → Write/Read per role) | All cubes; security groups | `TravelBudgetOwner` can write Trip Detail; cannot write Rates |
| 4.2 | Configure cell security for Amount (if not using PAW read-only) | Cell security cube | Amount cannot be entered by any group |
| 4.3 | Configure dimension security (department filtering) | Security groups | Each department owner sees only their data |
| 4.4 | UAT — budget analyst enters trips | Phase 1–3 complete | Amounts calculate; monthly summary correct |
| 4.5 | UAT — finance reviews Monthly Summary | — | Totals match; drill-down works |
| 4.6 | UAT — admin updates rates → verify repricing | — | Changing a rate updates all Amounts instantly |
| 4.7 | Performance check — large trip count | — | Monthly Summary view loads in < 5 seconds |
| 4.8 | Documentation and user training | — | User guide; training session delivered |

---

## 3. Common sequencing mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Creating cube before dimensions exist | `CubeCreate` fails — dimension not found | Always create all dimensions in Prolog before `CubeCreate` |
| Loading data before elements exist | "Invalid key" error in TI log | Use atomic single-process: elements before data load |
| Writing rules file before cube exists | Rules file cannot be attached | Create cube first; then attach rules |
| Assigning security before objects exist | Security assignment silently fails | Create objects first; security last |
| Building PAW views before cube has data | Empty views confuse UAT testers | Load at least test data in Phase 1 before building views |
| Running `ClearTripData` without scope parameters | Clears entire cube | Always validate pVersion / pDepartment parameters before clearing |

---

## 4. Rollback plan

If a phase fails, roll back in reverse dependency order:

```
1. Delete PAW books and views
2. Delete chores
3. Delete TI processes
4. Delete rules files (detach from cube)
5. Delete cubes
6. Delete dimensions
7. Delete security groups
```

For most recoveries, only steps 1–4 are needed (structural changes rarely require
deleting dimensions and cubes once they are correct).
