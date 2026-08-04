#!/usr/bin/env bash
set -euo pipefail

# Reusable remote branch hygiene audit.
# Compares current remote heads against open/merged/closed PR heads
# and prints explicit cleanup candidates.

REPO="${1:-ecostratus/StrataOS}"
API_ROOT="https://api.github.com/repos/${REPO}"

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

workdir="$(mktemp -d "${TMPDIR:-/tmp}/branch-audit.XXXXXX")"
trap 'rm -rf "$workdir"' EXIT

remote_heads="$workdir/remote_heads.txt"
open_heads="$workdir/open_heads.txt"
merged_heads="$workdir/merged_heads.txt"
closed_unmerged_heads="$workdir/closed_unmerged_heads.txt"
merged_remote_candidates="$workdir/merged_remote_candidates.txt"
closed_unmerged_remote="$workdir/closed_unmerged_remote.txt"

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

comm -12 "$remote_heads" "$merged_heads" > "$merged_remote_candidates"
comm -12 "$remote_heads" "$closed_unmerged_heads" > "$closed_unmerged_remote"

echo "Repository: ${REPO}"
printf 'REMOTE_HEADS_COUNT\t%s\n' "$(wc -l < "$remote_heads" | tr -d ' ')"
printf 'OPEN_PR_HEADS_COUNT\t%s\n' "$(wc -l < "$open_heads" | tr -d ' ')"
printf 'MERGED_PR_HEADS_COUNT\t%s\n' "$(wc -l < "$merged_heads" | tr -d ' ')"
printf 'CLOSED_UNMERGED_PR_HEADS_COUNT\t%s\n' "$(wc -l < "$closed_unmerged_heads" | tr -d ' ')"

printf 'SAFE_DELETION_CANDIDATES_COUNT\t%s\n' "$(wc -l < "$merged_remote_candidates" | tr -d ' ')"
printf 'UNSAFE_CLOSED_UNMERGED_REMOTE_COUNT\t%s\n' "$(wc -l < "$closed_unmerged_remote" | tr -d ' ')"

echo "---REMOTE HEADS---"
cat "$remote_heads"

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
