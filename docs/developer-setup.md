# Developer Setup Guide

This guide helps you set up your development environment for the Personal Operating System repository.

## Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- (Optional) Microsoft Excel for viewing/editing templates

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ecostratus/personal-operating-system-60d.git
cd personal-operating-system-60d
```

### 2. GitHub CLI Authentication

This repository uses GitHub CLI for various development tasks. To authenticate:

**For detailed authentication options and troubleshooting, see [GitHub Authentication Quick Reference](github-auth-guide.md).**

#### Option A: Using the Setup Script (Recommended)

```bash
./scripts/setup_github_auth.sh
```

This interactive script will guide you through the authentication process.

#### Option B: Manual Authentication

```bash
gh auth login
```

Follow the prompts to:
1. Choose authentication method (web browser recommended)
2. Select GitHub.com
3. Authenticate via your web browser
4. Choose your preferred git protocol (HTTPS or SSH)

#### Verify Authentication

```bash
gh auth status
```

You should see confirmation that you're logged into GitHub.com.

#### Test Authentication

Run the test script to verify your authentication setup:

```bash
python3 scripts/test_github_auth.py
```

This will check for GitHub tokens and test API access.

### 3. Install Python Dependencies

#### For Job Discovery

```bash
pip install -r automation/job-discovery/scripts/requirements.txt
```

#### For Resume Tailoring

```bash
pip install -r automation/resume-tailoring/scripts/requirements.txt
```

#### For Outreach

```bash
pip install -r automation/outreach/scripts/requirements.txt
```

#### For Development/Testing

```bash
pip install -r dev-requirements.txt
```

### 4. Configure Environment

Copy the sample configuration and customize it:

```bash
cp config/env.sample.json config/env.json
```

Edit `config/env.json` and add your API keys:
- OpenAI API key (for AI-powered features)
- Indeed Publisher key (for job discovery)
- LinkedIn API key (if using LinkedIn integration)
- Other service credentials as needed

**Important:** Never commit `env.json` to version control. It's already in `.gitignore`.

### 5. Set Up Excel Templates (Optional)

If you plan to use Excel integration:

1. Review the schema: `excel-templates/system-of-record-schema.md`
2. Copy the template: `excel-templates/system-of-record-template.xlsx`
3. Customize for your needs

## GitHub CLI Usage

Once authenticated, you can use GitHub CLI for various tasks:

### Repository Management

```bash
# View repository information
gh repo view

# Clone a repository
gh repo clone <repository>
```

### Pull Requests

```bash
# List pull requests
gh pr list

# Create a pull request
gh pr create

# View a pull request
gh pr view <number>

# Check out a pull request
gh pr checkout <number>
```

### Issues

```bash
# List issues
gh issue list

# Create an issue
gh issue create

# View an issue
gh issue view <number>
```

### Workflow/Actions

```bash
# View workflow runs
gh run list

# View workflow details
gh run view <run-id>

# View workflow logs
gh run view <run-id> --log
```

## Using GitHub Tokens in Scripts

For automation scripts that need GitHub API access, you can use a personal access token:

### Create a Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "personal-os-automation")
4. Select appropriate scopes:
   - `repo` - Full control of private repositories (if needed)
   - `read:org` - Read org and team membership (if needed)
   - `workflow` - Update GitHub Action workflows (if needed)
5. Generate and copy the token

### Configure Token in Environment

Add to your `config/env.json` or set as environment variable:

```bash
export GITHUB_TOKEN="your_token_here"
```

Or add to your shell profile (~/.bashrc, ~/.zshrc, etc.):

```bash
echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

## Testing Your Setup

### Run the Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/job_discovery_tests.py -v

# Run with coverage
pytest --cov=automation tests/
```

### Run a Sample Automation

```bash
# Example: Run job discovery
python automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output
```

## Troubleshooting

### GitHub CLI Authentication Issues

**Problem:** `gh auth status` shows not authenticated

**Solution:** Run `gh auth login` again and complete the authentication flow.

**Problem:** Token expired

**Solution:** Run `gh auth refresh -h github.com`

### Python Import Errors

**Problem:** `ModuleNotFoundError` when running scripts

**Solution:** Ensure you've installed the required dependencies:
```bash
pip install -r dev-requirements.txt
pip install -r automation/job-discovery/scripts/requirements.txt
```

### Permission Denied on Scripts

**Problem:** Cannot execute setup script

**Solution:** Make it executable:
```bash
chmod +x scripts/setup_github_auth.sh
```

### API Rate Limits

**Problem:** GitHub API rate limit exceeded

**Solution:** 
- Authenticate with GitHub CLI to get higher rate limits
- Use a personal access token for API calls
- Wait for the rate limit to reset (check with `gh api rate_limit`)

## Next Steps

After setup, you can:

1. Review the [master brief](master-brief.md) to understand objectives
2. Check the [operating constraints](operating-constraints.md)
3. Review the [governance model](governance-model.md)
4. Start using automation scripts for your 60-day plan

## Additional Resources

- [GitHub Authentication Quick Reference](github-auth-guide.md) - Comprehensive guide for `gh auth login`
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub CLI Authentication](https://cli.github.com/manual/gh_auth_login)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

## Security Best Practices

- Never commit API keys, tokens, or credentials to version control
- Use environment variables or config files (that are gitignored) for sensitive data
- Rotate tokens periodically
- Use tokens with minimal required scopes
- Store tokens securely (e.g., password manager)
- Review `.gitignore` to ensure sensitive files are excluded

## Support

For questions or issues:
1. Check this guide and other documentation in `docs/`
2. Review specification files in each module
3. Check configuration examples
4. Create an issue in the repository
