import argparse
import json
import os
import sys
from typing import Optional

# Ensure repo root on path
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from automation.common.metrics import get_summary, reset


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Metrics CLI: show summary or reset counters")
    parser.add_argument("--summary", action="store_true", help="Print metrics summary as JSON")
    parser.add_argument("--reset", action="store_true", help="Reset metrics counters")
    parser.add_argument("--file", default=None, help="Optional metrics file path (defaults to logs/metrics.json)")
    args = parser.parse_args(argv)

    if args.reset:
        reset(args.file)  # type: ignore[arg-type]
        print("Metrics reset.")
        # If both requested, also show summary after reset
        if args.summary:
            s = get_summary(args.file)  # type: ignore[arg-type]
            print(json.dumps(s, ensure_ascii=False, indent=2))
        return 0

    if args.summary or not (args.summary or args.reset):
        # Default action is summary
        s = get_summary(args.file)  # type: ignore[arg-type]
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
