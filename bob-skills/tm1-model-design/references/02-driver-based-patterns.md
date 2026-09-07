# Driver-Based Model Patterns — TM1 Design Reference

> **Accuracy foundation:** Rules syntax and feeder patterns are verified in
> `tm1-accuracy/references/rules-and-feeders.md`. Cross-check all rule
> statements and feeder declarations against that file.

---

## 1. What is a driver-based model?

A driver-based model derives every cost or revenue line from a **formula**, not a
manual dollar entry:

```
Budget Amount = Rate × Quantity
```

| Component | Who provides it | Example |
|-----------|----------------|---------|
| **Rate** | Finance / procurement (standard rates) | $220 per hotel night |
| **Quantity** | Business user (planning input) | 3 nights |
| **Amount** | TM1 rule (never entered) | $660 |

**Benefits:**
- Transparent — anyone can see exactly why a number is what it is
- Auditable — changing the rate reprices every trip instantly
- Consistent — no two users can enter the same trip at different costs

---

## 2. Standard cube triad

Every driver-based model uses three cubes working together:

### Cube 1: Rates Reference cube

Holds standard rates by cost category, optionally by route/version/period.
- **Input:** Finance / procurement admin only
- **No planning input from business users**
- **Dimensions:** typically Route (or destination), Cost Category, Rate Measure, Version, Month

```
Travel Budget - Rates
├── Travel Route           (rates can differ by route — e.g. Perth flights cost more)
├── Travel Cost Category   (Airfares, Hotel, Car Hire, Taxi, Incidentals)
├── Travel Rate Measure    (Rate, Unit Description)
├── Travel Version         (Budget, Revised Budget)
└── Travel Month           (rates may vary by period)
```

### Cube 2: Detail / Input cube

One record per trip. Business users enter Quantity; Rate is defaulted from the
Rates cube via a TI process or DB() rule; Amount is always rule-calculated.
- **Input:** Budget analysts — Quantity only
- **Rate cells:** defaulted by TI, overridable if business rules permit
- **Amount cells:** read-only — protected in PAW input view

```
Travel Budget - Trip Detail
├── Travel Version
├── Travel Department
├── Travel Route
├── Travel Cost Category
├── Travel Month
├── Travel Trip            (Trip 001, Trip 002 … Trip 200)
└── Travel Measure         (Rate | Quantity | Amount)
```

### Cube 3: Summary / Reporting cube (optional)

Aggregates trip-level detail to a monthly summary for management reporting.
Can be achieved by:
- **Option A (preferred):** Use a view of the Detail cube with the Trip dimension
  consolidated to "Total Trips" — no separate cube needed
- **Option B:** A separate Summary cube populated by a TI aggregation process —
  use when report performance on the Detail cube is unacceptable

---

## 3. Data flow design

```
┌─────────────────────────────────────────┐
│ RATES CUBE                               │
│ Standard rates loaded by admin via TI    │
│ or maintained in Rate Maintenance view   │
└──────────────────┬──────────────────────┘
                   │ DB() rule pulls rate into Trip Detail
                   │ OR TI process copies rates to Trip Detail
                   ▼
┌─────────────────────────────────────────┐
│ TRIP DETAIL CUBE                         │
│ User enters: Quantity                    │
│ Rate: defaulted (overridable)            │
│ Amount = Rate × Quantity  ← TM1 Rule    │
└──────────────────┬──────────────────────┘
                   │ TM1 native consolidation
                   │ (Trip dimension rolls up to "Total Trips")
                   ▼
┌─────────────────────────────────────────┐
│ MONTHLY SUMMARY VIEW / CUBE              │
│ Amount at "Total Trips" × Month × Route  │
│ Management reporting, no input           │
└─────────────────────────────────────────┘
```

---

## 4. Rate sourcing — two approaches

### Approach A: DB() rule (recommended for live rate lookups)

The Trip Detail cube pulls its Rate directly from the Rates cube at query time:

```
# In Travel Budget - Trip Detail rules file
[Travel Measure:'Rate'] = N:
    DB('Travel Budget - Rates',
       !Travel Route,
       !Travel Cost Category,
       'Rate',
       !Travel Version,
       !Travel Month);
```

**Pros:** Always current — changing a rate in the Rates cube immediately reprices all trips.
**Cons:** Adds a cross-cube DB() call to every Rate cell; minor performance overhead.

### Approach B: TI copy process (recommended for large models)

A TurboIntegrator process `Travel.DefaultRatesToTrips` runs at budget cycle start and
copies rates from the Rates cube into the Trip Detail cube's Rate cells.
Users can then override individual Rate cells for specific trips.

**Pros:** Rate cells in Trip Detail are plain data — no DB() overhead; override is simple.
**Cons:** Rates in Trip Detail become stale if the Rates cube is updated after the copy runs.
Must re-run the TI process to refresh.

**Design decision guide:**

| If… | Use |
|-----|-----|
| Rates change frequently during the budget cycle | Approach A (DB()) |
| Trip count is large (>1,000 trips) and query performance matters | Approach B (TI copy) |
| Users need to override rates on a per-trip basis | Approach B (TI copy) |
| Model is small and simplicity is preferred | Approach A (DB()) |

---

## 5. Cost category design

Standard five cost categories for travel models. Adapt as needed:

| Cost Category | Rate basis | Quantity basis | Notes |
|---|---|---|---|
| Airfares | $ per ticket (return economy) | Number of tickets | Route-specific — Perth costs more |
| Hotel | $ per room per night | Number of nights | Destination-based rate |
| Car Hire | $ per day | Number of rental days | Optional — quantity = 0 if not needed |
| Taxi / Rideshare | $ per trip | Number of taxi trips | Both ends of travel |
| Incidentals | $ per traveller per day | Number of traveller-days | At destination only |

**Adding new categories:** Add the leaf member to `Travel Cost Category`, add a rate
in the Rates cube, and the Amount rule applies automatically — no rule change needed.

---

## 6. Version design for driver-based models

```
All Versions
├── Budget          ← Annual budget (driver-based, Rate × Quantity)
├── Revised Budget  ← Mid-year reforecast (same structure as Budget)
└── Forecast        ← Rolling forecast (may have fewer periods)
```

**Design rule:** All versions use the same cube structure and the same rules.
Do not create separate cubes per version.

---

## 7. Trip dimension sizing

| Consideration | Guidance |
|---|---|
| How many trip slots? | Start with 200 (Trip 001–Trip 200). TM1's sparse storage means unused trips cost no memory. |
| What if we exceed the pool? | Add more members — dimension rebuild is straightforward |
| Naming | Use zero-padded numbers (`Trip 001`, not `Trip 1`) for correct sort order |
| Top consolidation | `Total Trips` — this is what the Summary view shows |

---

## 8. Design anti-patterns to avoid

| Anti-pattern | Problem | Correct approach |
|---|---|---|
| Amount entered manually | Bypasses the driver logic; inconsistent with other trips | Amount is always rule-derived; protect in PAW |
| One cube per cost category | Proliferates cubes; hard to report across categories | Use a Cost Category dimension in one cube |
| Rate hardcoded in the rule | Rate changes require a rules file edit and model restart | Rates always live in the Rates cube |
| No separate Rates cube | Rates mixed with planning data; no clean separation of concerns | Always use a dedicated Rates reference cube |
| Quantity entered as a dollar amount | Destroys the Rate × Quantity logic | Train users: Quantity is always a unit count |
