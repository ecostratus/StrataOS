# System of Record Schema

## Overview

This document defines the schema for the Excel-based System of Record that serves as the central database for the 60-day personal operating system.

## File Structure

The System of Record workbook contains multiple sheets for different data types:

1. **Jobs** - Job opportunities tracker
2. **Applications** - Application status tracker
3. **Outreach** - Networking and outreach log
4. **Consulting** - Consulting pipeline tracker
5. **Interviews** - Interview schedule and notes
6. **Contacts** - Professional contacts database
7. **Weekly_Goals** - Weekly goal tracking
8. **Audit_Log** - System activity audit trail
9. **Dashboard** - Summary metrics and charts

## Sheet Schemas

### 1. Jobs Sheet

**Purpose**: Track discovered job opportunities and their evaluation

| Column Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| job_id | Text | Yes | Unique identifier (auto-generated) |
| date_found | Date | Yes | When job was discovered |
| company_name | Text | Yes | Company name |
| job_title | Text | Yes | Position title |
| location | Text | No | Job location |
| remote_policy | Text | No | Remote/Hybrid/Onsite |
| job_url | Text | Yes | Link to job posting |
| description_summary | Long Text | No | Brief description |
| source | Text | Yes | Where job was found |
| score_overall | Number | No | Overall score (0-10) |
| score_role_fit | Number | No | Role fit score (0-10) |
| score_company_fit | Number | No | Company fit score (0-10) |
| score_compensation | Number | No | Compensation score (0-10) |
| score_location | Number | No | Location score (0-10) |
| score_growth | Number | No | Growth opportunity score (0-10) |
| priority | Text | No | Exceptional/Strong/Moderate/Weak/Poor |
| status | Text | Yes | Discovered/Reviewing/Applied/Rejected/Closed |
| resume_tailored | Boolean | No | Has resume been tailored? |
| resume_path | Text | No | Path to tailored resume |
| notes | Long Text | No | Additional notes |
| last_updated | DateTime | Yes | Last modification timestamp |

### 2. Applications Sheet

**Purpose**: Track application submissions and their outcomes

| Column Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| application_id | Text | Yes | Unique identifier |
| job_id | Text | Yes | Reference to Jobs sheet |
| date_applied | Date | Yes | Application submission date |
| company_name | Text | Yes | Company name |
| job_title | Text | Yes | Position title |
| application_method | Text | Yes | Direct/Recruiter/Referral/Other |
| referral_source | Text | No | If referred, by whom |
| resume_version | Text | No | Which resume was used |
| cover_letter | Boolean | No | Was cover letter included? |
| status | Text | Yes | Submitted/Under Review/Interview/Rejected/Offer/Accepted/Declined |
| date_status_updated | Date | Yes | When status last changed |
| response_time_days | Number | No | Days to first response |
| rejection_reason | Text | No | If known |
| notes | Long Text | No | Additional notes |
| last_updated | DateTime | Yes | Last modification timestamp |

### 3. Outreach Sheet

**Purpose**: Log networking and outreach activities

| Column Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| outreach_id | Text | Yes | Unique identifier |
| date_sent | Date | Yes | When message was sent |
| recipient_name | Text | Yes | Contact name |
| recipient_company | Text | No | Their company |
| recipient_role | Text | No | Their job title |
| platform | Text | Yes | LinkedIn/Email/Other |
| message_type | Text | Yes | Cold/Networking/FollowUp/Referral |
| related_job_id | Text | No | If related to specific job |
| subject | Text | No | Message subject/title |
| response_received | Boolean | No | Did they respond? |
| response_date | Date | No | When they responded |
| response_type | Text | No | Positive/Neutral/Negative |
| meeting_scheduled | Boolean | No | Was meeting scheduled? |
| meeting_date | Date | No | Meeting date if scheduled |
| outcome | Text | No | Outcome description |
| notes | Long Text | No | Additional notes |
| last_updated | DateTime | Yes | Last modification timestamp |

### 4. Consulting Sheet

**Purpose**: Track consulting opportunities and proposals

| Column Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| opportunity_id | Text | Yes | Unique identifier |
| date_created | Date | Yes | When opportunity identified |
| client_name | Text | Yes | Client/company name |
| client_industry | Text | No | Industry |
| client_size | Text | No | Small/Medium/Large/Enterprise |
| engagement_type | Text | Yes | Discovery/Implementation/Retainer/Training |
| description | Long Text | Yes | Opportunity description |
| estimated_value | Number | No | Estimated revenue |
| status | Text | Yes | Lead/Qualified/Proposal/Negotiation/Won/Lost |
| proposal_sent_date | Date | No | When proposal was sent |
| proposal_path | Text | No | Path to proposal document |
| decision_date | Date | No | Expected or actual decision date |
| win_probability | Number | No | Percentage (0-100) |
| actual_value | Number | No | If won, actual contract value |
| start_date | Date | No | If won, start date |
| lost_reason | Text | No | If lost, why |
| notes | Long Text | No | Additional notes |
| last_updated | DateTime | Yes | Last modification timestamp |

### 5. Interviews Sheet

**Purpose**: Schedule and track interview activities

