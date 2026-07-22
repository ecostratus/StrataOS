# Human Validation Review

## Fixture Information

Fixture: `principal-servicenow-role`
Person: James Naphen (Principal platform architect, 15yrs, ServiceNow)
Opportunity: Principal ServiceNow Architect at Acme Systems (Remote)
Date: 2026-01-21

---

## Engine Output

**Expected Recommendation**: APPLY_IMMEDIATELY  
**Confidence Score**: 1.0 (maximum)  
**Decision Logic**: 
- Remote alignment (+0.30) ✓
- Seniority alignment (+0.30) ✓
- Skill match (+0.40) ✓
- **Total: 1.0 → APPLY_IMMEDIATELY**

---

## Human Assessment: Is This Advice Sound?

### Question 1: Would you recommend James apply?

**Answer**: **PROBABLY, but not with full confidence**

**Reasoning**:

✅ **Strengths of the match:**
- Hard skill alignment is genuine (ServiceNow expertise clearly matches stated requirement)
- Seniority level is appropriate (Principal person, Principal role)
- Remote constraint is satisfied
- Job title signals growth/lateral move (matches stated goal)

⚠️ **Critical missing information that would influence recommendation:**
1. **Company quality/trajectory** 
   - Unknown: Is Acme Systems stable, growing, or declining?
   - Unknown: Are they investing in platform engineering or cutting costs?
   - Impact: This job could be a 3-year journey or a 6-month exit. The advice changes.

2. **Compensation context**
   - Unknown: James's current comp / market comp / Acme's comp
   - Unknown: Is this a step up financially, lateral, or step down?
   - Impact: If step down, it's wrong advice despite skills matching.

3. **Role scope ambiguity**
   - Unknown: What does "Principal ServiceNow Architect" actually own at Acme?
   - Unknown: Is this individual contributor or team leadership?
   - Impact: "Principal" can mean very different things. James might need to dig.

4. **Why is remote in the constraints?**
   - Observation: James specified remote-only (✓ match)
   - Unknown: Is he avoiding a location, or does he have distributed preferences?
   - Unknown: Is Acme's remote truly distributed, or "remote-first at HQ"?
   - Impact: Might be wrong for unstated reasons.

### Question 2: Is the engine's confidence justified?

**Answer**: **No. Score of 1.0 is overconfident.**

**Why**:
- The engine observed: 3 positive signals, 0 negative signals
- The engine inferred: perfect fit → maximum recommendation
- The reality: observed data is incomplete; missing signals don't equal positive signals
- A human would say: "Skills match well, location works, level seems right. But I need to know more about the company and comp before I'd tell someone to apply immediately."

**Confidence calibration issue**:
```
Engine: "All signals I checked are green" → 1.0
Human: "All signals I checked are green, but I didn't check enough" → 0.7
```

### Question 3: What would change the recommendation?

