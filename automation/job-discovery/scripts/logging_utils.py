"""
Structured logging helpers for job discovery pipeline.
"""
from __future__ import annotations

import json
from datetime import datetime
try:  # Python 3.11+
    from datetime import UTC  # type: ignore
except Exception:  # Python <3.11
    from datetime import timezone as _tz  # type: ignore
    UTC = _tz.utc  # type: ignore
from typing import Any, Optional


_SINK_PATH: Optional[str] = None


def set_jsonl_sink(path: Optional[str]) -> None:
    global _SINK_PATH
    _SINK_PATH = path


def get_jsonl_sink() -> Optional[str]:
    return _SINK_PATH


def _append_jsonl(line: str) -> None:
    if not _SINK_PATH:
        return
    try:
        with open(_SINK_PATH, "a", encoding="utf-8") as f:
            f.write(line)
            f.write("\n")
    except Exception:
        # Best-effort; do not raise
        pass


def structured_log(logger, level: str, event: str, **fields: Any) -> None:
    payload = {
        "ts": datetime.now(UTC).isoformat(),
        "level": level.upper(),
        "event": event,
        **fields,
    }
    line = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    if level.lower() == "error":
        logger.error(line)
    elif level.lower() == "warning":
        logger.warning(line)
    else:
        logger.info(line)
    _append_jsonl(line)
