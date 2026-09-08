# Planning Analytics Skill

A comprehensive BOB skill for exploring IBM Planning Analytics and TM1 data through natural language queries, providing business-focused insights and executive-ready reporting.

## Overview

This skill transforms Planning Analytics into an accessible business intelligence platform, enabling users to:

- 🗣️ **Natural Language Queries** - Ask questions in plain English, not MDX
- 📊 **Variance Analysis** - Budget vs Actual, Forecast vs Actual, Period-over-Period
- 🔍 **Outlier Detection** - Identify anomalous patterns requiring attention
- 📈 **Key Driver Analysis** - Understand what's driving your results
- 📄 **Executive Reports** - Professional, business-ready formatting

## What This Skill Does

When you ask a business question, this skill:

1. **Understands Your Intent** - Translates natural language to TM1 queries
2. **Finds the Right Data** - Selects appropriate cubes, dimensions, and members
3. **Applies Intelligence** - Uses consolidations, time periods, and filters intelligently
4. **Delivers Insights** - Returns formatted results with business context
5. **Explains Choices** - Shows why certain data was selected

## Quick Start

### Example Queries

```
"Show Q1 2025 compensation budget vs actual by department"
"What's driving revenue variance in the East region?"
"Find unusual expense patterns in March"
"Compare this year to last year by product"
"Show sales trends over the last 12 months"
```

### Example Output

```markdown
📊 Q1 2025 Compensation Budget vs Actual by Department

**Server:** 24Retail
**Cube:** Compensation
**Period:** Q1 2025

| Department | Budget | Actual | Variance ($) | Variance (%) |
|------------|--------|--------|--------------|--------------|
| **Total Company** | **$50,638** | **$50,638** | **$0** | **0.0%** |
| East Region | $50,638 | $50,638 | $0 | 0.0% |
| └─ Massachusetts | $50,638 | $50,638 | $0 | 0.0% |
| Central Region | $0 | No Data | - | - |
| West Region | $0 | No Data | - | - |

**Key Findings:**
- Total Q1 compensation matched budget exactly ($0 variance)
- All activity concentrated in Massachusetts
- Other regions show no budget or actual data for Q1

**Data Notes:**
- Only Massachusetts shows active compensation data
- May indicate preliminary data or no employees assigned to other regions
```

## Key Features

### 1. Semantic Data Exploration

Works with **pre-analyzed cubes** that have AI-generated metadata:

- Understands business terminology
- Maps concepts to TM1 structures automatically
- Applies intelligent defaults
- Explains data selection choices

**Example:**
```
Query: "Show sales in May 2023"

System automatically:
- Selects Sales cube
- Finds May in Month dimension
- Finds 2023 in Year dimension
- Applies appropriate consolidations
- Returns formatted results
```

### 2. Financial Analysis

#### Variance Analysis
Compare different versions of your data:
- Budget vs Actual
- Forecast vs Actual
- Prior Year vs Current Year
- Plan vs Revised Plan

#### Trend Analysis
Identify patterns over time:
- Growth rates
- Seasonal variations
- Moving averages
- Trend direction

#### Outlier Detection
Find anomalies using multiple algorithms:
- Statistical outliers
- Unusual patterns
- Threshold violations
- Contextual explanations

#### Key Driver Analysis
Understand what's driving results:
- Impact analysis
- Sensitivity analysis
- Factor importance
- Actionable insights

### 3. Executive Reporting

Professional, business-ready output:
- Clean table formatting
- Hierarchical structures
- Key findings summaries
- Data quality notes
- Actionable recommendations

### 4. TM1 Expertise

Get guidance on:
- Cube design best practices
- Dimension structure recommendations
- Rule and feeder development
- Performance optimization
- Security model design
- Migration strategies

## Use Cases

### Financial Planning & Analysis
- Monthly variance reviews
- Budget vs actual analysis
- Forecast accuracy tracking
- Scenario comparison
- What-if analysis

### Performance Management
- KPI tracking and monitoring
- Trend analysis
- Goal vs actual comparison
- Department performance reviews
- Regional comparisons

### Data Quality & Governance
- Outlier identification
- Data completeness checks
- Consistency validation
- Audit trail analysis

### Strategic Planning
- Long-term trend analysis
- Scenario modeling
- Key driver identification
- Risk assessment

## How It Works

### Step 1: Ask Your Question
Use natural language to describe what you want to see:
```
"Show me Q1 compensation variance by department"
```

### Step 2: Skill Processes Query
The skill:
- Identifies relevant cube (Compensation)
- Maps business terms to dimensions
- Selects appropriate members
- Applies intelligent defaults

### Step 3: Retrieve Data
Uses MCP tools to:
- Query TM1 server
- Execute MDX if needed
- Retrieve formatted results

### Step 4: Generate Insights
Delivers:
- Formatted data tables
- Key findings
- Business context
- Data quality notes
- Recommendations

## Technical Details

### MCP Tools Integration

This skill uses the following MCP tools:

**Data Exploration:**
- `get_data_from_data_explorer` - Semantic queries on pre-analyzed cubes
- `get_MDX_for_recommended_view` - Natural language to MDX translation
- `execute_mdx_and_get_view` - Execute MDX queries
- `lookup_potential_members` - Find dimension members

**Advanced Analytics:**
- `perform_impact_analysis` - Key driver analysis
- `perform_outlier_detection` - Anomaly detection
- `get_impact_analysis_summary` - AI-generated insights
- `get_outlier_summary` - Outlier explanations

