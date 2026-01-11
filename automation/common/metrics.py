import os
import json
from typing import Dict, Any

_DEFAULT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
_DEFAULT_FILE = os.path.join(_DEFAULT_DIR, "metrics.json")


def _ensure_dir(path: str) -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        pass


def _load(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(path: str, data: Dict[str, Any]) -> None:
    _ensure_dir(path)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def inc(category: str, counter: str, amount: int = 1, path: str = _DEFAULT_FILE) -> None:
    """Increment a named counter for a category.

    Example: inc("outreach", "renders") -> logs/metrics.json {"outreach": {"renders": N}}
    """
    data = _load(path)
    cat = data.setdefault(category, {})
    cat[counter] = int(cat.get(counter, 0)) + amount
    data[category] = cat
    _save(path, data)


def get_summary(path: str = _DEFAULT_FILE) -> Dict[str, Any]:
    """Return metrics summary dictionary."""
    return _load(path)
