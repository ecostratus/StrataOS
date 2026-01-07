# Job Scraper Specification

## Purpose

Automate the discovery and collection of job postings from multiple sources based on defined criteria.

## Objectives

- Aggregate job postings from multiple sources
- Filter based on role, location, and other criteria
- Extract key information for scoring and tracking
- Store results in standardized format for Excel import

## Data Sources

### Supported Sources
- Job boards (LinkedIn, Indeed, etc.)
- Company career pages
- Recruiter feeds
- API-based sources

### Data Collection Method
- Respect robots.txt and rate limits
- Use appropriate delays between requests
- Handle errors gracefully
- Log all scraping activities

## Output Format

### Required Fields
- Job Title
- Company Name
- Location
- Job Description (summary)
- URL to full posting
- Date Posted
- Source
- Scraped Date/Time

### Output File
- CSV format for Excel import
- UTF-8 encoding
- Timestamp in filename
- Stored in designated output folder

## Filtering Criteria

### Configurable Filters
- Keywords (include/exclude)
- Location (include/exclude)
- Company size
- Industry
- Job level (entry, mid, senior)
- Remote/hybrid/onsite
- Date posted (last N days)

## Error Handling

### Expected Errors
- Network timeouts
- Rate limiting
- Changed page structure
- Invalid data

### Error Response
- Log error with details
- Continue with remaining sources
- Report summary of errors
- Alert if critical failure

## Performance

### Targets
- Process 100+ postings per run
- Complete within 5 minutes
- Minimal resource usage
- Background execution

## Configuration

### Config File Location
`config/job_discovery_config.json`

### Required Settings
- Source URLs
- Filter criteria
- Output path
- Rate limit settings
- Error notification settings
