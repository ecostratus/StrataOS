# Phase 3G — Interview Prep Hardening Execution Checklist

## 1. Scan & Identify
- [ ] List interview-prep modules and templates
- [ ] Flag module-level risky imports
- [ ] Flag hyphenated/invalid dotted imports
- [ ] Flag importlib usage
- [ ] Flag non-deterministic context/template selection

## 2. Two-Stage Import Hardening
- [ ] Try dotted imports first
- [ ] Add dynamic fallback via `load_module_from_path`
- [ ] Move risky imports inside functions
- [ ] Use repo-root-relative paths only
- [ ] Preserve schema/flags/public APIs

## 3. Determinism & Instrumentation
- [ ] Deterministic context assembly
- [ ] Deterministic template selection
- [ ] Add logging + metrics: start, context_loaded, variant_selected, rendered, saved

## 4. Tests
- [ ] Dynamic import tests for interview-prep modules
- [ ] Snapshot tests for prompt outputs
- [ ] Runner smoke test (no PYTHONPATH)

## 5. Validation Commands
- [ ] `./.venv/bin/python -m pytest -q --tb=short`
- [ ] `python3 scripts/ci/check_docs.py`
- [ ] `./.venv/bin/python automation/common/run_prompts.py --interview-context config/interview_context.sample.json --interview-output-dir output/interview`

## 6. PR Artifacts
- [ ] PR Title, Commit Message
- [ ] Release Notes Block
- [ ] Audit Trail Entry
- [ ] Diff Summary
- [ ] Verification Checklist

## 7. Governance
- [ ] Ask before execution (Phase 3G hardening patch)
- [ ] Tag release and publish notes
