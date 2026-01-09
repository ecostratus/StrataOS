"""
Consulting Offer Generator v1
Placeholder for consulting proposal generation script.

This script will:
- Load client and opportunity information
- Generate professional consulting proposals
- Export formatted proposals for review

See prompt-spec.md for full specification.
"""

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.config_loader import config

def main():
    """Main entry point for consulting offer generator."""
    config.initialize()
    environment = config.get("SYSTEM_ENVIRONMENT", "development")
    proposal_template = config.get(
        "CONSULTING_PROPOSAL_TEMPLATE_PATH",
        "./consulting/templates/proposal_template.docx",
    )
    hourly_rate = config.get_int("CONSULTING_HOURLY_RATE", 150)
    print("Consulting offer generator v1 - Structure placeholder")
    print(f"Env: {environment} | Template: {proposal_template} | Rate: {hourly_rate}")

if __name__ == "__main__":
    main()
