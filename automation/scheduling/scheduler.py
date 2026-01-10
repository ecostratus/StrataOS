from __future__ import annotations

"""
Scheduler helpers for Phase 3B.

Pure functions only. All time computations use UTC and must be deterministic
under frozen time for tests.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any


def compute_next_run(now_utc: datetime, config: Dict[str, Any]) -> datetime:
    """Compute the next run time in UTC based on the provided config.

    Supports two modes:
    - interval: next run is `now_utc + interval_minutes`
    - window: next run is today's window time if in the future, otherwise tomorrow's

    Args:
        now_utc: Current UTC time (timezone-aware).
        config: Configuration mapping including scheduling.* keys.

    Returns:
        A timezone-aware datetime representing the next run timestamp in UTC.
    """
    sched = (config.get("scheduling") or {})
    mode = str(sched.get("mode", "interval")).lower()
    if mode == "window":
        wt = str(sched.get("window_time", "09:00"))
        try:
            hh, mm = [int(x) for x in wt.split(":", 1)]
        except Exception:
            hh, mm = 9, 0
        today_window = now_utc.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if now_utc.tzinfo is None:
            today_window = today_window.replace(tzinfo=timezone.utc)
        if now_utc <= today_window:
            return today_window
        # else next day
        return (today_window + timedelta(days=1))
    # default interval mode
    interval = int((sched.get("interval_minutes") or 60))
    return now_utc + timedelta(minutes=interval)


def should_run(
    now_utc: datetime, last_run_ts: Optional[datetime], config: Dict[str, Any]
) -> bool:
    """Determine if the pipeline should run at now_utc.

    - interval: run when `last_run_ts` is None or `now_utc - last_run_ts >= interval`
    - window: run once per day at window time; if `now_utc` is before today's window, do not run.

    Args:
        now_utc: Current UTC time (timezone-aware).
        last_run_ts: The last run timestamp in UTC, if any.
        config: Configuration mapping including scheduling.* keys.

    Returns:
        True if a run should occur at now_utc; False otherwise.
    """
    sched = (config.get("scheduling") or {})
    mode = str(sched.get("mode", "interval")).lower()
    if mode == "window":
        wt = str(sched.get("window_time", "09:00"))
        try:
            hh, mm = [int(x) for x in wt.split(":", 1)]
        except Exception:
            hh, mm = 9, 0
        today_window = now_utc.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if now_utc.tzinfo is None:
            today_window = today_window.replace(tzinfo=timezone.utc)
        if now_utc < today_window:
            return False
        # After window time: run if we haven't run at/after today's window
        if last_run_ts is None:
            return True
        # If last run occurred before today's window, we should run
        return last_run_ts < today_window
    # interval mode
    interval = int((sched.get("interval_minutes") or 60))
    if last_run_ts is None:
        return True
    return (now_utc - last_run_ts) >= timedelta(minutes=interval)
