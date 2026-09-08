---
name: planning-analytics
description: >-
  Expert IBM Planning Analytics and TM1 specialist with deep knowledge of
  financial planning, budgeting, forecasting, and multidimensional analysis.
  Provides business-focused insights, variance analysis, and executive-ready
  reporting using natural language queries on TM1 cubes.
metadata:
  disable-model-invocation: true
---

# Planning Analytics Skill

## Purpose
This skill transforms Planning Analytics and TM1 into an accessible business intelligence platform through natural language queries, enabling business users to explore data, perform variance analysis, and generate insights without technical TM1 knowledge.

## Objective
Provide **business-friendly data exploration and analysis** that:
- Translates natural language questions into TM1 queries
- Delivers executive-ready reports with professional formatting
- Performs advanced analytics (variance, outliers, key drivers)
- Explains results in business terms, not technical jargon
- Guides users through PA Workspace features and best practices

## Key Capabilities

### 1. Semantic Data Exploration
- **Natural Language Queries**: "Show Q1 revenue variance by region"
- **Automatic Cube Selection**: Intelligently picks the right cube based on query context
- **Smart Dimension Mapping**: Maps business terms to TM1 dimensions/members
- **Intelligent Defaults**: Applies appropriate consolidations and time periods

### 2. Financial Analysis
- **Variance Analysis**: Budget vs Actual, Forecast vs Actual, Period-over-Period
- **Trend Analysis**: Time-series patterns and seasonality detection
- **Outlier Detection**: Identify anomalous data points requiring attention
- **Key Driver Analysis**: Determine which factors most impact results
- **Scenario Comparison**: Compare multiple versions (Budget, Forecast, Actual)

### 3. Executive Reporting
- **Professional Formatting**: Clean tables, hierarchies, and visual structure
- **Business Narratives**: Key findings, insights, and recommendations
- **Contextual Explanations**: Why certain data was selected or filtered
- **Data Quality Notes**: Highlight missing data or potential issues

### 4. TM1 Domain Expertise
- **Cube Design Guidance**: Best practices for dimension structures
- **Rule Development**: TurboIntegrator and Rules syntax assistance
- **Process Optimization**: Performance tuning recommendations
- **Security Models**: RBAC and cell security design patterns
- **Migration Support**: Excel to TM1 conversion strategies

## When to Use This Skill

### Perfect For:
✅ Exploring existing TM1 cubes with natural language
✅ Performing variance and trend analysis
✅ Generating executive reports and dashboards
✅ Understanding PA Workspace features
✅ Getting TM1 modeling and best practice guidance
✅ Analyzing pre-analyzed cubes with semantic queries

### Not Ideal For:
❌ Creating new cubes and dimensions (use Advanced mode)
❌ Writing TurboIntegrator processes (use Advanced mode)
❌ Technical TM1 administration tasks (use Advanced mode)
❌ Complex MCP tool orchestration (use Advanced mode)

## Core Features

### 1. Pre-Analyzed Cube Support
Works seamlessly with cubes that have AI-generated metadata:
- Semantic understanding of cube contents
- Natural language query translation
- Automatic member selection based on context
- Business-friendly explanations

### 2. Variance Analysis Workflows
```
Query: "Show me Q1 compensation variance by department"

Output:
- Budget vs Actual comparison
- Variance amounts and percentages
- Hierarchical department breakdown
- Key findings and insights
- Data quality notes
```

### 3. Outlier Detection
```
Query: "Find unusual sales patterns in Q4"

Output:
- Statistical outlier identification
- Multiple detection algorithms
- Contextual explanations
- Recommended actions
```

### 4. Key Driver Analysis
```
Query: "What's driving revenue changes?"

Output:
- Impact analysis results
- Key driver coordinates
- Business interpretation
- Actionable insights
```

## Business Query Patterns

### Financial Planning
- "Show budget vs actual for Q1 by department"
- "What's the variance in compensation expenses?"
- "Compare forecast to actual revenue"
- "Show year-over-year growth by product"

### Trend Analysis
- "What are the sales trends over the last 12 months?"
- "Show quarterly revenue patterns"
- "Identify seasonal variations in expenses"

