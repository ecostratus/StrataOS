You are assisting with Phase 3D: Extended Sources + Transform Expansion.

Your tasks:
1. Add new enrichment transforms (skills, domain tags, seniority heuristics, stack inference).
2. Use shared normalization helpers (ensure_str, normalize_terms).
3. Ensure deterministic ordering of all outputs.
4. Keep transforms pure, type-safe, and side-effect-free.
5. Add unit tests for:
   - mixed case
   - whitespace
   - punctuation
   - duplicates
   - deterministic ordering
6. Do not modify scoring thresholds or orchestrator logic.
7. All existing tests must remain green.
8. Add config-driven behavior for new transforms.
