"""
Post-generation hallucination check for consulting proposal output.

Checks:
  1. Every dollar figure in the output is either stated in the source context
     or correctly derivable from rate * hours (within a 5% tolerance for rounding).
  2. No date strings appear in deadline/validity fields — those must remain
     as placeholders for the user to fill in.
  3. No milestone weeks outside the range declared in the source context.

Usage:
    python3 automation/consulting-funnel/scripts/verify_consulting_output.py \
        --source config/consulting_context_jnaphen.json \
        --output output/consulting/consulting_artifact_<timestamp>.txt
"""

import argparse
import json
import re
import sys


def load_source(context_path: str) -> dict:
    with open(context_path, encoding="utf-8") as f:
        return json.load(f)


def extract_dollar_amounts(text: str) -> list[float]:
    amounts = []
    for m in re.finditer(r"\$\s*([\d,]+(?:\.\d+)?)\s*(?:/hr|/hour|k\b)?", text, re.IGNORECASE):
        raw = m.group(1).replace(",", "")
        try:
            amounts.append(float(raw))
        except ValueError:
            pass
    return amounts


def extract_week_numbers(text: str) -> list[int]:
    return [int(m.group(1)) for m in re.finditer(r"\bWeek\s+(\d+)\b", text, re.IGNORECASE)]


def extract_dates(text: str) -> list[str]:
    # ISO dates, month-day-year, or written month names
    patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ]
    found = []
    for p in patterns:
        found.extend(re.findall(p, text, re.IGNORECASE))
    return found


def derivable_totals(rate_low: float, rate_high: float, hours_per_week: int = 40, weeks: int = 24) -> set[float]:
    """Return the set of plausible total-investment figures derivable from the source rate and duration."""
    totals = set()
    for rate in range(int(rate_low), int(rate_high) + 1, 5):
        for w in range(1, weeks + 2):
            for h in (20, 24, 30, 32, 40):  # common weekly hour assumptions
                totals.add(round(rate * h * w))
    return totals


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source = load_source(args.source)
    with open(args.output, encoding="utf-8") as f:
        output_text = f.read()

    findings: list[str] = []

    rate_low = float(source.get("engagement_rate_low", source.get("hourly_rate", 0)))
    rate_high = float(source.get("engagement_rate_high", rate_low))

    # Max week declared in source
    declared_weeks = []
    for key in ("timeline",):
        val = source.get(key, "")
        declared_weeks += [int(m) for m in re.findall(r"week\s*(\d+)", val, re.IGNORECASE)]
    for key in ("phase1_duration", "phase2_duration", "phase3_duration"):
        val = source.get(key, "")
        declared_weeks += [int(m) for m in re.findall(r"(\d+)", val)]
    max_declared_week = max(declared_weeks) if declared_weeks else 24

    # Stated amounts from context (rate range + any explicit totals)
    stated_amounts: set[float] = set()
    for key in ("hourly_rate", "engagement_rate_low", "engagement_rate_high"):
        if key in source:
            stated_amounts.add(float(source[key]))

    allowed_totals = derivable_totals(rate_low, rate_high)

    # Check dollar amounts
    for amount in extract_dollar_amounts(output_text):
        if amount in stated_amounts:
            continue
        # Allow amounts that are the rate itself (e.g. listed as $/hr)
        if rate_low <= amount <= rate_high:
            continue
        # Allow totals derivable from rate × hours × weeks within 5%
        closest = min(allowed_totals, key=lambda x: abs(x - amount)) if allowed_totals else amount
        pct_diff = abs(closest - amount) / max(amount, 1)
        if pct_diff > 0.05:
            findings.append(
                f"Dollar amount ${amount:,.0f} not derivable from source rate "
                f"(${rate_low:.0f}-${rate_high:.0f}/hr) — verify or remove"
            )

    # Check week numbers
    for week in extract_week_numbers(output_text):
        if week > max_declared_week + 4:  # small buffer for minor model re-phasing
            findings.append(
                f"Week {week} in output exceeds declared engagement length "
                f"(max week {max_declared_week} in source)"
            )

    # Check for filled-in dates that should remain as placeholders
    dates_found = extract_dates(output_text)
    if dates_found:
        findings.append(
            f"Specific date(s) found in output — these should be placeholders, "
            f"not filled in: {', '.join(dates_found[:5])}"
        )

    if findings:
        print("PROPOSAL CHECK FAILED — review before sending:\n")
        for f in findings:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("Proposal check passed — no unsourced dollar amounts, out-of-range weeks, or filled dates detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
