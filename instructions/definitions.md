# Definitions

## Role Tags
Normalized role keywords (for example, `engineer`, `developer`) extracted from job content.

## Bucket
Human-readable score class:
- Weak
- Moderate
- Strong
- Exceptional

## Low Relevance
Jobs that fail default relevance gates (for example empty role tags or below minimum bucket threshold).

## Query-Layer Filtering
Filtering applied when reading jobs from storage/API, without changing core enrichment or scoring computation.

## Discovery Run
A full ingestion execution that fetches, filters, enriches, scores, and stores job artifacts.
