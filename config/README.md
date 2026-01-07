# Configuration Directory

## Overview

This directory contains configuration files and settings for the personal operating system.

## Files

### env.sample.json
Template for environment-specific configuration. Copy to `env.json` and customize.
**DO NOT commit `env.json`** - it contains sensitive data.

### endpoints.md
Documentation of API endpoints and service URLs used by the system.

## Setup Instructions

1. **Create your config file**:
   ```bash
   cp env.sample.json env.json
   ```

2. **Fill in your values**:
   - API keys
   - Service URLs
   - Personal preferences
   - File paths

3. **Protect sensitive data**:
   - Never commit `env.json` to git
   - Use environment variables for production
   - Rotate keys regularly
   - Follow least-privilege principle

## Configuration Management

### Local Development
- Use `env.json` for local configuration
- Keep template (`env.sample.json`) updated
- Document all configuration options

### Production/Automation
- Use environment variables
- Store secrets in Azure Key Vault or similar
- Never hardcode credentials in scripts

## Security Best Practices

1. **Never commit secrets**:
   - Add `env.json` to `.gitignore`
   - Review commits before pushing
   - Use git-secrets or similar tools

2. **Rotate credentials**:
   - Change API keys quarterly
   - Update after any potential exposure
   - Document rotation procedures

3. **Principle of least privilege**:
   - Use read-only keys where possible
   - Limit API scopes
   - Separate dev and prod credentials

4. **Encryption**:
   - Encrypt sensitive config files
   - Use secure credential storage
   - Protect file permissions (chmod 600)

## Configuration Options

See `env.sample.json` for all available configuration options with descriptions.

## Troubleshooting

### Config file not found
- Check file path in scripts
- Ensure `env.json` exists
- Verify file permissions

### Invalid configuration
- Validate JSON syntax
- Check for required fields
- Verify data types

### API authentication errors
- Verify API keys are current
- Check key scopes and permissions
- Test keys independently

## Support

For questions about configuration, refer to:
- `endpoints.md` for API documentation
- Individual script documentation
- Security best practices guide
