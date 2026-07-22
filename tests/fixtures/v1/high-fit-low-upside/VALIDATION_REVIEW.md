# Adversarial Fixture Validation: High-Fit-Low-Upside

**Scenario**: Sarah Chen (Principal ServiceNow architect, remote-required) considering Principal role at declining company with below-market compensation and no growth path.

**Input Summary**:
- Person: Sarah Chen, Principal, 14 years ServiceNow
- Opportunity: Principal ServiceNow Architect, Horizon Tech Solutions (declining company)
- Observations: 3 factors known with perfect quality (skill, level, remote)
- Missing: compensation_level, company_trajectory, reporting_structure, team_maturity

## v1.0 Output (Algorithm Previous)

- Recommendation: `NETWORK_FIRST`
- Confidence: `1.0`
- Prediction Confidence: `1.0`
- Interpretation: "Perfect match on known criteria"

## v1.1 Output (Three-Dimensional Confidence)

- Recommendation: `NETWORK_FIRST` (unchanged)
- Alignment: `1.00` (all observed factors perfectly match criteria)
- Completeness: `0.43` (3 known / 7 required factors = 43%)
- Confidence Quality: `1.0` (HIGH quality sources: job posting, LinkedIn)
- Decision Confidence: `0.45` (MEDIUM)
- Rationale: "Strong alignment with observable criteria, but 57% of decision factors unknown"
- Unknowns:
  - compensation_level (impact: HIGH)
  - company_trajectory (impact: HIGH)
  - team_maturity (impact: MEDIUM)
  - reporting_structure (impact: MEDIUM)

## Human Validation Assessment

**Scenario Realism**: ✓ Realistic - common situation in job search (perfect fit on visible criteria, red flags on company health/compensation)

**Decision Quality Analysis**:
- Human expert assessment: "Probably not" (~0.4 confidence, "Nice role on paper but declining company = risk")
- v1.0 recommendation: "NETWORK_FIRST" (conservative, research mode)
- v1.1 confidence: 0.45 MEDIUM ✓ Aligned with human uncertainty
- Gap analysis: v1.0 conflated "observed alignment" with "confidence"; v1.1 separates them

**Pattern Insight**: 
When observations are perfect but incomplete, v1.1 correctly reduces confidence from 1.0 → 0.45. This addresses the **overconfidence pathology** identified in Phase 2 proof: "Don't conflate alignment with confidence."

**Why NETWORK_FIRST?**: The model sees:
- High alignment on skill/level/remote
- Missing company health/compensation/team signals
- Conservative pathway: research company before applying (NETWORK_FIRST)

**Critical Unknown**: Compensation below market (aligned with opportunity description) + company declining. If these factors were known, recommendation might shift to HOLD_AND_MONITOR or PASS. This suggests **v1.1 unknowns extraction is working correctly** — missing data that would materially affect the decision.

## Certification Implications

✓ **Confidence Calibration Advancing**: v1.0 said 1.0 (certain), human said ~0.4 (uncertain), v1.1 says 0.45 (honest). Confidence gap narrowed from 0.6 to ±0.05.

⏳ **Next Gate**: Validate this pattern holds across additional scenarios. If v1.1 consistently achieves 0.45-0.55 MEDIUM in mixed-quality scenarios, advance from "Confidence Semantics Preview" to "Judgment Calibration v1.1 Preview" (human + engine agreement stabilizing).

**Decision Confidence Interpretation**:
- Score 0.45, Level MEDIUM = "Mostly reasonable recommendation, but material uncertainties remain"
- Unknowns list should inform next data-gathering step (e.g., "research company health, confirm compensation range")

---

**Validation Status**: ✓ Pass — Pattern matches expected behavior. Confidence narrowed, unknowns extracted correctly, conservative recommendation aligns with incomplete data. Ready for second fixture validation.