**Factors that could flip to HOLD or CAUTION:**
1. Acme is in major downsizing (→ HOLD)
2. Compensation is 30% below market (→ HOLD)
3. Role is pure individual contributor (James wants people leadership) (→ CAUTION)
4. "Remote" means "remote but must be in US Pacific timezone" (→ DEPENDS on James's timezone)
5. Company is early-stage, pre-Series-B (→ CAUTION, depends on James's risk appetite)

---

## Validation Verdict

| Dimension | Assessment | Confidence |
|-----------|------------|------------|
| **Skill match is real** | ✅ YES | 100% |
| **Seniority level is appropriate** | ✅ YES | 95% |
| **Remote constraint satisfied** | ✅ YES | 100% |
| **This is actionable advice as-is** | ⚠️ PROBABLY | 60% |
| **Engine confidence level justified** | ❌ NO | 0% |

---

## v1.1 Confidence Semantics: How the Engine Now Addresses This Gap

As of 2026-01-24, the decision engine now implements three-dimensional confidence semantics that directly resolve the validator's concern about overconfidence.

### v1.0 Model (Original)
```
Observation: 3 positive signals, 0 negative signals
Inference: 1.0 confidence
Interpretation: "All checked criteria match"
Human reality: "All checked criteria match, but insufficient data"
Gap: Conflates "perfect match" with "good decision"
```

### v1.1 Model (Updated)
```
Three dimensions now tracked separately:

1. ALIGNMENT: 1.0
   Interpretation: "High match with stated criteria"
   Details: All 3 observed factors align perfectly
   
2. COMPLETENESS: 0.43 (3 of 7 required factors known)
   Known: required_skill, role_level, work_mode
   Unknown: compensation_level, company_trajectory, 
            team_maturity, reporting_structure
   
3. EVIDENCE QUALITY: 1.0 (HIGH)
   All observations come from reliable sources
   
4. DECISION CONFIDENCE: 0.45 (MEDIUM)
   Conservative interpretation: "strong alignment with stated 
   criteria, but incomplete information (42% of decision factors known)"
   Rationale: Confidence reduced by incompleteness, not alignment
   Components stored separately for future calibration
```

### How This Addresses the Validation Gap

**Before v1.1:**
- Validator: "Engine says 1.0, I'd say 0.6"
- Engine claim: "Perfect match"
- Reality: Incomplete information treated as absence of negative signals

**After v1.1:**
- Validator: "Engine says alignment 1.0 + completeness 0.43 → confidence 0.45 MEDIUM"
- Engine claim: "Perfect alignment on observed factors, but missing 57% of decision factors"
- Reality: Unknown factors explicitly tracked as reasoning objects

**Validation outcome:**
```
Validator's 0.6 ≈ Engine's 0.45 MEDIUM?
Not exact alignment, but now in the same ballpark.
More importantly: gap is now explained, not invisible.
```

### Unknowns Extracted as First-Class Reasoning Objects

The engine now identifies and tracks:

| Unknown | Impact | Decision Effect | Resolution Strategy |
|---------|--------|-----------------|---------------------|
| **company_trajectory** | HIGH | May affect stability and growth | Research company trajectory |
| **compensation_level** | HIGH | May affect financial viability | Research compensation level |
| **reporting_structure** | MEDIUM | May affect scope clarity | Research reporting structure |
| **team_maturity** | MEDIUM | May affect execution risk | Research team maturity |

This matches the validator's "Critical missing information" list from the human assessment.

### v1.0 vs v1.1 Comparison

| Aspect | v1.0 | v1.1 |
|--------|------|------|
| **Recommendation** | APPLY_IMMEDIATELY | APPLY_IMMEDIATELY ✓ |
| **Confidence score** | 1.0 | 0.45 |
| **Confidence interpretation** | Perfect match | Medium (aligned but incomplete) |
| **Alignment visible** | ❌ Hidden in score | ✅ Explicit (1.0) |
| **Completeness visible** | ❌ Not tracked | ✅ Explicit (0.43) |
| **Unknowns visible** | ❌ Treated as absences | ✅ Explicit list (4 items) |
| **Decision changes?** | N/A | ❌ NO (same recommendation) |
| **Judgment improves?** | N/A | ✅ YES (honest about limits) |

---

## Judgment Quality Assessment

### v1.0 Engine Assessment

**What the engine did well:**
- Deterministic interpretation of observable facts
- Correct mapping of constraints to job attributes
- Appropriate weighting of skill match
- Fully traceable reasoning chain

**What the engine missed (v1.0):**
- The difference between "matches stated criteria" and "good career move"
- Unknown signals were treated as absence of negative signals, not as uncertainty
- Missing data did not reduce confidence (fundamental confidence semantics gap)
- No explicit tracking of decision factors vs. observed factors

### v1.1 Engine Assessment

**What v1.1 now addresses:**
- ✅ Unknown signals now explicitly reduce completeness score
- ✅ Confidence is now separated into alignment, completeness, and evidence quality
- ✅ Unknowns are tracked as first-class reasoning objects with impact assessment
- ✅ Decision confidence is now conservative (0.45 MEDIUM) rather than maximum (1.0)
- ✅ Validator gap is now narrower (human said 0.6, engine now says 0.45 MEDIUM)

**What v1.1 still doesn't address:**
- Cross-contextual reasoning (Why does James need remote? What's his actual goal?)
- Implicit tradeoffs (Would James trade comp for growth? Stability for learning?)
- External signals (Company health, market conditions, career trajectory implications)
- These require human judgment and are out of scope for v1.1

---

## Recommendation for StrataOS

### This fixture is suitable for:
- ✅ **Testing determinism** (does engine produce consistent output?)
- ✅ **Testing schema compliance** (do outputs match expected structure?)
- ✅ **Testing traceability** (can we trace recommendation back to observations?)

### This fixture is NOT suitable for:
- ❌ **Proving the engine makes perfect decisions** (unknowns still exist; completion is human's job)
- ❌ **Validating implicit tradeoffs** (e.g., growth vs. stability, comp vs. learning)

### This fixture NOW demonstrates (v1.1):
- ✅ **Honest confidence calibration** (alignment is high, confidence is medium due to incompleteness)
- ✅ **Decision-support reasoning** (shows what's known, what's unknown, what would change the recommendation)
- ✅ **Judgment improvement** (same recommendation with realistic confidence)

### Next steps:
1. Create two additional fixtures as suggested:
   - **High Fit / Low Upside** (matches hard criteria but lower career value)
   - **Medium Fit / High Trajectory** (non-obvious match but strategic opportunity)

2. For each: perform similar human validation review

3. Use disagreement patterns to identify systematic gaps in the engine's reasoning

---

## Reviewer Sign-off

**Review History:**
- 2026-01-21: Initial validation (v1.0 model) - Overconfidence detected
- 2026-01-24: v1.1 Confidence Semantics Preview implemented and validated

**Assessment:**
- v1.0: Engine determinism proven. Decision quality concern identified (confidence vs. completeness conflation).
- v1.1: Confidence semantics corrected. Same recommendation, honest uncertainty representation. Validator gap narrowed.

**Validation Status:** Decision Model v1.1 Confidence Semantics Preview
- ✅ Recommendation preserved (APPLY_IMMEDIATELY)
- ✅ Confidence bounds improved (1.0 → 0.45 MEDIUM, closer to validator's 0.6)
- ✅ Unknowns explicitly tracked (4 decision factors identified as missing)
- ✅ Contract tests passing (all 6 tests including migration test)

**Next gate:** Once additional fixtures are validated and patterns stabilize, advance to "Judgment Calibration v1.1 Certified" status.
