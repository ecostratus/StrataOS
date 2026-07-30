# Source Priority Matrix

This matrix summarizes initial source prioritization from profile scorecards.

## Method

Priority rank is based on weighted score, compliance confidence, and strategic fit.

## Current Ranking

| Rank | Source | Weighted Score | Recommendation | Notes |
| --- | --- | --- | --- | --- |
| 1 | Greenhouse | 3.85 | Integrate | Existing adapter baseline and high fit |
| 2 | Lever | 3.85 | Integrate | Existing adapter baseline and high fit |
| 3 | LinkedIn | 3.85 | Pilot | High value with stricter access controls |
| 4 | Workday career sites | 3.45 | Pilot | Strong direct-employer value, parser complexity |
| 5 | ZipRecruiter | 3.35 | Pilot | Broad coverage pending access validation |
| 6 | Dice | 3.30 | Pilot | Strong tech-role signal potential |
| 7 | Indeed | 3.25 | Pilot | High volume with quality and policy controls |
| 8 | Wellfound | 3.25 | Pilot | Startup-focused value lane |
| 9 | Monster | 3.00 | Defer | Lower near-term priority |
| 10 | CareerBuilder | 2.90 | Defer | Lower near-term priority |

## Gating Rules Before Build

- Compliance review must be approved for each P1 source.
- Source must have at least one stable payload sample set.
- Adapter test scaffold must be in place before integration.

## Update Cadence

- Refresh after each major source validation cycle.
