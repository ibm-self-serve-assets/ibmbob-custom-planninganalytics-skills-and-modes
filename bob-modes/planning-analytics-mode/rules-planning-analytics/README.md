# Planning Analytics Mode - Quick Reference

## 📋 Overview

This mode provides comprehensive support for IBM Planning Analytics tasks, combining deep TM1 modeling expertise with advanced data analysis capabilities through MCP (Model Context Protocol) integration.

## 🎯 When to Use This Mode

Use Planning Analytics mode for:
- **Data Analysis**: Query cubes, perform variance analysis, identify outliers
- **TM1 Modeling**: Design cubes, dimensions, rules, processes
- **Workspace Guidance**: Navigate and use Planning Analytics Workspace
- **Integration**: TM1 REST API, OData patterns, external system integration
- **Implementation**: Best practices, migration strategies, optimization

## 📁 File Structure

| File | Purpose |
|------|---------|
| `1_overview.xml` | Mode purpose, scope, core principles, MCP integration context |
| `2_mcp_tools_reference.xml` | Complete catalog of MCP tools with parameters and examples |
| `3_workflows.xml` | Comprehensive workflows for all PA tasks |
| `4_best_practices.xml` | Best practices and common pitfalls |
| `5_response_patterns.xml` | Response formatting for different scenarios |
| `6_troubleshooting.xml` | Common issues and recovery strategies |

## 🔧 Available MCP Tools

### Discovery Tools
- `get_available_tm1_servers` - List available servers
- `get_tm1_cubes` - List cubes with metadata
- `list_cubes_with_ai_analysis_metadata` - Check which cubes are pre-analyzed
- `get_cube_dimensions` - Get cube dimensions
- `get_cube_sample_members` - See sample members from dimensions
- `lookup_potential_members` - Search for members by name

### Query Tools
- `get_data_from_data_explorer` - Natural language queries (pre-analyzed cubes only)
- `execute_mdx_and_get_view` - Direct MDX queries (any cube)
- `get_MDX_for_recommended_view` - Generate MDX from natural language

### Analysis Tools
- `perform_impact_analysis` - Identify key drivers
- `perform_outlier_detection` - Find anomalies
- `generate_exploration_analysis_report` - Create PDF reports

### Management Tools
- `create_tm1_cube` / `delete_tm1_cube` - Cube management
- `save_mdx_view` / `get_saved_view` / `list_cube_views` - View management

### Process Management Tools
- `get_tm1_processes` / `get_tm1_process_details` - List and inspect processes
- `create_tm1_process` / `update_tm1_process` / `delete_tm1_process` - Process CRUD operations
- `execute_tm1_processes_asynchronously` - Execute processes
- `get_tm1_server_process_status` / `get_tm1_server_process_threads` - Monitor execution
- `cancel_tm1_process_execution` - Stop running processes
- `get_tm1_server_process_execution_error_logs` - Debug process failures

## 🚀 Quick Start Workflows

### 1. Data Query Workflow
```
1. get_available_tm1_servers → Find server
2. list_cubes_with_ai_analysis_metadata → Check if cube is pre-analyzed
3. If pre-analyzed:
   → get_data_from_data_explorer (natural language)
   If not pre-analyzed:
   → execute_mdx_and_get_view (MDX query)
```

### 2. Variance Analysis Workflow
```
1. Discovery workflow (find server, cube, dimensions)
2. Query data for Budget and Actual versions
3. Calculate variances (Actual - Budget)
4. Identify material variances (>10% or >$100K)
5. Generate insights and recommendations
```

### 3. Advanced Analysis Workflow
```
1. Query data (get state)
2. perform_impact_analysis → get_impact_analysis_summary
   OR
   perform_outlier_detection → get_outlier_summary
   OR
   generate_exploration_analysis_report
```

## ⚠️ Common Issues & Solutions

### Issue: "Cube not pre-analyzed"
**Solution**: Switch to `execute_mdx_and_get_view` with MDX query
```
1. Check status with list_cubes_with_ai_analysis_metadata
2. Use get_cube_sample_members to get member IDs
3. Construct MDX query
4. Execute with execute_mdx_and_get_view
```

### Issue: "Member not found"
**Solution**: Use `lookup_potential_members` to find correct member ID
```
1. Call lookup_potential_members with search term
2. Present matches to user
3. Use correct member ID in query
```

### Issue: "No data returned"
**Solution**: Verify filters and member existence
```
1. Check time period exists (get_cube_sample_members)
2. Verify member combinations are valid
3. Broaden query scope if needed
```

## 📊 Response Format Examples

### Data Analysis Response
```markdown
📊 Q4 2025 Revenue Variance Analysis

**Server:** 24Retail
**Cube:** Revenue
**Period:** Q4 2025
**Organization:** Total Company

**Financial Summary:**
| Product | Budget | Actual | Variance | Variance % |
|---------|--------|--------|----------|------------|
| Phones  | $6.15M | $5.96M | -$199K   | -3.2%      |
| PCs     | $12.79M| $12.15M| -$645K   | -5.0%      |
| Tablets | $3.68M | $4.87M | +$1.19M  | +32.4%     |

**Key Findings:**
- Overall revenue exceeded budget by 1.5%
- Tablets drove positive variance (+$1.19M)
- PCs and Phones underperformed

**Recommended Actions:**
1. Investigate tablet success factors
2. Review phone/PC sales pipeline
3. Update Q1 forecast
```

## 🎓 Core Principles

1. **Adaptive Tool Selection** - Choose right tool based on cube pre-analysis status
2. **Graceful Error Recovery** - Automatically try alternatives when one approach fails
3. **Context-Aware Communication** - Adapt to user's technical level
4. **Source Attribution** - Always cite data sources
5. **Authoritative Guidance** - Prioritize IBM documentation

## 🔗 Key Decision Points

### Should I use get_data_from_data_explorer or execute_mdx_and_get_view?
- **Check first**: `list_cubes_with_ai_analysis_metadata`
- **If is_analyzed: true** → Use `get_data_from_data_explorer`
- **If is_analyzed: false** → Use `execute_mdx_and_get_view`

### When should I use member IDs vs aliases?
- **Always use IDs** in MDX queries and tool parameters
- **Use aliases** only for display to users
- **Get IDs from**: `get_cube_sample_members`

### How do I handle errors?
- **Never leave user stuck** - always provide path forward
- **Fail gracefully** - try alternatives automatically
- **Communicate clearly** - explain in user-friendly terms
- **See**: `6_troubleshooting.xml` for detailed recovery strategies

## 📚 Additional Resources

- **IBM Documentation**: [Planning Analytics Documentation](https://www.ibm.com/docs/en/planning-analytics)
- **MCP Tools Reference**: See `2_mcp_tools_reference.xml`
- **Workflows**: See `3_workflows.xml`
- **Troubleshooting**: See `6_troubleshooting.xml`

## 🆘 Need Help?

1. Check `6_troubleshooting.xml` for common issues
2. Review `2_mcp_tools_reference.xml` for tool details
3. See `3_workflows.xml` for step-by-step workflows
4. Consult `4_best_practices.xml` for guidance

---

**Made with Bob** - IBM Planning Analytics Mode