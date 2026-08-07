# Repository Audit Checklist

Use this checklist for repo hygiene, branch alignment, release-readiness reviews, and repository integrity audits.

## 1. Repository identity and state
- Confirm repository name, owner, default branch, and current checkout branch.
- Confirm the working tree is clean or that any remaining changes are intentional.
- Record local modifications and untracked files before any sync or commit action.
- Call out local-only files that must remain excluded from sync or commit.

## 2. Git topology and refs
- Confirm remotes and upstream tracking.
- Verify the current branch points to the expected commit.
- Check for local branches that are stale, duplicate, or no longer needed.
- Check for ghost, unreachable, orphaned, or special refs and document any findings.
- Inspect `refs/original`, `refs/replace`, `refs/stash`, `refs/bisect`, packed refs, reflog residue, worktrees, sparse checkout, submodules, and LFS state.
- Ensure no unexpected tags or packed refs are being relied on without review.

## 3. Sync and drift audit
- Fetch remote updates.
- Report ahead/behind counts against upstream.
- If behind, rebase safely and preserve unrelated changes.
- If a rebase or sync is blocked by divergence, stop and request direction.
- Confirm the push completed successfully and re-check divergence after push.

## 4. Tree and content integrity
- Verify required repository paths exist.
- Check for duplicate filenames, duplicate content, and unexpected shadowed paths.
- Verify that docs, tests, automation, config, and source folders remain aligned with the documented architecture.
- Review for transient runtime artifacts that should not be committed.
- Treat small tree mismatches, stale path references, and normalization drift as audit findings, not as harmless noise.
- Compare the documented tree to the actual filesystem and flag any omissions, renamed folders, or misplaced files.
- Confirm that the repo narrative, folder structure, and actual contents remain consistent after any refactor or reorganization.
- Report duplicate evidence with full paths, not only hashes or basenames.

## 5. Validation and quality gates
- Run the required validation steps for the current change scope.
- Prefer objective gates in this order when available:
	1. targeted failing check or behavior-scoped regression test
	2. narrow test for the touched slice
	3. full relevant test suite
	4. syntax or dependency validation
	5. structural scans for docs/config/workflows
- If hooks or tests fail, do not push until the failure is understood and addressed.
- Record the exact validation command and outcome.
- If validation is blocked, say so explicitly and identify what additional access or context is required.

## 6. Commit and push hygiene
- Stage only intended files.
- Use a scoped commit message that reflects the actual change.
- Record the commit hash, files included, and files intentionally excluded.
- Push only after validation passes.
- If the push is blocked by authentication or network constraints, record that as a blocker rather than treating it as a pass.

## 7. GitHub and governance audit
- Inspect open pull requests, draft pull requests, stale pull requests, and mergeability when authenticated access is available.
- Validate branch protection, rulesets, required checks, reviewers, environments, variables, secrets, and security-alert surfaces when authenticated access is available.
- Distinguish verified, blocked, unavailable, and not-applicable surfaces.
- Do not imply governance validation if the API response was 401, 403, 404, 410, or otherwise incomplete.

## 8. Configuration and dependency audit
- Compare environment templates and active configs for schema drift, required-key drift, and secret placeholder drift.
- Compare requirement files for conflicting version constraints and drift in pinned packages.
- Treat secret value differences separately from structural configuration differences.
- Note that `pip check` validates installed package compatibility, not dependency freshness or vulnerability state.

## 9. Semantic consistency audit
- Check for duplicate or conflicting prompts, instructions, workflows, and automation responsibilities.
- Check for stale or contradictory documentation.
- Check for repeated policy logic that should have a single source of truth.
- Use similarity checks and reference scans, but do not claim semantic equivalence without inspecting the actual content.

## 10. Reporting format
- Report findings in a control matrix with each domain labeled as one of: Pass, Fail, Blocked, Unavailable, or Not Applicable.
- Avoid unsupported percentages, health scores, or confidence scores unless they are derived from explicit, documented criteria.
- Separate verified findings from blocked checks.
- Include full repository paths for duplicate files, drifted files, and failing artifacts.

## 11. Final audit summary
- Branch name
- Ahead/behind state before sync
- Commit hash pushed
- Files included in commit
- Files intentionally excluded
- Validation outcomes
- Control matrix by domain
- Blocked surfaces and why they were blocked
- High-confidence cleanup candidates
