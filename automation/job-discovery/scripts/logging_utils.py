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
from typing import Any


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
