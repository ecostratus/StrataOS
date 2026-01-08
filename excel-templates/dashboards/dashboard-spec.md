# Dashboard Specification

## Overview

This document defines the specification for the 60-Day Operating Dashboard that provides visual insights and metrics for the personal operating system.

This dashboard integrates with the **Canonical 10-Sheet System of Record (SoR)** schema.

## Dashboard Purpose

Provide at-a-glance visibility into:
- Current progress toward 60-day goals
- Key performance indicators (KPIs)
- Activity trends and patterns
- Funnel metrics
- Goal achievement tracking
- System health indicators

## Dashboard File

**File**: `60d_operating_dashboard.xlsx`

## Dashboard Layout

### Section 1: Executive Summary (Top)

**60-Day Timeline Progress**
- Visual timeline showing current day within 60-day window
- Start date, current date, end date
- Days elapsed / Days remaining
- Progress bar (% complete)

**Key Metrics Summary**
| Metric | This Week | Last Week | Total | Target | On Track? |
|--------|-----------|-----------|-------|--------|-----------|
| Applications | X | Y | Total | Goal | ✓/✗ |
| Interviews | X | Y | Total | Goal | ✓/✗ |
| Outreach | X | Y | Total | Goal | ✓/✗ |
| Offers | X | Y | Total | Goal | ✓/✗ |

### Section 2: Activity Funnel

**Role Search Funnel**
```
Roles Identified (500) ───→ High FitScore (50) ───→ Applied (25) ───→ 
Response (10) ───→ Interview (5) ───→ Offer (1)
```

With conversion rates at each stage:
- Identification to High FitScore: X%
- High FitScore to Applied: Y%
- Applied to Response: Z%
- Response to Interview: A%
- Interview to Offer: B%

**Visual**: Funnel chart showing drop-off at each stage

**Data Source**: Roles sheet (Status field), StatusHistory sheet (status transitions)

### Section 3: Activity Trends

**Weekly Activity Chart**
- Line chart showing weekly trends for:
  - Roles identified (Roles sheet, Status = "Identified")
  - Applications submitted (Roles sheet, Status = "Applied")
  - Outreach sent (Outreach sheet, SentDate)
  - Interviews conducted (Interviews sheet, CompletedDate)

**Time Period**: Last 8 weeks

**Data Sources**: Roles sheet, Outreach sheet, Interviews sheet, StatusHistory sheet

### Section 4: Response Metrics

**Response Rates Dashboard**
- Application response rate: X% (Target: 20-30%)
- Outreach response rate: Y% (Target: 20-30%)
- Interview conversion rate: Z% (Target: 30-40%)
- Overall effectiveness score: A/10

**Visual**: Gauge charts for each metric showing actual vs target

### Section 5: Quality Metrics

**Role FitScore Distribution**
- Histogram showing distribution of role fit scores
- Average FitScore: X.X
- Median FitScore: X.X
- Number of exceptional matches (90-100)
- Number of strong matches (70-89)

**Data Source**: Roles sheet (FitScore field)

**Application Quality**
- Average days to apply (from identification to Applied status)
- Status transition time analysis

**Data Sources**: Roles sheet, StatusHistory sheet

### Section 6: Consulting Pipeline

**Opportunity Stages**
| Stage | Count | Value | Status |
|-------|-------|-------|--------|
| Discovery | X | $XX,XXX | Open |
| Proposal | X | $XX,XXX | Open/In Progress |
| Implementation | X | $XX,XXX | In Progress |
| Retainer | X | $XX,XXX | In Progress |
| Training | X | $XX,XXX | Open/In Progress |
| Closed Won | X | $XX,XXX | 100% |
| Closed Lost | X | $XX,XXX | 0% |

**Visual**: Pipeline chart with stages and values

**Data Source**: Consulting sheet (Type, Status, ValueEstimate fields)

### Section 7: Time Investment

**Time Allocation**
- Pie chart showing time spent:
  - Job search: XX hours (XX%)
  - Consulting: XX hours (XX%)
  - Networking: XX hours (XX%)
  - Interview prep: XX hours (XX%)
  - Administration: XX hours (XX%)

**Efficiency Metrics**
- Time per application: X hours
- Time per outreach: X minutes
- ROI of automation: X hours saved/week

### Section 8: Goal Achievement

**Weekly KPI Tracker**

Metrics are calculated from the Metrics sheet, which stores computed KPIs:
- Applications submitted (from Roles sheet status transitions)
- Outreach messages sent (from Outreach sheet)
- Interviews scheduled (from Interviews sheet)
- Offers received (from Roles sheet, Status = "Closed" with positive outcome)

**Metrics Display**
| Week Of | Metric Name | Target | Actual | Achievement % |
|---------|-------------|--------|--------|---------------|
| Week 1 | Applications | X | Y | XX% |
| Week 1 | Outreach | A | B | XX% |
| Week 2 | Applications | X | Y | XX% |
| Week 2 | Outreach | A | B | XX% |

**Overall Achievement Rate**: XX%

**Visual**: Line chart showing weekly achievement percentage

