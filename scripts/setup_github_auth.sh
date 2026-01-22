#!/bin/bash
# GitHub CLI Authentication Setup Script
# This script helps developers authenticate with GitHub CLI (gh) for this repository

set -e

echo "================================================"
echo "GitHub CLI Authentication Setup"
echo "================================================"
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo ""
    echo "Please install it first:"
    echo "  macOS:    brew install gh"
    echo "  Linux:    https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo "  Windows:  https://github.com/cli/cli/releases"
    echo ""
    exit 1
fi

echo "✓ GitHub CLI (gh) is installed"
echo ""

# Check current authentication status
echo "Checking current authentication status..."
if gh auth status &> /dev/null; then
    echo "✓ You are already authenticated with GitHub"
    echo ""
    gh auth status
    echo ""
    read -p "Do you want to login again? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup complete!"
        exit 0
    fi
else
    echo "⚠ Not currently authenticated with GitHub"
    echo ""
fi

# Perform authentication
echo "Starting GitHub CLI authentication..."
echo ""
echo "You will be prompted to:"
echo "  1. Choose authentication method (web browser or token)"
echo "  2. Authenticate via GitHub"
echo "  3. Choose default git protocol (HTTPS or SSH)"
echo ""

# Run gh auth login
gh auth login

# Verify authentication
echo ""
echo "Verifying authentication..."
if gh auth status &> /dev/null; then
    echo "✓ Successfully authenticated!"
    echo ""
    gh auth status
    echo ""
    echo "================================================"
    echo "Setup Complete!"
    echo "================================================"
    echo ""
    echo "You can now use GitHub CLI commands like:"
    echo "  gh repo view"
    echo "  gh pr list"
    echo "  gh issue list"
    echo ""
else
    echo "❌ Authentication failed. Please try again."
    exit 1
fi
