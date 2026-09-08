# Planning Analytics Skill - Usage Guide

This guide explains how to use the Planning Analytics skill to explore TM1 data, perform financial analysis, and generate business insights using natural language queries.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Query Patterns](#query-patterns)
3. [Understanding Results](#understanding-results)
4. [Advanced Analytics](#advanced-analytics)
5. [Working with Pre-Analyzed Cubes](#working-with-pre-analyzed-cubes)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Examples](#examples)

---

## Quick Start

### Step 1: Activate the Skill

In Advanced mode, the Planning Analytics skill can be activated automatically when you ask PA-related questions, or you can explicitly activate it.

**Automatic Activation:**
```
"Show me Q1 compensation variance by department"
```

**Explicit Activation:**
```
"Use planning-analytics skill to analyze sales data"
```

### Step 2: Ask Your Question

Use natural, business-friendly language:

```
"Show Q1 2025 compensation budget vs actual by department"
"What's driving revenue variance in the East region?"
"Find unusual expense patterns in March"
"Compare this year to last year by product"
```

### Step 3: Review Results

The skill returns:
- Formatted data tables
- Key findings and insights
- Data quality notes
- Explanations of data selection
- Recommendations

---

## Query Patterns

### Variance Analysis

**Budget vs Actual:**
```
"Show budget vs actual for Q1 by department"
"What's the variance in compensation expenses?"
"Compare budget to actual revenue for March"
```

**Forecast vs Actual:**
```
"Show forecast vs actual sales"
"What's the forecast accuracy for Q4?"
"Compare forecast to actual by region"
```

**Period-over-Period:**
```
"Compare this year to last year"
"Show year-over-year growth by product"
"What's the month-over-month change in expenses?"
```

### Trend Analysis

**Time Series:**
```
"Show sales trends over the last 12 months"
"What are the quarterly revenue patterns?"
"Display monthly expense trends for 2024"
```

**Growth Rates:**
```
"Calculate year-over-year growth rates"
"Show quarterly growth by region"
"What's the compound growth rate?"
```

**Seasonal Patterns:**
```
"Identify seasonal variations in sales"
"Show seasonal expense patterns"
"What are the peak sales months?"
```

### Comparative Analysis

**Regional Comparison:**
```
"Compare Q1 performance across regions"
"Show sales by region for March"
"Which region has the highest revenue?"
```

**Product Comparison:**
```
"Compare product line performance"
"Show top 10 products by revenue"
"Which products are underperforming?"
```

**Department Comparison:**
```
"Compare department expenses"
"Show compensation by department"
"Which departments are over budget?"
```

### Outlier Detection

**Anomaly Identification:**
```
"Find unusual sales patterns in Q4"
"Show outliers in expense data"
"Identify anomalous transactions"
```

**Threshold Violations:**
```
"Show expenses exceeding budget by more than 10%"
"Find sales below target"
"Identify departments with significant variances"
```

### Key Driver Analysis

**Impact Analysis:**
```
"What's driving revenue changes?"
"Show key drivers of expense variance"
"What factors most impact profitability?"
```

**Sensitivity Analysis:**
```
"How sensitive is revenue to price changes?"
"What's the impact of volume on profit?"
"Show sensitivity to cost changes"
```

---

## Understanding Results

### Result Components

#### 1. Data Table
```markdown
| Department | Budget | Actual | Variance ($) | Variance (%) |
|------------|--------|--------|--------------|--------------|
| Total Company | $50,638 | $50,638 | $0 | 0.0% |
| East Region | $50,638 | $50,638 | $0 | 0.0% |
```

**What to look for:**
- Hierarchical structure (indentation shows parent-child)
- Numeric formatting (currency, percentages)
- Missing data indicators (-, No Data)
- Consolidation levels (Total, Region, Department)

#### 2. Key Findings
```markdown
**Key Findings:**
- Total Q1 compensation matched budget exactly ($0 variance)
- All activity concentrated in Massachusetts
- Other regions show no budget or actual data
```

**What to look for:**
- Most important insights highlighted
- Unusual patterns noted
- Significant variances called out
- Business implications stated

#### 3. Data Notes
```markdown
**Data Notes:**
- Only Massachusetts shows active compensation data
- May indicate preliminary data or no employees assigned
- Variance columns empty (may require calculation rules)
```

**What to look for:**
- Data quality issues
- Missing or incomplete data
- Preliminary vs final data
- Calculation limitations

#### 4. Explanations
```markdown
**Explanation:**
Based on your query, the system decided to show "2024" in Year dimension.
For unspecified dimensions, "Total Company" was assigned to context
because it is a top-level consolidation.
```

**What to look for:**
- Why certain data was selected
- What defaults were applied
- Alternative interpretations
- Dimension/member choices

---

## Advanced Analytics

### Outlier Detection

**Query:**
```
"Find unusual sales patterns in Q4 2024"
```

**What You Get:**
- Multiple detection algorithms (Isolation Forest, LOF, etc.)
- Outlier coordinates (row, column, value)
- Statistical significance scores
- Business context and explanations
- Recommended actions

**How to Use:**
1. Review detected outliers
2. Check statistical scores
3. Investigate business causes
4. Take corrective action

### Key Driver Analysis

**Query:**
```
"What's driving revenue variance in the East region?"
```

**What You Get:**
- Key driver identification
- Impact scores (x, y coordinates)
- Feature importance rankings
- Business interpretation
- Actionable insights

**How to Use:**
1. Identify top drivers
2. Understand impact magnitude
3. Focus on high-impact factors
4. Develop action plans

### Impact Analysis

**Query:**
```
"Show impact analysis for Q1 sales"
```

**What You Get:**
- Impact coordinates
- Range information (min, max)
- Visual representation data
- Business insights

**How to Use:**
1. Plot impact points
2. Identify clusters
3. Understand relationships
4. Make data-driven decisions

---

## Working with Pre-Analyzed Cubes

### What Are Pre-Analyzed Cubes?

Pre-analyzed cubes have AI-generated metadata that enables semantic queries. They understand business terminology and can map natural language to TM1 structures.

### Finding Pre-Analyzed Cubes

**Query:**
```
"What cubes are available for analysis?"
"Show me pre-analyzed cubes on 24Retail server"
"List cubes with AI metadata"
```

**Response:**
```
Available pre-analyzed cubes:
- Compensation: Employee compensation and benefits data
- Revenue: Sales and revenue tracking
- Expenses: Operating expense management
```

### Using Pre-Analyzed Cubes

**Semantic Queries (Pre-Analyzed Only):**
```
"Show sales in May 2023"
"What's the compensation for Q1?"
"Display revenue by region"
```

The system automatically:
- Selects the right cube
- Maps business terms to dimensions
- Applies intelligent defaults
- Returns formatted results

**MDX Queries (Any Cube):**
```
"Execute this MDX: SELECT {[Product].[Product].Members} ON 0 FROM [Sales]"
```

Works with any cube, but requires technical knowledge.

---

## Best Practices

### Writing Effective Queries

#### Be Specific
✅ **Good:** "Show Q1 2025 compensation budget vs actual by department"
❌ **Avoid:** "Show me data"

#### Include Context
✅ **Good:** "Compare this year to last year by product line"
❌ **Avoid:** "Compare years"

#### Use Business Terms
✅ **Good:** "What's the variance in compensation expenses?"
❌ **Avoid:** "SELECT FROM [}Cubes] WHERE..."

#### Specify Time Periods
✅ **Good:** "Show March 2025 sales"
❌ **Avoid:** "Show sales" (which period?)

### Interpreting Results

#### Read Key Findings First
Start with the summary to understand main insights quickly.

#### Check Data Notes
Look for data quality issues or limitations before drawing conclusions.

#### Review Explanations
Understand why certain data was selected to validate results.

#### Consider Context
Think about business factors that might explain patterns.

### Following Up

#### Drill Down
```
Initial: "Show Q1 sales by region"
Follow-up: "Show East region sales by state"
Follow-up: "Show Massachusetts sales by product"
```

#### Compare Periods
```
Initial: "Show Q1 2025 sales"
Follow-up: "Compare to Q1 2024"
Follow-up: "Show year-over-year growth"
```

#### Investigate Outliers
```
Initial: "Find unusual sales patterns"
Follow-up: "Show details for the outlier in March"
Follow-up: "What caused the spike in Product A?"
```

---

## Troubleshooting

### Common Issues

#### "No pre-analyzed cubes found"

**Cause:** Server has no cubes with AI metadata

**Solution:**
- Use explicit cube names in queries
- Use MDX queries instead of semantic queries
- Ask to list all available cubes

#### "Cannot find dimension member"

**Cause:** Member name not recognized

**Solution:**
- Use `lookup_potential_members` to search
- Check spelling and capitalization
- Use member aliases if available
- Be more specific in query

#### "Data not available for specified period"

**Cause:** Time period doesn't exist in cube

**Solution:**
- Check available time periods first
- Adjust query to use existing periods
- Verify data has been loaded

#### "Cube not found"

**Cause:** Cube name incorrect or doesn't exist

**Solution:**
- List available cubes first
- Check cube name spelling
- Verify server connection

### Getting Help

**List Available Resources:**
```
"What cubes are available?"
"Show dimensions for Sales cube"
"What members are in the Product dimension?"
```

**Understand Structure:**
```
"Describe the Compensation cube structure"
"Show sample data from Sales cube"
"What dimensions does Revenue cube have?"
```

**Validate Queries:**
```
"Convert my query to MDX"
"Show me the MDX for this view"
"What data will this query return?"
```

---

## Examples

### Example 1: Monthly Variance Review

**Scenario:** CFO wants to review March compensation variance

**Query:**
```
"Show me March 2025 compensation variance by department"
```

**Result:**
```markdown
📊 March 2025 Compensation Variance by Department

| Department | Budget | Actual | Variance ($) | Variance (%) |
|------------|--------|--------|--------------|--------------|
| Total Company | $150,000 | $155,000 | $5,000 | 3.3% |
| Marketing | $50,000 | $57,500 | $7,500 | 15.0% |
| Sales | $60,000 | $58,000 | -$2,000 | -3.3% |
| Operations | $40,000 | $39,500 | -$500 | -1.3% |

**Key Findings:**
- Total company 3.3% over budget ($5,000)
- Marketing significantly over budget (15%)
- Sales and Operations under budget
- Net variance driven by Marketing overspend

**Recommendations:**
- Investigate Marketing overspend causes
- Review Marketing headcount vs budget
- Consider budget reallocation if trend continues
```

### Example 2: Trend Analysis

**Scenario:** VP Sales wants to understand revenue trends

**Query:**
```
"Show revenue trends over the last 12 months"
```

**Result:**
```markdown
📈 12-Month Revenue Trend Analysis

| Month | Revenue | Growth % | 3-Mo Avg |
|-------|---------|----------|----------|
| Jan 2024 | $1.2M | - | - |
| Feb 2024 | $1.3M | 8.3% | - |
| Mar 2024 | $1.4M | 7.7% | $1.3M |
| ... | ... | ... | ... |
| Dec 2024 | $1.8M | 5.9% | $1.7M |

**Key Findings:**
- Consistent upward trend throughout year
- Average monthly growth: 6.5%
- Seasonal peak in Q4 (holiday season)
- Strong momentum entering 2025

**Insights:**
- Growth rate stabilizing around 6%
- Q4 seasonality pattern confirmed
- Forecast suggests continued growth
```

### Example 3: Outlier Detection

**Scenario:** Controller notices unusual expense patterns

**Query:**
```
"Find unusual expense patterns in Q4 2024"
```

**Result:**
```markdown
🔍 Q4 2024 Expense Outlier Analysis

**Detected Outliers:**

1. **Marketing - December**
   - Amount: $125,000
   - Expected: $50,000
   - Deviation: 150% above normal
   - Significance: High

2. **IT - November**
   - Amount: $5,000
   - Expected: $45,000
   - Deviation: 89% below normal
   - Significance: High

**Analysis:**
- Marketing spike likely year-end campaign
- IT drop may indicate delayed projects
- Both require investigation

**Recommendations:**
- Verify Marketing campaign ROI
- Check IT project status
- Review budget allocation for Q1
```

### Example 4: Key Driver Analysis

**Scenario:** CEO wants to understand revenue variance drivers

**Query:**
```
"What's driving the revenue variance in Q1?"
```

**Result:**
```markdown
🎯 Q1 Revenue Variance Key Drivers

**Top Drivers:**

1. **Product Line A** (Impact Score: 0.85)
   - Contribution: $250,000 variance
   - Driver: Volume increase (15%)
   - Action: Increase production capacity

2. **East Region** (Impact Score: 0.72)
   - Contribution: $180,000 variance
   - Driver: New customer acquisition
   - Action: Replicate strategy in other regions

3. **Pricing** (Impact Score: 0.45)
   - Contribution: $90,000 variance
   - Driver: Price optimization
   - Action: Continue pricing strategy

**Summary:**
- Volume and new customers are primary drivers
- Pricing strategy contributing positively
- Focus on scaling successful initiatives
```

---

## Tips for Success

### 1. Start Broad, Then Drill Down
Begin with high-level queries, then progressively drill into details.

### 2. Use Follow-Up Questions
Build on previous results to explore deeper.

### 3. Combine Multiple Analyses
Use variance analysis, then outlier detection, then key drivers for comprehensive insights.

### 4. Save Important Views
Ask to save frequently used views for quick access.

### 5. Generate Reports
Request PDF reports for executive presentations.

### 6. Validate Results
Cross-check important findings with source data.

### 7. Document Insights
Keep track of key findings and recommendations.

---

**Ready to explore your Planning Analytics data?** Start with a simple query and let the skill guide you through the analysis!