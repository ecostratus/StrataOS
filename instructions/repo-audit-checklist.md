# Repository Audit Checklist

Use this checklist for repo hygiene, branch alignment, and release-readiness reviews.

## 1. Repository identity and state
- Confirm repository name, owner, default branch, and current checkout branch.
- Confirm the working tree is clean or that any remaining changes are intentional.
- Record local modifications and untracked files before any sync or commit action.

## 2. Git topology and refs
- Confirm remotes and upstream tracking.
- Verify the current branch points to the expected commit.
- Check for local branches that are stale, duplicate, or no longer needed.
- Check for ghost, unreachable, or orphaned refs and document any findings.
- Ensure no unexpected tags or packed refs are being relied on without review.

## 3. Sync and drift audit
- Fetch remote updates.
- Report ahead/behind counts against upstream.
- If behind, rebase safely and preserve unrelated changes.
- If a rebase or sync is blocked by divergence, stop and request direction.

## 4. Tree and content integrity
- Verify required repository paths exist.
- Check for duplicate filenames or unexpected shadowed paths.
- Verify that docs, tests, automation, config, and source folders remain aligned with the documented architecture.
- Review for transient runtime artifacts that should not be committed.
- Treat small tree mismatches, stale path references, and normalization drift as audit findings, not as harmless noise.
- Compare the documented tree to the actual filesystem and flag any omissions, renamed folders, or misplaced files.
- Confirm that the repo narrative, folder structure, and actual contents remain consistent after any refactor or reorganization.

## 5. Validation and quality gates
- Run the required validation steps for the current change scope.
- If hooks or tests fail, do not push until the failure is understood and addressed.
- Record the exact validation command and outcome.

## 6. Commit and push hygiene
- Stage only intended files.
- Use a scoped commit message that reflects the actual change.
- Record the commit hash, files included, and files intentionally excluded.
- Push only after validation passes.

## 7. Final audit summary
- Branch name
- Ahead/behind state before sync
- Commit hash pushed
- Files included in commit
- Files intentionally excluded
- Validation outcomes
- Confidence rating for repo integrity
