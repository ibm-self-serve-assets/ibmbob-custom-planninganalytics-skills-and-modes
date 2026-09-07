# Naming Conventions — TM1 Design Reference

Consistent naming is one of the most important decisions in a TM1 model. Names are
permanent — renaming objects later breaks rules, feeders, TI processes, views, and
PAW books. Agree on conventions before building anything.

---

## 1. General naming rules

| Rule | Rationale |
|------|-----------|
| Use Title Case for all object names | Consistent across the model; readable in PAW |
| Use spaces (not underscores or camelCase) for display names | TM1 supports spaces; they read better in views and PAW |
| Use a consistent **module prefix** for all objects in a model | Prevents name collisions when multiple models share a server |
| Keep names meaningful and self-documenting | A developer reading a rules file should immediately understand `[Travel Measure:'Amount']` |
| Avoid abbreviations except for well-known codes (SYD, MEL, Q1) | Cryptic names become a maintenance burden |
| Maximum length guideline: 64 characters for cubes/dimensions; 32 for members | Long names cause display truncation in some PAW views |

---

## 2. Cubes

**Pattern:** `[Module] - [Purpose]`

| Object | Example |
|--------|---------|
| Input / detail cube | `Travel Budget - Trip Detail` |
| Rates / reference cube | `Travel Budget - Rates` |
| Summary / reporting cube | `Travel Budget - Monthly Summary` |
| Security cube | `}ElementSecurity_Travel Budget - Trip Detail` *(TM1 auto-names security cubes with `}` prefix)* |

**Rules:**
- Always prefix with the module name (`Travel Budget`)
- Separate module and purpose with ` - ` (space-dash-space)
- Do not suffix with "Cube" — it is redundant

---

## 3. Dimensions

**Pattern:** `[Module] [Concept]`

| Dimension | Example |
|-----------|---------|
| Routes | `Travel Route` |
| Cost types | `Travel Cost Category` |
| Measures | `Travel Measure` |
| Time | `Travel Month` |
| Version | `Travel Version` |
| Organisation | `Travel Department` |
| Trip instances | `Travel Trip` |

**Rules:**
- Always prefix with the module name
- Singular noun (not plural): `Travel Route`, not `Travel Routes`
- Use `Measure` (not `Measures`) for the measures dimension

---

## 4. Dimension members

### Consolidation members

**Pattern:** `[Adjective/Preposition] [Noun]` or `All [Noun]`

| Member type | Example |
|-------------|---------|
| Top total | `All Routes`, `Total Travel Costs`, `All Departments` |
| Origin group | `From Sydney`, `From Melbourne` |
| Time total | `FY2026`, `Q1 FY2026` |
| Version group | `All Versions` |

### Leaf members (N-type)

**Pattern:** Meaningful, human-readable, no abbreviations except well-known codes

| Member type | Pattern | Example |
|-------------|---------|---------|
| Routes | `[ORIGIN CODE] - [DEST CODE]` | `SYD - MEL`, `PER - BNE` |
| Months | `[Mon] [YYYY]` | `Jan 2026`, `Feb 2026` |
| Trips | `Trip [NNN]` (zero-padded) | `Trip 001`, `Trip 050`, `Trip 200` |
| Cost categories | Full name | `Airfares`, `Hotel`, `Car Hire`, `Taxi / Rideshare`, `Incidentals` |
| Measures | Single word or short phrase | `Rate`, `Quantity`, `Amount` |
| Versions | Full name | `Budget`, `Revised Budget`, `Forecast` |

**Zero-padding for trips:** Use `Trip 001` not `Trip 1` — ensures alphanumeric sort
order is correct. Without zero-padding: `Trip 1`, `Trip 10`, `Trip 100`, `Trip 2`...

---

## 5. TurboIntegrator processes

**Pattern:** `[Module].[ActionVerb][Object]`

| Purpose | Name |
|---------|------|
| Build all dimensions and cubes | `Travel.BuildModel` |
| Load rates from file | `Travel.LoadRates` |
| Copy rates to trip detail | `Travel.DefaultRatesToTrips` |
| Clear trip data | `Travel.ClearTripData` |
| Aggregate to summary cube | `Travel.AggregateSummary` |
| Export monthly budget | `Travel.ExportMonthlyBudget` |
| Validate data quality | `Travel.ValidateData` |

**Rules:**
- Use dot notation: `Module.Action` — groups related processes alphabetically in the process list
- Action verb first: `Load`, `Clear`, `Export`, `Build`, `Default`, `Validate`
- No spaces in process names — use PascalCase within the dot segments

---

## 6. Views

**Pattern:** `[Module] - [Purpose] - [Audience]`

| View | Name |
|------|------|
| Trip input view | `Travel Budget - Trip Entry - Analyst` |
| Management summary | `Travel Budget - Monthly Summary - Management` |
| Rate maintenance | `Travel Budget - Rate Maintenance - Admin` |
| Version comparison | `Travel Budget - Version Comparison - Finance` |
| Outlier check | `Travel Budget - Outlier Review - Finance` |

**Rules:**
- Match the cube's module prefix
- Audience suffix helps users find the right view in PAW

---

## 7. PAW books

**Pattern:** `[Module] [FY or Period] [Audience]`

| Book | Name |
|------|------|
| Main budget entry book | `Travel Budget FY2026 Analysts` |
| Management reporting book | `Travel Budget FY2026 Management` |
| Admin / setup book | `Travel Budget Admin` |

---

## 8. Chores (scheduled processes)

**Pattern:** `Chore.[Module].[Description]`

| Chore | Name |
|-------|------|
| Nightly rate refresh | `Chore.Travel.NightlyRateRefresh` |
| Monthly summary aggregation | `Chore.Travel.MonthlySummaryAggregation` |
| Weekly data export | `Chore.Travel.WeeklyExport` |

---

## 9. Security groups

**Pattern:** `[Module][Role]`

| Role | Group name |
|------|-----------|
| Model administrators | `TravelAdmin` |
| Department budget owners | `TravelBudgetOwner` |
| Read-only viewers | `TravelViewer` |
| Rate maintainers | `TravelRateMaintainer` |

---

## 10. Rules file comments

Every rules file should start with a header comment:

```
# ============================================================
# Cube:    Travel Budget - Trip Detail
# Purpose: Driver-based calculation — Amount = Rate × Quantity
# Model:   Australia Travel Budget
# Version: PA latest
# Updated: [date]
# ============================================================
```

---

## 11. Naming convention checklist

Before finalising a model design, verify:

- [ ] All cube names use `Module - Purpose` pattern
- [ ] All dimension names use `Module Concept` pattern (singular)
- [ ] Trip members are zero-padded (`Trip 001`, not `Trip 1`)
- [ ] TI processes use `Module.ActionVerb` pattern with no spaces
- [ ] Views use `Module - Purpose - Audience` pattern
- [ ] Security group names follow `ModuleRole` pattern
- [ ] No object name contains a reserved TM1 character (`}`, `!`, `[`, `]`)
- [ ] No two objects of the same type have the same name
