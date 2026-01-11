import os
import json
from datetime import datetime
from typing import Any, Dict, Optional

_DEFAULT_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
_DEFAULT_LOG_FILE = os.path.join(_DEFAULT_LOG_DIR, "events.jsonl")


def _ensure_log_dir(path: str) -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        pass


def log_event(category: str, data: Dict[str, Any], log_file: Optional[str] = None) -> None:
    """Append a JSONL event to the log file.

    Args:
        category: Short event category label (e.g., "outreach", "resume").
        data: Arbitrary event payload; must be JSON-serializable.
        log_file: Optional explicit path to log file; defaults to logs/events.jsonl.
    """
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "category": category,
        **data,
    }
    path = log_file or _DEFAULT_LOG_FILE
    _ensure_log_dir(path)
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Logging failures should never crash the app
        pass
