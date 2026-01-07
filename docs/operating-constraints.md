# Operating Constraints

## System Constraints

### Technical Constraints
- **Microsoft 365 Compatibility**: All Excel templates must work with Excel Online and Desktop
- **Copilot Studio Integration**: Flows must be compatible with Copilot Studio architecture
- **Python Version**: Scripts should use Python 3.8+ for maximum compatibility
- **Lightweight Scripts**: Keep script dependencies minimal and manageable

### Process Constraints
- **Manual Review Required**: All automated outputs require human review before action
- **Audit Trail**: Every action must be logged and traceable
- **Reversibility**: Changes must be reversible through documented rollback procedures
- **Privacy**: No sensitive data in public repositories or cloud services without encryption

## Operational Boundaries

### Time Constraints
- Daily review cycle: 30 minutes maximum
- Weekly review cycle: 2 hours maximum
- Automation execution: Background processes only

### Resource Constraints
- Budget: Track all paid service usage
- API Limits: Respect rate limits for all external services
- Storage: Keep local data organized and backed up

## Governance Constraints

### Decision Authority
- **Automated**: Routine data collection and formatting
- **Semi-Automated**: Suggested actions requiring approval
- **Manual Only**: Final decisions on applications, outreach, and commitments

### Compliance Requirements
- Follow all platform terms of service
- Respect data privacy regulations (GDPR, CCPA)
- Maintain professional standards in all communications

## Quality Constraints

### Output Standards
- All generated content must be reviewed for accuracy
- Resume tailoring must maintain truthfulness
- Outreach messages must be personalized and authentic
- Consulting proposals must be realistic and deliverable

## Change Management

### Modification Approval
- Documentation changes: Self-approved with changelog
- Script changes: Test before deployment
- Process changes: Document rationale and impact
- Flow changes: Version control and rollback plan
