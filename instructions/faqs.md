# FAQs

## Why are some jobs not shown by default?
Default API and UI behavior hides low-relevance jobs to reduce noise.

## How do I see all jobs, including weak matches?
Turn on **Show low relevance jobs** in the UI, or set `include_low_relevance: true` in API requests.

## Why is a job excluded even if title looks relevant?
It may have empty `role_tags`, fall below the minimum bucket, or be filtered by configured keyword/location/tag rules.

## Can I lower the threshold without code changes?
Yes. Use `min_bucket` in API calls (`Weak`, `Moderate`, `Strong`, `Exceptional`).

## Does this replace scoring?
No. This is query-layer filtering. Scoring still computes relevance independently.
