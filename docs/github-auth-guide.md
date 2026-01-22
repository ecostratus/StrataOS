# GitHub Authentication Quick Reference

This document provides quick commands and tips for GitHub CLI authentication.

## Check Authentication Status

```bash
gh auth status
```

## Login to GitHub

### Interactive Login (Recommended)

```bash
gh auth login
```

This will prompt you to:
1. Choose GitHub.com or GitHub Enterprise
2. Select HTTPS or SSH protocol
3. Authenticate via web browser or paste a token
4. Complete authentication

### Login with Token

```bash
gh auth login --with-token < token.txt
```

Or:

```bash
echo "YOUR_TOKEN_HERE" | gh auth login --with-token
```

### Using the Setup Script

Run the automated setup script:

```bash
./scripts/setup_github_auth.sh
```

## Refresh Token

If your token expires:

```bash
gh auth refresh
```

## Logout

```bash
gh auth logout
```

## Environment Variables

The GitHub CLI looks for authentication in this order:

1. `GH_TOKEN` environment variable
2. `GITHUB_TOKEN` environment variable
3. Authentication saved by `gh auth login`

### Setting Token as Environment Variable

```bash
export GITHUB_TOKEN="your_token_here"
```

Add to your shell profile for persistence:

```bash
echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

Or for zsh:

```bash
echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

## Creating a Personal Access Token

1. Go to [GitHub Settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name
4. Select scopes based on your needs:
   - `repo` - Full control of private repositories
   - `workflow` - Update GitHub Action workflows
   - `read:org` - Read org and team membership
   - `admin:public_key` - Full control of user public keys
5. Click "Generate token"
6. Copy the token immediately (you won't be able to see it again)
7. Store it securely

## Common Issues and Solutions

### "Not authenticated"

**Solution:** Run `gh auth login` and complete authentication

### "Token expired"

**Solution:** Run `gh auth refresh`

### "Permission denied"

**Solution:** Check token scopes. You may need to regenerate with additional permissions.

### "Rate limit exceeded"

**Solution:** Authenticate to get higher rate limits (5000 req/hour vs 60 req/hour)

## Verification Commands

After authentication, verify with these commands:

```bash
# Check authentication status
gh auth status

# Test API access
gh api user

# List your repositories
gh repo list

# Check rate limit
gh api rate_limit

# Run the test script (Python)
python3 scripts/test_github_auth.py
```

The `test_github_auth.py` script will:
- Check if gh CLI is authenticated
- Look for GitHub tokens in environment or config
- Test API access with your credentials
- Display your authenticated user info
- Show your current rate limit

## Security Best Practices

1. **Never commit tokens** to version control
2. **Use tokens with minimal scopes** required for your task
3. **Rotate tokens regularly** (e.g., every 90 days)
4. **Delete tokens** when no longer needed
5. **Use environment variables** or secure credential managers
6. **Set token expiration** when creating tokens
7. **Monitor token usage** in GitHub Settings

## Additional Resources

- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub CLI Authentication](https://cli.github.com/manual/gh_auth)
- [Creating Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)

## Quick Troubleshooting

| Issue | Command | Expected Result |
|-------|---------|----------------|
| Check if logged in | `gh auth status` | Shows authenticated account |
| Login | `gh auth login` | Interactive prompt |
| Refresh token | `gh auth refresh` | Token refreshed |
| Test API access | `gh api user` | Returns user JSON |
| Check rate limit | `gh api rate_limit` | Shows limit info |
| View token scopes | `gh auth status -t` | Shows token and scopes |

## Configuration File Location

GitHub CLI stores auth configuration in:
- Linux/macOS: `~/.config/gh/hosts.yml`
- Windows: `%AppData%\GitHub CLI\hosts.yml`

**Note:** This file is already in `.gitignore` to prevent accidental commits.
