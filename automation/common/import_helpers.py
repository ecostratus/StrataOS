"""
Shared helpers for dynamic module loading to handle hyphenated directories.

Rules:
- Never modify public directory names (e.g., job-discovery/ stays hyphenated).
- Use two-stage import: try dotted import first; if that fails, load via importlib.util
  using a repo-root-relative path.
"""

import os
import importlib.util

# Compute repo root from this file
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def load_module_from_path(rel_path: str, module_name: str):
    """
    Load a Python module from a repo-root-relative path.

    rel_path: e.g., "automation/job-discovery/scripts/enrichment_transforms.py"
    module_name: a unique name to bind the loaded module under (e.g., "enrichment_transforms")

    Returns the loaded module object or None if load fails.
    """
    full_path = os.path.join(_REPO_ROOT, rel_path)
    spec = importlib.util.spec_from_file_location(module_name, full_path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    except Exception:
        return None
    return mod
