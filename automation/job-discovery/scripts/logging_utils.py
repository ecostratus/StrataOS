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
import os


_SINK_PATH: Optional[str] = None
_SUPPRESS_STDOUT_IF_JSONL: bool = False


def set_jsonl_sink(path: Optional[str]) -> None:
    global _SINK_PATH
    _SINK_PATH = path
    # Ensure sink file exists so tests can detect it even without logs
    if path:
        try:
            dir_name = os.path.dirname(path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                pass
        except Exception:
            # Best-effort creation
            pass


def set_suppress_stdout_if_jsonl(flag: bool) -> None:
    global _SUPPRESS_STDOUT_IF_JSONL
    _SUPPRESS_STDOUT_IF_JSONL = bool(flag)


def get_jsonl_sink() -> Optional[str]:
    return _SINK_PATH


def get_suppress_stdout_if_jsonl() -> bool:
    return _SUPPRESS_STDOUT_IF_JSONL


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
    # Optionally suppress stdout logging when JSONL sink is active
    suppress_stdout = bool(_SINK_PATH) and _SUPPRESS_STDOUT_IF_JSONL
    if not suppress_stdout:
        if level.lower() == "error":
            logger.error(line)
        elif level.lower() == "warning":
            logger.warning(line)
        else:
            logger.info(line)
    _append_jsonl(line)
