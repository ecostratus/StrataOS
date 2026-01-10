from __future__ import annotations

"""
SQLite storage backend for Phase 3B.

Schema initialization must be idempotent. All primary keys should be deterministic
based on input data (e.g., hashes) to avoid nondeterministic autoincrement usage.
"""

import os
import sqlite3
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Tuple

# Resolve repo root to locate default data directory and config
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
try:
    from config.config_loader import config  # type: ignore
except Exception:
    config = None  # type: ignore


def _db_path() -> str:
    """Resolve SQLite DB path from config or default."""
    default_path = os.path.join(_ROOT, "data", "jobs.db")
    cfg = {}
    if config and hasattr(config, "get"):
        try:
            cfg = config.get("STORAGE", {}) or {}
        except Exception:
            cfg = {}
    return str(cfg.get("sqlite_path", default_path))


def _get_conn() -> sqlite3.Connection:
    path = _db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_schema() -> None:
    """Initialize or migrate the SQLite schema (idempotent)."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_ts TEXT PRIMARY KEY,
            timestamp_iso TEXT NOT NULL,
            summary_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS jobs (
            run_ts TEXT NOT NULL,
            job_id TEXT NOT NULL,
            title TEXT,
            location TEXT,
            company TEXT,
            source TEXT,
            url TEXT,
            posted_date TEXT,
            PRIMARY KEY (run_ts, job_id),
            FOREIGN KEY (run_ts) REFERENCES runs(run_ts) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS enriched (
            run_ts TEXT NOT NULL,
            job_id TEXT NOT NULL,
            features_json TEXT NOT NULL,
            PRIMARY KEY (run_ts, job_id),
            FOREIGN KEY (run_ts, job_id) REFERENCES jobs(run_ts, job_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS scores (
            run_ts TEXT NOT NULL,
            job_id TEXT NOT NULL,
            score REAL,
            bucket TEXT,
            PRIMARY KEY (run_ts, job_id),
            FOREIGN KEY (run_ts, job_id) REFERENCES jobs(run_ts, job_id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()


def insert_run(run_summary: Dict[str, Any]) -> None:
    """Insert a run summary row keyed by run timestamp string (run_ts).

    Expects either `run_summary["run_ts"]` (YYYYMMDD_%H%M%S) or derives it from
    `run_summary["timestamp_utc"]` (ISO) if present.
    """
    ts_iso = str(run_summary.get("timestamp_utc", ""))
    run_ts = str(run_summary.get("run_ts", ""))
    if not run_ts:
        try:
            # Example ISO: 2025-01-01T12:00:00+00:00
            dt = datetime.fromisoformat(ts_iso.replace("Z", "+00:00"))
            run_ts = dt.strftime("%Y%m%d_%H%M%S")
        except Exception:
            raise ValueError("run_summary must include 'run_ts' or a valid 'timestamp_utc'")
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO runs(run_ts, timestamp_iso, summary_json) VALUES (?, ?, ?)",
        (run_ts, ts_iso or "", json.dumps(run_summary, separators=(",", ":"))),
    )
    conn.commit()
    conn.close()


def insert_jobs(run_ts: str, jobs: List[Dict[str, Any]]) -> None:
    """Insert discovered jobs for a given run timestamp.

    Primary key is (run_ts, job_id) where job_id is a deterministic hash of
    "source|url".
    """
    conn = _get_conn()
    cur = conn.cursor()
    for j in jobs:
        src = str(j.get("source", ""))
        url = str(j.get("url", ""))
        job_id = hashlib.sha1(f"{src}|{url}".encode("utf-8")).hexdigest()
        cur.execute(
            """
            INSERT OR IGNORE INTO jobs(run_ts, job_id, title, location, company, source, url, posted_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_ts,
                job_id,
                j.get("title"),
                j.get("location"),
                j.get("company"),
                src,
                url,
                j.get("posted_date"),
            ),
        )
    conn.commit()
    conn.close()


def insert_enriched(run_ts: str, enriched: List[Dict[str, Any]]) -> None:
    """Insert enriched features for a given run timestamp.

    Expects entries containing at least `source` and `url` to derive job_id.
    Stores features as compact JSON.
    """
    conn = _get_conn()
    cur = conn.cursor()
    for e in enriched:
        src = str(e.get("source", ""))
        url = str(e.get("url", ""))
        job_id = hashlib.sha1(f"{src}|{url}".encode("utf-8")).hexdigest()
        cur.execute(
            "INSERT OR REPLACE INTO enriched(run_ts, job_id, features_json) VALUES (?, ?, ?)",
            (run_ts, job_id, json.dumps(e, separators=(",", ":"))),
        )
    conn.commit()
    conn.close()


def insert_scores(run_ts: str, scores: List[Dict[str, Any]]) -> None:
    """Insert scores for a given run timestamp.

    Expects entries containing at least `source` and `url` to derive job_id.
    """
    conn = _get_conn()
    cur = conn.cursor()
    for s in scores:
        src = str(s.get("source", ""))
        url = str(s.get("url", ""))
        job_id = hashlib.sha1(f"{src}|{url}".encode("utf-8")).hexdigest()
        cur.execute(
            "INSERT OR REPLACE INTO scores(run_ts, job_id, score, bucket) VALUES (?, ?, ?, ?)",
            (run_ts, job_id, s.get("score"), s.get("bucket")),
        )
    conn.commit()
    conn.close()


def prune(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply retention policy and return a summary of deletions.

    Combined rule: delete runs that are older than `days` AND not within the
    latest `keep_latest_n_runs`. Always protect at least the latest run.
    Purge order is ascending by run timestamp.
    """
    retention = (config.get("RETENTION") or {})
    days = retention.get("days")
    keep_n = int(retention.get("keep_latest_n_runs", 1) or 1)
    if days is None:
        return {"deleted_runs": [], "kept_runs": []}
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT run_ts, timestamp_iso FROM runs ORDER BY run_ts ASC")
    rows: List[Tuple[str, str]] = cur.fetchall()
    run_list = [r[0] for r in rows]
    # Determine cutoff
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=int(days))
    # Parse run_ts into datetimes
    def _parse(ts: str) -> datetime:
        return datetime.strptime(ts, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)

    eligible_by_age = [ts for ts in run_list if _parse(ts) < cutoff]
    latest_n = set(run_list[-keep_n:]) if keep_n > 0 else set()
    to_delete = [ts for ts in eligible_by_age if ts not in latest_n]
    deleted: List[str] = []
    for ts in to_delete:
        cur.execute("DELETE FROM runs WHERE run_ts = ?", (ts,))
        deleted.append(ts)
    conn.commit()
    conn.close()
    kept = [ts for ts in run_list if ts not in deleted]
    return {"deleted_runs": deleted, "kept_runs": kept}
