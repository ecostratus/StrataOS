# Local and Remote Sync Prompt

Use this prompt for all branch sync and repository hygiene runs.

## Prompt

You are performing local and remote repository sync alignment and hygiene.

Repository rules:
- Never use destructive commands such as git reset --hard or git checkout -- unless explicitly approved.
- Do not amend existing commits unless explicitly requested.
- Preserve unrelated working-tree changes.
- Use non-interactive git commands only.

Required workflow:
1. Confirm current branch, status, and upstream tracking.
2. Fetch remote updates.
3. Report ahead and behind counts against upstream.
4. If behind, pull with rebase and resolve conflicts safely without discarding user changes.
5. Run repository validation or quality gates required by hooks.
6. Stage only intended files.
7. Create a clear commit message that reflects the scoped change.
8. Push to upstream branch.
9. Return a final sync summary that includes:
   - Branch name
   - Ahead and behind result before sync
   - Commit hash pushed
   - Files included in commit
   - Files intentionally excluded
   - Validation or hook outcomes

Output expectations:
- Show the exact commands run.
- Explain why each step was performed.
- If blocked, stop and report the blocker with the safest next action.

Safety checks:
- If there are unrelated modified or untracked files, leave them out unless asked to include them.
- If remote has diverged and rebase cannot proceed cleanly, stop and request direction.
- If any check fails, do not push until the issue is addressed.
