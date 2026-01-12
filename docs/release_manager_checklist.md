# Release Manager Checklist

## 1. Pre‑Release Validation
- [ ] All tests pass (`pytest -q --tb=short`)
- [ ] Docs CI passes (`scripts/ci/check_docs.py`)
- [ ] Combined runner works (full-sources mode)
- [ ] No PYTHONPATH required
- [ ] Snapshot tests stable
- [ ] No schema/flag/public API changes unless explicitly scoped

## 2. Code Review
- [ ] Two-stage imports applied
- [ ] Dynamic loaders use repo-root-relative paths
- [ ] No module-level risky imports
- [ ] No hyphenated importlib calls
- [ ] No dead code or unused imports

## 3. Documentation
- [ ] Release notes updated
- [ ] Audit trail updated
- [ ] Roadmap updated
- [ ] Progress checklist updated

## 4. PR Preparation
- [ ] PR title follows pattern:
      Phase X: vY.Z Import Hardening — <Component>
- [ ] Commit message follows release discipline
- [ ] Diff summary included
- [ ] Verification checklist included

## 5. Tagging & Publishing
- [ ] Tag created:
      git tag vY.Z -m "<release title>"
- [ ] Tag pushed:
      git push origin vY.Z
- [ ] Release published on GitHub

## 6. Post‑Release
- [ ] Validate release artifacts
- [ ] Update master roadmap
- [ ] Create next milestone issue
