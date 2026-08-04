Adapter Design Contract

Intent
------
This document defines a stable, minimal contract between core platform workflows and external adapters that supply or transform job discovery data. The contract exists solely to guarantee predictable integration behavior and decision ownership; it contains no implementation details or technology-specific requirements.

Contract Boundaries
-------------------
- Scope: the contract covers input shapes, output shapes, operational guarantees, error signaling, and versioning semantics for adapters. It does not prescribe transport, language, or runtime.
- Boundary: adapters are external to core workflow logic. Core workflows shall treat adapters as black boxes which conform to this contract.

Inputs and Outputs
------------------
- Inputs: adapters receive an immutable, documented configuration object and an execution context containing `run_id`, `timestamp`, and `credentials_reference` (opaque token). The configuration shall include explicit flags for enabled behavior and rate limit parameters.
- Outputs: adapters produce two deterministic artifacts per execution:
  1. Raw output: an append-only line-delimited JSON (JSONL) stream of source-native records.
 2. Mapped output: a line-delimited JSON stream where each record adheres to the canonical SoR schema.
- All outputs shall include record-level metadata: `adapter_id`, `adapter_version`, `source_id`, `fetched_at`, and `run_id`.

Behavioral Guarantees
---------------------
- Determinism: given the same inputs and adapter version, the adapter shall produce the same mapped output ordering and content within the limits of source volatility.
- Idempotence: adapters shall not produce duplicate mapped records for the same source record when run with identical `run_id` and configuration; duplicate detection or stable record ids must be provided.
- Observability: adapters shall emit structured logs and metrics for fetch counts, retries, latency, and error classes.

Failure Modes and Degradation
----------------------------
- Fail-open policy: adapters may fail for a single source without aborting the entire workflow. The adapter must write a failure artifact with error classification and continue if configured to do so.
- Authentication failures: must surface a distinct error class and include remediation hints; these require AO action and escalation per SOP.
- Partial results: adapters returning partial data must mark records with a `partial=true` flag and include `partial_reason` in the artifact.

Versioning and Compatibility Rules
---------------------------------
- Semantic versioning: adapters shall use semantic versioning (MAJOR.MINOR.PATCH). MAJOR changes may break mapping or schema and require explicit change approvals and `ChangeLog` entries.
- Backwards compatibility: MINOR and PATCH releases must remain backward compatible for the contract interfaces. Core workflows shall bind to a specific adapter version in configuration; defaulting to `latest` is prohibited for production runs.

Ownership and Approval
----------------------
- Adapter Owner (AO): is accountable for adapter correctness, testing, CI, and the `ChangeLog` entry for each version.
- Platform Owner (PO): approves contract changes, integration test requirements, and production enablement for adapters.
- Approval: any contract modification requires written approval from PO and updates to the repository `docs/` area and `ChangeLog` prior to deployment.

Notes
-----
- The contract intentionally omits transport and runtime choices to allow adapter evolution without core refactors.
- Adapters must support automated testing hooks that allow CI to validate mapped outputs against canonical schema before deployment.
