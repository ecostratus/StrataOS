# Phase 3G — Hardening Super‑Prompt (Reusable)

Use this prompt to execute or regenerate the next hardening phase end-to-end.

```
You are assisting with the personal-operating-system-60d repository.
Your task is to execute or regenerate a full hardening phase (e.g., v0.3.7), including code patches, dynamic import fixes, tests, docs, audit updates, and PR artifacts.

Follow these instructions exactly:

============================================================
PHASE 1 — SCAN & IDENTIFY BROKEN IMPORTS
============================================================
1. Scan the target modules (sources, utils, filters, adapters, runner, and any new modules).
2. Identify:
   - Module-level risky imports
   - Hyphenated dotted imports
   - importlib.import_module("automation.job-discovery...") calls
   - Any import that breaks when run without PYTHONPATH
3. Produce a list of imports requiring hardening.

============================================================
PHASE 2 — APPLY TWO-STAGE IMPORT HARDENING
============================================================
For each failing import:
A. Try dotted import.
B. On failure, dynamically load via load_module_from_path() using repo-root-relative paths.
C. Move all risky imports inside functions.
D. Replace importlib.import_module() with dynamic loaders.
E. Do NOT rename directories or change schema/flags.

============================================================
PHASE 3 — PATCH MODULES
============================================================
Patch:
- Orchestrator modules (function-scoped imports, dynamic adapter loading)
- Utilities (logging utils fallback, normalization fallback)
- Adapters (ensure dynamic loading compatibility)
- Runner (repo-root sys.path injection + two-stage imports)

============================================================
PHASE 4 — ADD/UPDATE TESTS
============================================================
Add or update:
- Dynamic import tests for orchestrator, utils, filters, adapters
- Full-sources smoke test for combined runner
- Ensure tests pass without PYTHONPATH

============================================================
PHASE 5 — VALIDATION COMMANDS
============================================================
Run:
./.venv/bin/python -m pytest -q --tb=short
python3 scripts/ci/check_docs.py
./.venv/bin/python automation/common/run_prompts.py \
  --outreach-context config/outreach_context.sample.json \
  --outreach-output-dir output/outreach \
  --resume-context config/resume_context.sample.json \
  --resume-output-dir output/resume

Expected:
- No ModuleNotFoundError
- No SyntaxError
- Prompts generated in full-sources mode

============================================================
PHASE 6 — GENERATE PR ARTIFACTS
============================================================
Produce:
- PR Title
- Commit Message
- Release Notes Block
- Audit Trail Entry
- Diff Summary
- Verification Checklist

============================================================
PHASE 7 — ASK BEFORE EXECUTION
============================================================
Before modifying any files, ask:

“Do you want me to execute the hardening patch now?”

============================================================
PHASE 8 — OUTPUT FORMAT
============================================================
Output must include:
- PR Title
- Commit Message
- Release Notes Block
- Audit Trail Entry
- Diff Summary
- Verification Checklist
```
