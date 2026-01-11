"""
Minimal prompt renderer for Phase 3E.

Deterministic, side-effect free rendering of templates with {{var}} placeholders.
Avoids external dependencies; templates should not use control flow.
"""

from __future__ import annotations

import re
from typing import Any, Dict

_PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}")


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    # Join lists deterministically
    if isinstance(value, (list, tuple, set)):
        try:
            return ", ".join(str(v) for v in value)
        except Exception:
            return ", ".join(sorted(str(v) for v in value))
    return str(value)


def render_prompt(template_str: str, context: Dict[str, Any]) -> str:
    """
    Render a prompt from a simple {{var}} template string and context.

    Deterministic for a given template + context; side-effect free.
    Missing keys render as empty string.
    """

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        # Support dotted paths like a.b if provided
        cur: Any = context
        try:
            for part in key.split("."):
                if isinstance(cur, dict):
                    cur = cur.get(part)
                else:
                    cur = getattr(cur, part, None)
        except Exception:
            cur = None
        return _stringify(cur)

    rendered = _PLACEHOLDER.sub(_replace, template_str)
    return rendered.strip()
