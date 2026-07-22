# Dependency Security Baseline

**Status:** Clean  
**Established:** 2026-07-21  
**Last Updated:** 2026-07-21  

---

## Runtime Versions

| Component | Version |
|-----------|---------|
| Python | 3.11.7 |
| Node.js | system default |
| pip | 26.1.2 |

---

## Lock Strategy

- **Backend:** `pip freeze` captured in venv, `requirements.txt` pins minimum versions (`>=`).  
  Pinned minimum bounds prevent re-introduction of known-bad ranges.
- **Frontend:** `package-lock.json` committed. Exact resolved versions locked in lockfile.  
  `package.json` uses `^` ranges; lockfile enforces actual installed versions.

Upgrades are applied as standalone `security:` commits — separate from feature and refactor work.

---

## Vulnerability Scan Results

### Backend — `pip-audit` (2026-07-21)

| Package | Was | Fixed To | Severity | GHSA | Notes |
|---------|-----|----------|----------|------|-------|
| pip | 23.2.1 | 26.1.2 | Moderate/High | GHSA-mq26-g339-26xf, GHSA-wf93-45jw-7689, GHSA-4xh5-x5gv-qwph, GHSA-6vgw-5pg2-w6jp, GHSA-58qw-9mgm-455v, GHSA-jp4c-xjxw-mgf9 | 6 advisories — all resolved by upgrade to 26.1.2 |
| setuptools | 65.5.0 | 83.0.0 | High | GHSA-r9hx-vwmv-q579 (CVE-2022-40897) | DoS via regex in `package_index` |

**Post-remediation:** `No known vulnerabilities found`

### Frontend — `npm audit` (2026-07-21)

| Package | Was | Fixed To | Severity | GHSA | Notes |
|---------|-----|----------|----------|------|-------|
| esbuild | 0.21.5 (via vite 5) | 0.25.x (via vite 7) | Moderate | GHSA-67mh-4wv8-2f99 | Dev server CORS bypass — dev-only exposure |
| vite | 5.4.21 | 7.3.6 | High (transitive) | GHSA-4w7w-66w2-5vf9, GHSA-v6wh-96g9-6wx3 | Path traversal in optimized deps; NTLMv2 on Windows |

Upgrade path: `vite` 5.4.21 → 7.3.6, `@vitejs/plugin-react` 4.x → 5.2.0.  
Production build verified clean post-upgrade.

**Post-remediation:** `found 0 vulnerabilities`

---

## Accepted Risks

None at baseline establishment. All flagged vulnerabilities remediated.

---

## GitHub Dependabot Alerts

GitHub flagged **4 vulnerabilities (1 high, 3 moderate)** on push prior to remediation.  
All resolved in commit `security: remediate dependency vulnerabilities`.

---

## Test Validation Post-Remediation

| Suite | Result |
|-------|--------|
| Decision model contract tests | 5 passed |
| Webapp API tests | passed |
| Full suite | 145 passed, 3 pre-existing failures (unrelated: job-discovery DummyConfig mock) |
| Frontend production build | ✓ clean (vite 7.3.6) |

Pre-existing failures (`test_main_filters_and_csv_export_deterministic`, `test_summary_artifact_created`, `test_logs_emitted_to_jsonl`) are tracked separately. Not introduced by this remediation.

---

## Governance Notes

This document is part of the StrataOS governance stack:

```
Architecture Governance  (docs/architecture/)
Decision Governance      (docs/architecture/decision-engine-v1/CERTIFICATION.md)
Security Governance      (docs/security/DEPENDENCY_BASELINE.md)  ← this file
```

Update this file whenever:
- A dependency is upgraded in response to a vulnerability
- A vulnerability is accepted as a known risk with rationale
- A new major runtime version is adopted
