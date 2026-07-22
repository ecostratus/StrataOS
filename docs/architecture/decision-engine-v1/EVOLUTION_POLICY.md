# Evolution Policy

This policy defines extension, modification, and removal rules for core objects.

| Object | Can be Extended | Can be Modified | Can be Removed |
| --- | --- | --- | --- |
| Person | Yes | Yes | No (without migration) |
| Opportunity | Yes | Yes | No |
| Observation | Yes | No | No |
| Evidence | Yes | No | No |
| Claim | Yes | Yes (versioned) | No |
| Policy | Yes | Yes | Yes |
| Decision | No | No (immutable record) | No |

## Additional Rules

- Claim updates require version increment and change reason.
- Decision records are append-only.
- Schema changes must be backward-compatible within a major version.
- Breaking changes require explicit migration ADR.