| Column Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| interview_id | Text | Yes | Unique identifier |
| application_id | Text | Yes | Reference to Applications sheet |
| company_name | Text | Yes | Company name |
| job_title | Text | Yes | Position title |
| interview_date | DateTime | Yes | Scheduled date and time |
| interview_type | Text | Yes | Phone/Video/Onsite/Technical/Behavioral/Final |
| interviewer_names | Text | No | Who will interview |
| duration_minutes | Number | No | Expected duration |
| preparation_completed | Boolean | No | Is prep done? |
| preparation_notes_path | Text | No | Path to prep materials |
| interview_completed | Boolean | No | Has interview occurred? |
| outcome | Text | No | Positive/Neutral/Negative |
| feedback_received | Boolean | No | Got feedback? |
| feedback | Long Text | No | Feedback notes |
| next_steps | Text | No | What happens next |
| notes | Long Text | No | Additional notes |
| last_updated | DateTime | Yes | Last modification timestamp |

### 6. Contacts Sheet

**Purpose**: Maintain professional contacts database

| Column Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| contact_id | Text | Yes | Unique identifier |
| first_name | Text | Yes | Contact first name |
| last_name | Text | Yes | Contact last name |
| company | Text | No | Current company |
| title | Text | No | Job title |
| industry | Text | No | Industry |
| email | Text | No | Email address |
| linkedin_url | Text | No | LinkedIn profile |
| phone | Text | No | Phone number |
| relationship | Text | No | Strong/Medium/Weak |
| how_met | Text | No | How you connected |
| tags | Text | No | Comma-separated tags |
| last_contact_date | Date | No | Last interaction |
| notes | Long Text | No | Additional notes |
| last_updated | DateTime | Yes | Last modification timestamp |

### 7. Weekly_Goals Sheet

**Purpose**: Track weekly goals and achievement

| Column Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| week_of | Date | Yes | Week start date |
| applications_target | Number | Yes | Target applications |
| applications_actual | Number | No | Actual applications |
| outreach_target | Number | Yes | Target outreach |
| outreach_actual | Number | No | Actual outreach |
| networking_target | Number | Yes | Target networking events |
| networking_actual | Number | No | Actual networking |
| other_goals | Long Text | No | Other goals |
| achievement_rate | Number | No | Percentage (0-100) |
| notes | Long Text | No | Weekly notes |
| last_updated | DateTime | Yes | Last modification timestamp |

### 8. Audit_Log Sheet

**Purpose**: Log all system activities for governance

| Column Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| log_id | Text | Yes | Unique identifier |
| timestamp | DateTime | Yes | When action occurred |
| action_type | Text | Yes | Type of action |
| component | Text | Yes | Script/Flow/Manual |
| description | Long Text | Yes | Action description |
| user_decision | Boolean | No | Was human decision involved? |
| automated | Boolean | No | Was action automated? |
| success | Boolean | Yes | Did action succeed? |
| error_message | Text | No | If failed, error details |
| related_record_id | Text | No | Reference to affected record |
| notes | Long Text | No | Additional context |

### 9. Dashboard Sheet

**Purpose**: Display summary metrics and visualizations

This sheet contains formulas, pivot tables, and charts that pull data from other sheets to display:
- Key performance indicators
- Trend charts
- Funnel metrics
- Goal achievement tracking
- Weekly/monthly summaries

## Data Types

- **Text**: Short text (255 characters max)
- **Long Text**: Extended text (no limit)
- **Number**: Numeric value
- **Date**: Date only (MM/DD/YYYY)
- **DateTime**: Date and time (MM/DD/YYYY HH:MM)
- **Boolean**: Yes/No or True/False

## Naming Conventions

- Use snake_case for column names
- Use PascalCase for sheet names
- IDs use format: `[type]_[timestamp]_[random]`
- Dates in ISO format: YYYY-MM-DD

## Data Validation Rules

1. **Required fields** must have data before saving
2. **IDs** must be unique within their sheet
3. **Dates** must be valid dates
4. **Status fields** must use predefined values
5. **Foreign keys** (e.g., job_id references) should exist in referenced sheet
6. **Scores** must be between 0-10
7. **Percentages** must be between 0-100

## Formulas and Automation

### Calculated Fields
- `response_time_days` = `date_status_updated` - `date_applied`
- `achievement_rate` = (`actual` / `target`) × 100
- Scores are calculated by automation scripts

### Conditional Formatting
- Priority levels color-coded
- Overdue items highlighted
- Status indicators with colors
- Score heat maps

## Data Maintenance

### Daily
- Update status fields as changes occur
- Log all activities in Audit_Log
- Check for data quality issues

### Weekly
- Review and clean data
- Archive old records if needed
- Validate referential integrity
- Update Dashboard calculations

### Monthly
- Comprehensive data audit
- Archive completed records
- Optimize workbook performance
- Backup data

## Privacy and Security

- **No passwords** in spreadsheet
- **No API keys** in spreadsheet
- Use external config for sensitive data
- Regular backups to secure location
- Access controlled to user only

## Integration Points

This Excel file integrates with:
- Python automation scripts (read/write via openpyxl)
- Copilot Studio flows (via Excel connector)
- Power BI (optional for advanced analytics)
- Export to CSV for backup

## Versioning

- Save new version weekly: `system-of-record-YYYYMMDD.xlsx`
- Keep last 8 weeks of versions
- Document major schema changes
