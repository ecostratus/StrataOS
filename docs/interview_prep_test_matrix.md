# Interview Prep Test Matrix

## Dynamic Import Tests
- Load interview_prep_v1 via path-based import; assert `main` exists.
- Load any shared utilities used by interview-prep.

## Snapshot Tests
- Render interview prompt templates with deterministic context; compare snapshots.

## Behavior Tests
- Deterministic template selection given same inputs.
- Logging + metrics events emitted at key stages.

## Runner Smoke Test
- Invoke interview-prep script in a controlled environment; assert output created.
