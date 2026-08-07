#!/usr/bin/env bash
set -euo pipefail

# Reusable branch hygiene audit.
# Produces a control matrix with verified, blocked, and cleanup candidate states.

REPO="${1:-ecostratus/StrataOS}"
API_ROOT="https://api.github.com/repos/${REPO}"
WORKTREE_ROOT="${2:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: required command not found: $1" >&2
    exit 1
  fi
}

require_cmd curl
require_cmd jq
require_cmd sort
require_cmd comm
require_cmd mktemp
require_cmd wc
require_cmd tr
require_cmd git

note() {
  printf '%s\n' "$*"
}

matrix_row() {
  local domain="$1"
  local status="$2"
  local evidence="$3"
  printf 'MATRIX\t%s\t%s\t%s\n' "$domain" "$status" "$evidence"
}

workdir="$(mktemp -d "${TMPDIR:-/tmp}/branch-audit.XXXXXX")"
trap 'rm -rf "$workdir"' EXIT

remote_heads="$workdir/remote_heads.txt"
local_heads="$workdir/local_heads.txt"
tracked_heads="$workdir/tracked_heads.txt"
open_heads="$workdir/open_heads.txt"
merged_heads="$workdir/merged_heads.txt"
closed_unmerged_heads="$workdir/closed_unmerged_heads.txt"
merged_remote_candidates="$workdir/merged_remote_candidates.txt"
closed_unmerged_remote="$workdir/closed_unmerged_remote.txt"
stale_local_heads="$workdir/stale_local_heads.txt"
detached_head_flag="$workdir/detached_head_flag.txt"

fetch_json() {
  local url="$1"
  local out="$2"
  local http_code
  http_code="$(curl -sS -w "%{http_code}" "$url" -o "$out")"
  if [[ "$http_code" -lt 200 || "$http_code" -ge 300 ]]; then
    echo "ERROR: GitHub API request failed (${http_code}) for ${url}" >&2
    if [[ -s "$out" ]]; then
      echo "Response:" >&2
      cat "$out" >&2
    fi
    exit 1
  fi
}

branches_json="$workdir/branches.json"
open_prs_json="$workdir/open_prs.json"
closed_prs_json="$workdir/closed_prs.json"

fetch_json "${API_ROOT}/branches?per_page=100" "$branches_json"
fetch_json "${API_ROOT}/pulls?state=open&per_page=100" "$open_prs_json"
fetch_json "${API_ROOT}/pulls?state=closed&per_page=100" "$closed_prs_json"

jq -r '.[].name' "$branches_json" | sort -u > "$remote_heads"
jq -r '.[].head.ref' "$open_prs_json" | sort -u > "$open_heads"
jq -r '.[] | select(.merged_at) | .head.ref' "$closed_prs_json" | sort -u > "$merged_heads"
jq -r '.[] | select(.merged_at == null) | .head.ref' "$closed_prs_json" | sort -u > "$closed_unmerged_heads"

git -C "$WORKTREE_ROOT" for-each-ref refs/heads --format='%(refname:short)' | sort -u > "$local_heads"
git -C "$WORKTREE_ROOT" for-each-ref refs/heads --format='%(refname:short)|%(upstream:short)' | awk -F'|' '$2 != "" {print $1}' | sort -u > "$tracked_heads"

if git -C "$WORKTREE_ROOT" symbolic-ref -q --short HEAD >/dev/null 2>&1; then
  : > "$detached_head_flag"
else
  printf 'detached\n' > "$detached_head_flag"
fi

comm -23 "$local_heads" "$remote_heads" > "$stale_local_heads"

comm -12 "$remote_heads" "$merged_heads" > "$merged_remote_candidates"
comm -12 "$remote_heads" "$closed_unmerged_heads" > "$closed_unmerged_remote"

echo "Repository: ${REPO}"
echo "Worktree: ${WORKTREE_ROOT}"

matrix_row "Git topology" "Pass" "local_heads=$(wc -l < "$local_heads" | tr -d ' '), remote_heads=$(wc -l < "$remote_heads" | tr -d ' '), tracked_heads=$(wc -l < "$tracked_heads" | tr -d ' ')"

if [[ -s "$detached_head_flag" ]]; then
  matrix_row "Current checkout" "Fail" "detached HEAD detected"
else
  matrix_row "Current checkout" "Pass" "branch=$(git -C "$WORKTREE_ROOT" symbolic-ref -q --short HEAD 2>/dev/null)"
fi

if [[ -s "$stale_local_heads" ]]; then
  matrix_row "Local branch drift" "Fail" "untracked_or_stale_local_heads=$(wc -l < "$stale_local_heads" | tr -d ' ')"
else
  matrix_row "Local branch drift" "Pass" "all local heads have remote counterparts"
fi

matrix_row "Remote branch inventory" "Pass" "remote_heads=$(wc -l < "$remote_heads" | tr -d ' ')"
matrix_row "Open PR heads" "Pass" "open_pr_heads=$(wc -l < "$open_heads" | tr -d ' ')"

if [[ -s "$merged_remote_candidates" ]]; then
  matrix_row "Cleanup candidates" "Pass" "merged_remote_candidates=$(wc -l < "$merged_remote_candidates" | tr -d ' ')"
else
  matrix_row "Cleanup candidates" "Pass" "none"
fi

if [[ -s "$closed_unmerged_remote" ]]; then
  matrix_row "Unsafe remote heads" "Blocked" "closed_unmerged_remote=$(wc -l < "$closed_unmerged_remote" | tr -d ' ')"
else
  matrix_row "Unsafe remote heads" "Pass" "none"
fi

echo "---LOCAL BRANCHES---"
cat "$local_heads"

echo "---REMOTE HEADS---"
cat "$remote_heads"

echo "---TRACKED LOCAL BRANCHES---"
cat "$tracked_heads"

echo "---OPEN PR HEADS (active)---"
cat "$open_heads"

echo "---MERGED PR HEADS THAT STILL EXIST REMOTELY (safe deletion candidates)---"
if [[ -s "$merged_remote_candidates" ]]; then
  cat "$merged_remote_candidates"
else
  echo "(none)"
fi

echo "---CLOSED-UNMERGED PR HEADS THAT STILL EXIST REMOTELY (not safe by default)---"
if [[ -s "$closed_unmerged_remote" ]]; then
  cat "$closed_unmerged_remote"
else
  echo "(none)"
fi

echo "---SUGGESTED DELETE COMMANDS (review first)---"
if [[ -s "$merged_remote_candidates" ]]; then
  while IFS= read -r branch; do
    [[ -z "$branch" ]] && continue
    echo "git push origin --delete ${branch}"
  done < "$merged_remote_candidates"
else
  echo "(none)"
fi
