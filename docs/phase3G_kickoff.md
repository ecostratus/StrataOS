# Phase 3G — Interview Prep Hardening Kickoff

Date: January 11, 2026

## Scope
Harden interview-prep modules for import robustness, deterministic behavior, and dynamic loading:
- Modules: automation/interview-prep/scripts/*, templates, context builders, shared utilities.
- Goals: two-stage imports, function-scoped loaders, deterministic context/template selection, logging + metrics events, snapshot tests, dynamic import tests.

## Targets
- Identify module-level risky imports, hyphenated/invalid dotted imports, importlib usage, and any non-deterministic behavior in prompt assembly.
- Apply two-stage import hardening with repo-root-relative paths; preserve schema, flags, and public APIs.

## Validation
- Tests: pytest suite, snapshot tests, dynamic import tests for interview-prep.
- Docs CI: scripts/ci/check_docs.py.
- Runner: smoke test via interview-prep entry script.

## Artifacts
- PR Title, Commit Message, Release Notes, Audit Entry, Diff Summary, Verification Checklist.

## Next Steps
- Execute Phase 3G hardening per the super‑prompt.
