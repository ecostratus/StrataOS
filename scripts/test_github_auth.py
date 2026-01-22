#!/usr/bin/env python3
"""
Example: Using GitHub Authentication in Automation Scripts

This script demonstrates how to use GitHub authentication in your
automation scripts, either via environment variables or gh CLI.
"""

import os
import subprocess
import sys
import json
from pathlib import Path


def get_github_token():
    """
    Get GitHub token from environment or gh CLI.
    
    Returns:
        str: GitHub token or None if not authenticated
    """
    # Try environment variables first (GH_TOKEN, then GITHUB_TOKEN)
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        print("✓ Found GitHub token in environment variables")
        return token
    
    # Try to get token from gh CLI
    try:
        result = subprocess.run(
            ['gh', 'auth', 'token'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            print("✓ Found GitHub token from gh CLI")
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Try to load from config
    config_path = Path(__file__).parent.parent / 'config' / 'env.json'
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
                token = config.get('github', {}).get('token', '').strip()
                if token:
                    print("✓ Found GitHub token in config/env.json")
                    return token
        except (json.JSONDecodeError, IOError):
            pass
    
    print("⚠ No GitHub token found")
    return None


def check_github_auth():
    """
    Check if user is authenticated with GitHub.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    try:
        result = subprocess.run(
            ['gh', 'auth', 'status'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def make_github_api_request(endpoint, token=None):
    """
    Make a simple GitHub API request.
    
    Args:
        endpoint (str): API endpoint (e.g., 'user', 'repos')
        token (str, optional): GitHub token
        
    Returns:
        dict: API response or None on error
    """
    import urllib.request
    import urllib.error
    
    url = f"https://api.github.com/{endpoint}"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"❌ API request failed: {e.code} {e.reason}")
        return None
    except Exception as e:
        print(f"❌ Error making API request: {e}")
        return None


def main():
    """Main function to demonstrate GitHub authentication."""
    print("=" * 60)
    print("GitHub Authentication Example")
    print("=" * 60)
    print()
    
    # Check if gh CLI is authenticated
    print("Checking gh CLI authentication...")
    if check_github_auth():
        print("✓ Authenticated with GitHub via gh CLI")
    else:
        print("⚠ Not authenticated with gh CLI")
        print("  Run: gh auth login")
    print()
    
    # Try to get token
    print("Looking for GitHub token...")
    token = get_github_token()
    print()
    
    if token:
        # Make a test API request
        print("Testing API access...")
        user_data = make_github_api_request('user', token)
        
        if user_data:
            print("✓ API access successful!")
            print(f"  Authenticated as: {user_data.get('login', 'Unknown')}")
            print(f"  Name: {user_data.get('name', 'Not set')}")
            print(f"  Public repos: {user_data.get('public_repos', 0)}")
        else:
            print("❌ API access failed")
        print()
        
        # Check rate limit
        print("Checking rate limit...")
        rate_limit = make_github_api_request('rate_limit', token)
        if rate_limit:
            core = rate_limit.get('rate', {})
            remaining = core.get('remaining', 0)
            limit = core.get('limit', 0)
            print(f"  Rate limit: {remaining}/{limit} remaining")
    else:
        print("❌ No GitHub token available")
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


if __name__ == '__main__':
    sys.exit(main())