**Data Source**: Metrics sheet (computed KPIs populated by automation)

### Section 9: System Health

**Automation Status**
- Role discovery flow: ✓ Working / ⚠ Issues / ✗ Down
- Resume tailoring flow: ✓ Working / ⚠ Issues / ✗ Down
- Outreach generation flow: ✓ Working / ⚠ Issues / ✗ Down
- FitScore calculation: ✓ Working / ⚠ Issues / ✗ Down

**Data Source**: FlowErrors sheet (check for unresolved errors)

**Data Quality**
- Missing data rate: X%
- StatusHistory completeness: XX%
- ChangeLog entries: X changes this week
- Data freshness: Updated X hours ago

**Data Sources**: StatusHistory sheet, ChangeLog sheet, FlowErrors sheet

**Active Flow Errors**
Count of unresolved errors from FlowErrors sheet where Resolved = "No"

**Alerts**
- [Active alert 1 if any - from FlowErrors]
- [Active alert 2 if any - from FlowErrors]

### Section 10: Next Actions

**Top Priorities**
1. [Priority action 1]
2. [Priority action 2]
3. [Priority action 3]

**Upcoming This Week**
- Interviews scheduled: X
- Applications due: X
- Proposals due: X
- Follow-ups needed: X

**Overdue Items**
- Overdue follow-ups: X
- Overdue applications: X
- Overdue prep: X

## Data Sources

All dashboard metrics pull from the **Canonical 10-Sheet System of Record** workbook:

### Core Entity Sheets
- **Roles sheet**: Target roles, applications status (FitScore, Status, CompanyID, LastUpdated)
- **Companies sheet**: Company information for roles and consulting
- **Contacts sheet**: Professional network contacts
- **Outreach sheet**: Outreach tracking (Channel, MessageType, ResponseType)
- **Interviews sheet**: Interview stages and outcomes
- **Consulting sheet**: Consulting pipeline (Type, Status, ValueEstimate)

### Computed and Audit Sheets
- **Metrics sheet**: Computed KPIs and summary metrics (populated by automation)
- **StatusHistory sheet**: Status change audit trail for all entities
- **FlowErrors sheet**: Automation and Copilot flow error tracking
- **ChangeLog sheet**: Structural changes to the SoR schema

## Refresh Frequency

**Automatic Refresh**: 
- On workbook open
- Every 15 minutes if workbook is open

**Manual Refresh**:
- Button to refresh all data connections
- Button to recalculate all formulas

## Dashboard Features

### Interactive Elements
- **Date range selector**: Filter charts by date range
- **Metric selector**: Choose which metrics to display
- **Drill-down**: Click chart elements to see details
- **Filters**: Company, status, priority filters

### Conditional Formatting
- Red/Yellow/Green for on-track indicators
- Heat maps for score distributions
- Progress bars for goal achievement
- Alert icons for issues

### Formulas
- All metrics calculated from source data
- Dynamic calculations based on selected date range
- Aggregations for weekly, monthly views
- Trend calculations (moving averages, growth rates)

### Charts
- **Line charts**: Trends over time
- **Bar charts**: Comparisons across categories
- **Pie charts**: Proportional distributions
- **Funnel charts**: Conversion funnels
- **Gauge charts**: Performance vs targets
- **Heat maps**: Score distributions

## Dashboard Setup

### Initial Setup
1. Link to System of Record workbook
2. Configure data connections
3. Set up named ranges
4. Create pivot tables
5. Build charts
6. Format layout and styling
7. Add interactive controls
8. Test refresh and updates

### Customization Options
- Adjust date ranges
- Modify target metrics
- Add/remove charts
- Change color schemes
- Customize KPIs
- Add annotations

## Usage Guidelines

### Daily Review (5 minutes)
- Check key metrics summary
- Review next actions
- Check for alerts

### Weekly Review (30 minutes)
- Analyze all dashboard sections
- Export screenshots for documentation
- Update targets if needed
- Review trends and patterns

### Monthly Review (60 minutes)
- Comprehensive dashboard analysis
- Compare against 60-day goals
- Adjust dashboard as needed
- Archive dashboard snapshot

## Dashboard Maintenance

### Weekly
- Verify data accuracy
- Check broken links
- Update calculated fields
- Refresh formatting

### Monthly
- Review dashboard effectiveness
- Add/remove metrics based on usefulness
- Update targets and goals
- Optimize performance

## Export and Sharing

**Export Options**:
- PDF for weekly reviews
- PNG for presentations
- CSV for data analysis
- Print-friendly layout

**Sharing**:
- Dashboard is personal (not shared)
- Screenshots can be shared
- Aggregate metrics can be shared
- No PII in shared versions

## Technical Requirements

- Excel 2016 or later (or Excel Online)
- Data connections enabled
- Macro-free (VBA not required)
- Works on Windows and Mac
- Mobile-friendly (Excel mobile app)

## Performance Optimization

- Use Excel tables for auto-expansion
- Minimize volatile formulas (NOW, TODAY)
- Use named ranges for readability
- Optimize pivot table refresh
- Limit data to last 90 days
- Archive old data monthly
