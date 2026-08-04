# Local and Remote Sync Prompt

Use this prompt for all branch sync and repository hygiene runs.

## Prompt

You are performing local and remote repository sync alignment and hygiene.

Repository rules:
- Never use destructive commands such as git reset --hard or git checkout -- unless explicitly approved.
- Do not amend existing commits unless explicitly requested.
- Preserve unrelated working-tree changes.
- Use non-interactive git commands only.
- Treat the repo audit as a safety-first operation: identify drift, stale refs, duplicate paths, ghost refs, and uncommitted noise before changing anything.

Required workflow:
1. Confirm current branch, status, upstream tracking, and repository identity.
2. Inspect remotes, local/remote branches, tags, and ref state for drift or stale references.
3. Fetch remote updates.
4. Report ahead and behind counts against upstream.
5. If behind, pull with rebase and resolve conflicts safely without discarding user changes.
6. Run repository validation or quality gates required by hooks.
7. Stage only intended files.
8. Create a clear commit message that reflects the scoped change.
9. Push to upstream branch.
10. Return a final sync summary that includes:
    - Branch name
    - Ahead and behind result before sync
    - Commit hash pushed
    - Files included in commit
    - Files intentionally excluded
    - Validation or hook outcomes
    - Repo confidence rating for alignment and hygiene

Output expectations:
- Show the exact commands run.
- Explain why each step was performed.
- If blocked, stop and report the blocker with the safest next action.
- Include a short repo-audit verdict such as: healthy, minor drift, stale refs found, or blocked by unresolved conflicts.

Safety checks:
- If there are unrelated modified or untracked files, leave them out unless asked to include them.
- If remote has diverged and rebase cannot proceed cleanly, stop and request direction.
- If any check fails, do not push until the issue is addressed.
- If the repo is missing expected structure, has duplicate paths, or contains unexpected artifacts, report them before proceeding.
