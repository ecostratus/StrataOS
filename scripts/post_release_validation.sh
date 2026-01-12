#!/usr/bin/env bash
set -euo pipefail

echo "=== Post-Release Validation ==="

echo "[1/5] Running tests..."
./.venv/bin/python -m pytest -q --tb=short

echo "[2/5] Running docs CI..."
python3 scripts/ci/check_docs.py

echo "[3/5] Validating combined runner (full-sources mode)..."
./.venv/bin/python automation/common/run_prompts.py \
  --outreach-context config/outreach_context.sample.json \
  --outreach-output-dir output/outreach \
  --resume-context config/resume_context.sample.json \
  --resume-output-dir output/resume

echo "[4/5] Checking for uncommitted changes..."
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Uncommitted changes detected:"
  git status --porcelain
  exit 1
fi

echo "[5/5] Confirming tag exists..."
if ! git describe --tags --exact-match HEAD >/dev/null 2>&1; then
  echo "No tag found on HEAD."
  exit 1
fi

echo "Post-release validation complete."
