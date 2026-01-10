# Field Mapping Reference

Canonical job fields:
- title
- location
- company
- source
- url
- posted_at (YYYY-MM-DD)

## LinkedIn → Canonical
- `title` → `title`
- `location` → `location`
- `company` → `company`
- `url` → `url`
- `posted_date`/`posted_at` → `posted_at` (normalized to YYYY-MM-DD)
- `source` → constant `linkedin`

## Indeed → Canonical
- `title` → `title`
- `location` → `location`
- `company` → `company`
- `url` → `url`
- `posted_date`/`datePublished`/`publishedAt` → `posted_at` (normalized to YYYY-MM-DD)
- `source` → constant `indeed`

## Lever → Canonical
- `text`/`title` → `title`
- `categories.location`/`location` → `location`
- `company` → `company`
- `hostedUrl`/`url` → `url`
- `createdAt`/`publishedAt` → `posted_at` (normalized to YYYY-MM-DD)
- `source` → constant `lever`

## Greenhouse → Canonical
- `title` → `title`
- `location.name`/`location` → `location`
- `company` → `company`
- `absolute_url`/`url` → `url`
- `updated_at`/`created_at` → `posted_at` (normalized to YYYY-MM-DD)
- `source` → constant `greenhouse`

## Ashby → Canonical
- `title` → `title`
- `companyName`/`company` → `company`
- `location` → `location`
- `jobUrl`/`url` → `url`
- `publishedAt`/`createdAt` → `posted_at` (normalized to YYYY-MM-DD)
- `source` → constant `ashby`

## ZipRecruiter → Canonical
- `title` → `title`
- `company` → `company`
- `location` → `location`
- `url` → `url`
- `datePosted`/`publishedAt` → `posted_at` (normalized to YYYY-MM-DD)
- `source` → constant `ziprecruiter`

## Google Jobs → Canonical
- `title` → `title`
- `company` → `company`
- `location` → `location`
- `url` → `url`
- `datePublished`/`publishedAt` → `posted_at` (normalized to YYYY-MM-DD)
- `source` → constant `googlejobs`

## Glassdoor → Canonical
- `title` → `title`
- `company` → `company`
- `location` → `location`
- `url` → `url`
- `datePosted`/`publishedAt` → `posted_at` (normalized to YYYY-MM-DD)
- `source` → constant `glassdoor`

## Craigslist → Canonical
- `title` → `title`
- `company` → `company`
- `location` → `location`
- `url` → `url`
- `datePosted`/`publishedAt` → `posted_at` (normalized to YYYY-MM-DD)
- `source` → constant `craigslist`

## GoRemote → Canonical
- `title` → `title`
- `company` → `company`
- `location` → `location`
- `url` → `url`
- `datePublished`/`publishedAt` → `posted_at` (normalized to YYYY-MM-DD)
- `source` → constant `goremote`
