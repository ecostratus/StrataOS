# Fixtures

Fixtures for job discovery mapping tests.

- linkedin_payload.json: Sample LinkedIn response shape.
- indeed_payload.json: Sample Indeed response shape.
- malformed_payload.json: Entries with missing fields.

Decision-model contract fixture:

- v1/principal-servicenow-role/person.json
- v1/principal-servicenow-role/opportunity.json
- v1/principal-servicenow-role/observations.json
- v1/principal-servicenow-role/policy.json
- v1/principal-servicenow-role/expected_evidence.json
- v1/principal-servicenow-role/expected_claims.json
- v1/principal-servicenow-role/expected_decision.json
- v1/principal-servicenow-role/expected_recommendation.json
- v1/principal-servicenow-role/expected_trace_artifact.json

Fixture governance:

- `v1` fixtures are frozen unless a deliberate baseline revision is approved.
- New baseline behavior should be added under a new version directory.
