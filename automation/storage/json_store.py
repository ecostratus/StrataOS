from __future__ import annotations

"""
JSON storage backend for Phase 3B.

Writes run-scoped artifacts under deterministic filenames and maintains an index
for discoverability. Retention logic removes older runs deterministically.
"""

import os
import json
import shutil
from typing import Any, Dict, List

# Resolve repo root to locate default data directory and config
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
try:
    from config.config_loader import config  # type: ignore
except Exception:
    config = None  # type: ignore


def _base_dir() -> str:
    """Resolve JSON store base directory from config or default."""
    default_dir = os.path.join(_ROOT, "data", "json-store")
    cfg = {}
    if config and hasattr(config, "get"):
        try:
            cfg = config.get("STORAGE", {}) or {}
        except Exception:
            cfg = {}
    return str(cfg.get("json_dir", default_dir))


def write_run(run_ts: str, summary: Dict[str, Any]) -> str:
    """Write a run summary for the given run timestamp.

    Args:
        run_ts: UTC run timestamp (string form) shared across artifacts.
        summary: Mapping of run metadata and metrics snapshot.

    Returns:
        Path to the written summary file.
    """
    base = _base_dir()
    run_dir = os.path.join(base, run_ts)
    os.makedirs(run_dir, exist_ok=True)
    path = os.path.join(run_dir, "summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, separators=(",", ":"))
    # Update index for discoverability
    idx_path = os.path.join(base, "index.json")
    try:
        idx = []
        if os.path.exists(idx_path):
            with open(idx_path, "r", encoding="utf-8") as f:
                idx = json.load(f) or []
        if run_ts not in idx:
            idx.append(run_ts)
            idx.sort()
        with open(idx_path, "w", encoding="utf-8") as f:
            json.dump(idx, f, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        # Non-fatal
        pass
    return path


def write_jsonl(kind: str, run_ts: str, items: List[Dict[str, Any]]) -> str:
    """Write a JSONL artifact for a given run timestamp and kind.

    Args:
        kind: One of {"jobs", "enriched", "scores"}.
        run_ts: UTC run timestamp (string form) shared across artifacts.
        items: List of items to serialize.

    Returns:
        Path to the written artifact file.
    """
    base = _base_dir()
    run_dir = os.path.join(base, run_ts)
    os.makedirs(run_dir, exist_ok=True)
    path = os.path.join(run_dir, f"{kind}.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False, separators=(",", ":")))
            f.write("\n")
    return path


def prune(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply retention policy to JSON-backed runs deterministically.

    Args:
        config: Configuration mapping including retention.* keys.

    Returns:
        A summary dict (e.g., {"deleted_runs": [...], "kept_runs": [...]}).
    """
    retention = (config.get("RETENTION") or {})
    days = retention.get("days")
    keep_n = int(retention.get("keep_latest_n_runs", 1) or 1)
    base = _base_dir()
    if days is None or not os.path.isdir(base):
        return {"deleted_runs": [], "kept_runs": []}
    # Determine run directories (names follow run_ts format)
    run_dirs = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and "_" in d]
    run_dirs.sort()  # Ascending by run_ts
    from datetime import datetime, timezone, timedelta

    def _parse(ts: str) -> datetime:
        return datetime.strptime(ts, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=int(days))
    eligible_by_age = [ts for ts in run_dirs if _parse(ts) < cutoff]
    latest_n = set(run_dirs[-keep_n:]) if keep_n > 0 else set()
    to_delete = [ts for ts in eligible_by_age if ts not in latest_n]
    deleted = []
    for ts in to_delete:
        shutil.rmtree(os.path.join(base, ts), ignore_errors=True)
        deleted.append(ts)
    kept = [ts for ts in run_dirs if ts not in deleted]
    # Update index
    idx_path = os.path.join(base, "index.json")
    try:
        with open(idx_path, "w", encoding="utf-8") as f:
            json.dump(kept, f, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        pass
    return {"deleted_runs": deleted, "kept_runs": kept}
