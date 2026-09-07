# Dimensions, Hierarchies, and Cube Modelling — Verified Reference

> **Version note:** The facts in this file were validated against **PA 2.1**.
> When this skill is used for a different version, verify against:
> `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=metadata-entity-types`
> Use `latest` in place of `<VERSION>` when no version is specified in the prompt.

Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=metadata-entity-types`

---

## Element types — exactly three

TM1 elements have exactly three types. Content that describes other types is incorrect.

| Type code | Name | Description |
|-----------|------|-------------|
| **N** | Numeric | Leaf element — holds data values. Can be a direct input cell or a rules-calculated cell. |
| **C** | Consolidated | Aggregation element — rolls up its components. Cannot hold direct input (writes go to the N-level children). |
| **S** | String | Holds string (text) values. Can be at leaf or consolidation level. |

**Level 0** in the hierarchy = leaf elements (N or S type).
**Each consolidation level** increments by 1 going upward.

---

## Hierarchy and dimension structure

```
Dimension
  └── Hierarchy (one or more; default hierarchy = same name as dimension)
        └── Element (N, C, or S)
              └── Components (for C elements — the children)
```

A dimension has a **default hierarchy** with the same name as the dimension.
Alternate hierarchies are supported but less commonly used in standard implementations.

---

## Attributes

Attributes store metadata about dimension elements:

| Attribute type | Use for |
|----------------|---------|
| String attribute | Descriptive text (e.g., `Manager`, `Region`) |
| Numeric attribute | Numeric metadata (e.g., `SortOrder`, `BudgetWeight`) |
| Alias attribute | Alternative display name for an element |

Aliases are a special category of String attribute. A dimension can have multiple alias
attributes. In views, users can switch between the element name and any alias.

Access attributes in rules using `ATTRS()` and `ATTRN()`:

```
ATTRS('Products', !Products, 'Category')   # String attribute
ATTRN('Products', !Products, 'SortOrder')  # Numeric attribute
```

---

## Cube design principles

### Measures dimension

Best practice: every cube should have a dedicated **Measures** (or equivalent) dimension
that contains all the metrics the cube stores (Revenue, Units, Price, etc.).
This makes rules scoping and feeder targeting precise.

### Sparsity

TM1 stores data **sparsely** — only cells with non-zero values consume memory.
A cube with many dimensions may have a very large theoretical size but a tiny actual
footprint if most intersections are empty.

**Implication for rules:** Rules-derived values exist in memory only if they are
**fed**. Without SKIPCHECK + FEEDERS, a rules-calculated cell at a
consolidation level may be skipped during aggregation if no data exists beneath it.

### Dimension ordering in cubes

Dimension order affects performance. General guidance:

1. Place **Measures** last (or as the last few dimensions)
2. Place **high-cardinality** dimensions (many members) towards the end
3. Place **low-cardinality** dimensions (few members — e.g., Version, Scenario) early

This is guidance, not a hard rule — the optimal order depends on the query patterns.

---

## Virtual dimensions (alias dimensions)

A virtual dimension is a dimension that exists in a cube but whose elements are drawn
from an attribute of another dimension. Rarely used in standard modelling; documented
here because the concept appears in advanced content and is sometimes incorrectly
described as a "calculated dimension."

---

## Sandboxes

A sandbox is a **private what-if data layer** over one or more cubes. Changes made
in a sandbox are visible only to the user who owns it, until the sandbox is published
or discarded.

- Sandboxes do not affect the base (published) data
- TI processes executed against a server run against the base data unless the sandbox
  is explicitly specified in the API call
- Sandboxes are created and managed per-user in PAW or via the REST API