**Reporting:**
- `generate_exploration_analysis_report` - PDF report generation
- `save_mdx_view` - Save views for reuse
- `get_saved_view` - Retrieve saved views

**Metadata:**
- `list_cubes_with_ai_analysis_metadata` - Find pre-analyzed cubes
- `get_cube_dimensions` - Understand cube structure
- `get_cube_sample_members` - Explore dimension members

### Pre-Analyzed Cubes

For semantic queries to work, cubes must be pre-analyzed with AI metadata. Check available cubes:

```
"What cubes are available for analysis?"
"Show me pre-analyzed cubes on 24Retail server"
```

### Output Formats

- **Markdown Tables** - Clean, readable data presentation
- **HTML Tables** - Multi-dimensional data with proper structure
- **Narrative Text** - Business insights and explanations
- **PDF Reports** - Executive-ready analysis documents

## Best Practices

### Writing Effective Queries

✅ **Good Queries:**
- "Show Q1 2025 compensation budget vs actual by department"
- "What's driving revenue variance in the East region?"
- "Find unusual expense patterns in March"
- "Compare this year to last year by product line"

❌ **Avoid:**
- Overly vague: "show me data"
- Too technical: "SELECT FROM [Cube] WHERE..."
- Without context: "variance" (variance of what?)

### Interpreting Results

- Read the **Key Findings** for quick insights
- Check **Data Notes** for quality issues
- Review **Explanations** to understand data selection
- Consider **Recommendations** for next steps

### Working with Missing Data

The skill will note when:
- Data is missing or zero
- Consolidations are used
- Preliminary vs final data
- Potential data quality issues

## Limitations

### What This Skill Can Do
✅ Explore existing cubes with natural language
✅ Perform variance and trend analysis
✅ Generate insights and reports
✅ Provide TM1 guidance and best practices

### What This Skill Cannot Do
❌ Create new cubes or dimensions
❌ Write TurboIntegrator processes
❌ Modify cube data
❌ Perform technical administration

### Workarounds
For tasks this skill cannot do, use **Advanced mode**:
- Cube creation from CSV
- TI process development
- Data loading
- Technical administration

## Integration with Advanced Mode

### Complementary Workflow

1. **Advanced Mode**: Create infrastructure
   - Build cubes from CSV data
   - Create dimensions and hierarchies
   - Develop TI processes
   - Load data

2. **Planning Analytics Skill**: Explore and analyze
   - Query data with natural language
   - Perform variance analysis
   - Generate insights
   - Create reports

3. **Advanced Mode**: Make changes
   - Modify cube structures
   - Update processes
   - Load new data

### Example Combined Workflow

```
Step 1 (Advanced Mode):
"Create a Sales cube from these CSV files"
→ Cube created with dimensions and data loaded

Step 2 (Planning Analytics Skill):
"Show Q1 sales variance by region"
→ Analysis performed, insights generated

Step 3 (Advanced Mode):
"Add a new Product dimension member"
→ Structure updated

Step 4 (Planning Analytics Skill):
"Show updated sales including new product"
→ New analysis with updated data
```

## Examples

### Example 1: Monthly Variance Review

**Query:**
```
"Show me March 2025 compensation variance by department"
```

**Output:**
- Budget vs Actual comparison table
- Variance amounts and percentages
- Department hierarchy with drill-down
- Key findings (e.g., "Marketing 15% over budget")
- Data quality notes
- Recommendations for follow-up

### Example 2: Trend Analysis

**Query:**
```
"What are the revenue trends over the last 12 months?"
```

**Output:**
- Monthly revenue data
- Growth rates by period
- Seasonal patterns identified
- Trend direction and strength
- Year-over-year comparison
- Forecast implications

### Example 3: Outlier Detection

**Query:**
```
"Find unusual sales patterns in Q4 2024"
```

**Output:**
- Detected anomalies with locations
- Statistical significance scores
- Potential causes
- Business impact assessment
- Recommended actions

### Example 4: Key Driver Analysis

**Query:**
```
"What's driving the revenue variance in the East region?"
```

**Output:**
- Key driver identification
- Impact scores by factor
- Sensitivity analysis
- Business interpretation
- Actionable insights

## Requirements

### Prerequisites
- IBM Planning Analytics or TM1 server access
- MCP server configured (ibm-pa-tools-tz-cube, ibm-pa-tools-tz-server)
- Pre-analyzed cubes for semantic queries (optional but recommended)

### Supported Servers
Works with any TM1/Planning Analytics server accessible via MCP tools.

## Troubleshooting

### "No pre-analyzed cubes found"
**Solution:** Use Advanced mode to create cubes, or use explicit MDX queries instead of semantic queries.

### "Cannot find dimension member"
**Solution:** Use `lookup_potential_members` tool or be more specific in your query.

### "Data not available for specified period"
**Solution:** Check available time periods in the cube, adjust query timeframe.

### "Cube not found"
**Solution:** List available cubes first, verify cube name spelling.

## Support

For technical issues with:
- **Cube creation**: Use Advanced mode
- **Process development**: Use Advanced mode
- **Data loading**: Use Advanced mode
- **Query formulation**: This skill provides guidance

## Version

Current version: 1.0.0

---

**Ready to explore your Planning Analytics data?** Activate this skill and start asking business questions in natural language!