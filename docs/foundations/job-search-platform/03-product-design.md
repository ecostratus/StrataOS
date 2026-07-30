# Product Design: Job Search Experience

## User Goals

- Find relevant jobs quickly with precise criteria.
- Tune search criteria without editing config files.
- Understand why results are ranked the way they are.
- Move seamlessly from search to resume and outreach actions.

## Core UX Flows

1. Build Search
- Enter title or keyword query.
- Add company include or exclude criteria.
- Set location: country, state, city.
- Choose job type and work type.
- Set salary min and max.

2. Refine Results
- Use chips and facets to narrow quickly.
- Sort by relevance, date, salary, and company.
- Save a search for re-use.

3. Act on Opportunities
- Select jobs and generate resume/outreach.
- Track source, freshness, and ranking context.

## Required Search Fields

- Title and keyword include
- Keyword exclude
- Company include
- Company exclude
- Country
- State or region
- City
- Salary minimum
- Salary maximum
- Currency
- Job type: full-time, part-time, contract, internship
- Work type: remote, hybrid, onsite
- Posted window: 24h, 3d, 7d, 14d, 30d

## UX Requirements

- Filter state is visible and reversible.
- Immediate feedback for zero-result conditions.
- Saved searches are one click away.
- Advanced controls are collapsible.
- Keyboard-accessible navigation and controls.

## Relevance Transparency

Each result should show:

- Matched title or keyword signals
- Matched location signals
- Freshness signal
- Score bucket and short explanation

## Success Criteria

- Users can define full search criteria in one screen.
- Search to shortlist time decreases over baseline.
- Saved searches are reused week over week.