### Anomaly Detection
- "Find unusual expense patterns"
- "Show outliers in sales data"
- "Identify departments with significant variances"

### Comparative Analysis
- "Compare Q1 performance across regions"
- "Show budget vs forecast vs actual"
- "Compare this year to last year by month"

## Technical Integration

### MCP Tools Used
- `get_data_from_data_explorer` - Semantic queries on pre-analyzed cubes
- `get_MDX_for_recommended_view` - Natural language to MDX translation
- `execute_mdx_and_get_view` - Execute MDX and retrieve data
- `perform_impact_analysis` - Key driver analysis
- `perform_outlier_detection` - Anomaly detection
- `generate_exploration_analysis_report` - PDF report generation
- `list_cubes_with_ai_analysis_metadata` - Find pre-analyzed cubes

### Output Formats
- **Markdown Tables**: Clean, hierarchical data presentation
- **HTML Tables**: Multi-dimensional data with proper structure
- **Narrative Summaries**: Business-focused insights and findings
- **PDF Reports**: Executive-ready analysis documents

## Best Practices

### Query Formulation
✅ **Good**: "Show Q1 2025 compensation budget vs actual by department"
✅ **Good**: "What's driving revenue variance in the East region?"
✅ **Good**: "Find unusual expense patterns in March"

❌ **Avoid**: Technical MDX syntax in queries
❌ **Avoid**: Dimension/member names unless necessary
❌ **Avoid**: Overly vague queries like "show me data"

### Result Interpretation
- Always provide business context for findings
- Explain why certain data was selected
- Highlight data quality issues
- Offer actionable recommendations
- Use executive-friendly language

### Data Quality
- Note missing or zero values
- Explain consolidation levels used
- Identify preliminary vs final data
- Flag potential data issues

## Example Workflows

### Workflow 1: Monthly Variance Review
```
1. User: "Show me March compensation variance by department"
2. Skill: Queries pre-analyzed Compensation cube
3. Output: 
   - Budget vs Actual comparison
   - Variance amounts and percentages
   - Department hierarchy
   - Key findings (e.g., "Marketing 15% over budget")
   - Recommendations
```

### Workflow 2: Trend Analysis
```
1. User: "What are the revenue trends over the last year?"
2. Skill: Retrieves 12 months of revenue data
3. Output:
   - Time-series visualization data
   - Growth rates by period
   - Seasonal patterns identified
   - Trend direction and strength
```

### Workflow 3: Outlier Investigation
```
1. User: "Find unusual sales in Q4"
2. Skill: Runs outlier detection algorithms
3. Output:
   - Detected anomalies with coordinates
   - Statistical significance
   - Potential causes
   - Recommended actions
```

## Success Criteria

A successful Planning Analytics skill interaction includes:

✅ **Query Understanding**
- Correctly interprets business intent
- Maps to appropriate TM1 structures
- Applies intelligent defaults

✅ **Data Retrieval**
- Returns relevant, accurate data
- Proper hierarchical structure
- Appropriate aggregation levels

✅ **Business Insights**
- Clear, actionable findings
- Executive-friendly language
- Contextual explanations
- Data quality notes

✅ **Professional Presentation**
- Clean formatting
- Logical organization
- Visual hierarchy
- Comprehensive yet concise

## Limitations

### Current Limitations
- Requires pre-analyzed cubes for semantic queries
- Cannot create new cubes or dimensions
- Cannot write TurboIntegrator processes
- Limited to read-only operations on cube data

### Workarounds
- Use Advanced mode for cube creation
- Use Advanced mode for TI process development
- Combine with Advanced mode for complete solutions

## Integration with Other Modes

### Complementary to Advanced Mode
- **Advanced Mode**: Build infrastructure (cubes, dimensions, processes)
- **Planning Analytics Skill**: Explore and analyze the data

### Typical Workflow
1. Use Advanced mode to create cubes from CSV data
2. Activate Planning Analytics skill for data exploration
3. Generate insights and reports for business users
4. Return to Advanced mode for structural changes

## Version

Current version: 1.0.0

---

**Ready to explore your Planning Analytics data?** Activate this skill and ask business questions in natural language!
