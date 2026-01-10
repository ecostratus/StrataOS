# Field Mapping Reference

Canonical job fields:
- title
- location
- company
- source
- url
- posted_date (YYYY-MM-DD)

## LinkedIn → Canonical
- `title` → `title`
- `location` → `location`
- `company` → `company`
- `url` → `url`
- `posted_date` → `posted_date` (normalized to YYYY-MM-DD)
- `source` → constant `linkedin`

## Indeed → Canonical
- `title` → `title`
- `location` → `location`
- `company` → `company`
- `url` → `url`
- `posted_date` → `posted_date` (normalized to YYYY-MM-DD)
- `source` → constant `indeed`
