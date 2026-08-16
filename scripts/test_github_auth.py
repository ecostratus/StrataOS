#!/usr/bin/env python3
"""Example: using shared GitHub authentication helpers in automation scripts."""

import sys
import urllib.error

from github_auth import check_github_auth, format_http_error, make_github_api_request, resolve_github_token


def main():
    """Main function to demonstrate GitHub authentication."""
    print("=" * 60)
    print("GitHub Authentication Example")
    print("=" * 60)
    print()

    print("Checking gh CLI authentication...")
    if check_github_auth():
        print(" Authenticated with GitHub via gh CLI")
    else:
        print("  Not authenticated with gh CLI")
        print("  Run: gh auth login")
    print()

    print("Looking for GitHub token...")
    token, source = resolve_github_token()
    if token and source:
        print(f" Found GitHub token from {source}")
    else:
        print("  No GitHub token found")
    print()

    if token:
        print("Testing API access...")
        try:
            user_data = make_github_api_request("user", token)
        except urllib.error.HTTPError as exc:
            user_data = None
            print(f" API request failed: {format_http_error(exc)}")
        except Exception as exc:
            user_data = None
            print(f" Error making API request: {exc}")

        if user_data:
            print(" API access successful!")
            print(f"  Authenticated as: {user_data.get('login', 'Unknown')}")
            print(f"  Name: {user_data.get('name', 'Not set')}")
            print(f"  Public repos: {user_data.get('public_repos', 0)}")
        else:
            print(" API access failed")
        print()

        print("Checking rate limit...")
        try:
            rate_limit = make_github_api_request("rate_limit", token)
        except urllib.error.HTTPError as exc:
            rate_limit = None
            print(f" API request failed: {format_http_error(exc)}")
        except Exception as exc:
            rate_limit = None
            print(f" Error making API request: {exc}")
        if rate_limit:
            core = rate_limit.get("rate", {})
            remaining = core.get("remaining", 0)
            limit = core.get("limit", 0)
            print(f"  Rate limit: {remaining}/{limit} remaining")
    else:
        print(" No GitHub token available")
        print()
        print("To use GitHub API in your scripts, you can:")
        print("  1. Run: gh auth login")
        print("  2. Set environment variable: export GITHUB_TOKEN='your_token'")
        print("  3. Add token to config/env.json in the 'github' section")
        print()
        return 1

    print()
    print("=" * 60)
    print("Example Complete")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
