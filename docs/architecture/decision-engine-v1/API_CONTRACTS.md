# API Contracts (v1)

This file defines implementation-facing API boundaries for the decision engine.

## Evaluate Opportunity

- Method: `POST`
- Path: `/api/decision/evaluate`

Request body:

- `person_id: string`
- `opportunity_id: string`
- `policy_id: string`
- `person_claims: Claim[]`
- `opportunity_claims: Claim[]`

Response body:

- `decision: Decision`
- `recommendation: Recommendation`

## Validate Policy

- Method: `POST`
- Path: `/api/decision/validate-policy`

Request body:

- `policy: Policy`

Response body:

- `valid: boolean`
- `errors: string[]`

## Validate Claims

- Method: `POST`
- Path: `/api/decision/validate-claims`

Request body:

- `claims: Claim[]`

Response body:

- `valid: boolean`
- `errors: string[]`
