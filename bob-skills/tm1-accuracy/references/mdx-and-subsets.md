# MDX and Dynamic Subsets — Verified Reference

> **Version note:** The facts in this file were validated against **PA 2.1**.
> When this skill is used for a different version, verify against the target version's docs.
> Replace `<VERSION>` with `latest` (default) or the explicit version from the prompt.

Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=mfs-tm1-specific-mdx-functions`
Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=data-guidelines-writing-tm1-rules-statements`

---

## Standard MDX in TM1

TM1 supports a subset of MDX (MultiDimensional eXpressions). The basic query structure:

```mdx
SELECT
  { [DimA].[DimA].[MemberX], [DimA].[DimA].[MemberY] } ON COLUMNS,
  { [DimB].[DimB].MEMBERS } ON ROWS
FROM [CubeName]
WHERE ([DimC].[DimC].[MemberZ])
```

- **ON COLUMNS** = Axis 0
- **ON ROWS** = Axis 1
- **WHERE** clause = slicer (filters, not rows/columns)
- Member references use `[Dimension].[Hierarchy].[Member]` format

---

## NON EMPTY — correct usage

`NON EMPTY` suppresses rows or columns where all cells are empty (zero or null).
It is applied **per axis independently**:

```mdx
SELECT
  NON EMPTY { [Product].[Product].MEMBERS } ON COLUMNS,
  NON EMPTY { [Month].[Month].MEMBERS } ON ROWS
FROM [Sales]
```

**Common mistake:** stating that `NON EMPTY` applies to the entire query or to the WHERE
clause. It does not — it applies only to the axis it qualifies.

---

## TM1-specific MDX functions

These functions are **TM1-specific** — they are not part of standard MDX and are not
available in other MDX-compliant tools (SSAS, SAP BW, etc.). Always label them as
TM1-specific when teaching them.

Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=mfs-tm1-specific-mdx-functions`

| Function | Description |
|----------|-------------|
| `TM1DISTINCT(<set>)` | Removes duplicate members from a set (including parent context check) |
| `TM1DRILLDOWNMEMBER(<set1>, <set2>\|ALL [,RECURSIVE])` | Expands members — mirrors the Subset Editor Expand button behaviour |
| `TM1FILTERBYPATTERN(<set>, <pattern> [,<attribute>])` | Filters set members by name pattern or attribute value |
| `TM1FILTERBYLEVEL(<set>, <level_number>)` | Returns only members at a specified level |
| `TM1Member` | Returns a member from a specified tuple |
| `TM1SORT(<set>, ASC\|DESC)` | Sorts a set alphabetically |
| `TM1SORTBYINDEX(<set>, ASC\|DESC)` | Sorts a set by member index value |
| `TM1SUBSETALL([<dimname>])` | Returns the TM1 "All" subset for a dimension |
| `TM1SubsetToSet(<dim>, <subset>)` | Returns members of a named TM1 subset as an MDX set |
| `TM1TupleSize` | Returns the number of members in a tuple |

---

## Dynamic subsets — MDX expressions in the Subset Editor

A dynamic subset stores an MDX expression rather than a static member list. The MDX
evaluates at runtime and the subset membership can change as data changes.

```mdx
# Dynamic subset — all leaf members of Products dimension
{TM1FILTERBYLEVEL({[Products].[Products].MEMBERS}, 0)}
```

Level 0 = leaf (N-type) elements. Level 1 = first consolidation level, etc.

```mdx
# Dynamic subset — members matching a pattern
{TM1FILTERBYPATTERN({[Accounts].[Accounts].MEMBERS}, 'Rev*')}
```

---

## DESCENDANTS function

```mdx
DESCENDANTS([Dim].[Hier].[ConsolidatedMember], <level>, LEAVES)
```

Returns all descendants at or below the specified level. `LEAVES` restricts to leaf
members only. This is standard MDX, not TM1-specific.

---

## CrossJoin

```mdx
CrossJoin({[Dim1].MEMBERS}, {[Dim2].MEMBERS})
```

Returns the Cartesian product of two sets. Can produce large result sets on big
dimensions — always combine with `NON EMPTY` or filter functions.

`NonEmptyCrossjoin` is an alternative that excludes empty tuples:

```mdx
NonEmptyCrossjoin({[Dim1].MEMBERS}, {[Dim2].MEMBERS}, 2)
```

The third argument specifies how many sets to check for emptiness.
