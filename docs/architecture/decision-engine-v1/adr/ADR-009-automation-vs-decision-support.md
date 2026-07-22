# ADR-009: Automation Engine vs. Decision-Support System

**Status**: Accepted  
**Date**: 2026-07-21  
**Deciders**: Human validation review of principal-servicenow-role fixture  
**Consultation**: Confidence semantics refinement session  

---

## Context

StrataOS decision engine currently produces outputs structured like an **automation engine**:

```
recommendation: APPLY_IMMEDIATELY
confidence: 1.0
```

This implies: "The system is confident it has determined the right answer."

A human reviewing the same opportunity disagrees (60% confidence vs. 100% engine confidence), revealing a fundamental architectural mismatch.

---

## Problem

### What an Automation Engine Claims
```
"I know the right answer."

Input: [facts]
Processing: [algorithm]
Output: [answer]
```

Implicit contract: If you follow my recommendation, it will be correct.

### What Automation Engine Actually Achieved
```
"I know the facts match these criteria."

Input: [facts]
Processing: [matching algorithm]
Output: [matching score]
```

Actual contract: These criteria are met.

### The Gap
An automation engine claiming 100% confidence when it has:
- ✅ Verified: Technical skills match
- ✅ Verified: Seniority level matches
- ✅ Verified: Remote availability matches
- ❌ Unknown: Compensation level
- ❌ Unknown: Company trajectory
- ❌ Unknown: Team maturity
- ❌ Unknown: Reporting structure

...is **not being honest about its reasoning**.

---

## Decision

StrataOS will transition from **Automation Engine** to **Decision-Support System** semantics.

### Automation Engine
```
Claim: "This is the right decision"
Role: Reduces human judgment to zero
Failure Mode: Confident wrong answer
Accountability: System responsible for outcome
```

### Decision-Support System
```
Claim: "This action passes the qualification threshold, but here is what you need to verify"
Role: Informs human judgment while being transparent about limits
Failure Mode: Human makes informed decision they understand
Accountability: System + human jointly responsible
```

---

## Implementation

### Output Structure Transition

#### v1.0 (Automation Engine Model)
```json
{
  "recommendation": "APPLY_IMMEDIATELY",
  "score": 0.8,
  "evidence_confidence": 1.0,
  "prediction_confidence": 1.0
}
```

Implied meaning: "System is highly confident this is correct."

#### v1.1 (Decision-Support System Model)
```json
{
  "recommendation": "APPLY_IMMEDIATELY",

  "alignment": {
    "score": 0.95,
    "interpretation": "High match with stated criteria"
  },

  "completeness": {
    "score": 0.43,
    "known_factors": 3,
    "required_factors": 7
  },

  "evidence_quality": {
    "score": 0.90,
    "source_quality": "HIGH"
  },

  "decision_confidence": {
    "score": 0.39,
    "level": "MEDIUM",
    "rationale": "Strong alignment with criteria, but insufficient context data"
  },

  "unknowns": [
    {
      "factor": "compensation",
      "impact": "HIGH",
      "decision_effect": "could_affect_financial_viability"
    },
    {
      "factor": "company_trajectory",
      "impact": "HIGH",
      "decision_effect": "could_affect_stability"
    }
  ]
}
```

Explicit meaning: "System recommends pursuing this, but recognizes these gaps in reasoning."

---

## Key Principle

**The recommendation action does not disappear.**

```
Old: "APPLY_IMMEDIATELY means I'm confident"
New: "APPLY_IMMEDIATELY means this passes the qualification threshold"
```

The system still says: "Pursue this opportunity."  
The system no longer claims: "I know this is the right move."

---

## Why This Matters

### Product Differentiation
An automation engine: replaces human judgment (risky, fails silently)  
A decision-support system: informs human judgment (transparent, fails visibly)

### Learning Signal
When a human disagrees with the recommendation:
- **Automation engine**: "The system was wrong"
- **Decision-support system**: "The system was wrong about [factor], which suggests we should improve [model aspect]"

The second enables continuous improvement.

### Trust Boundary
- **Automation engine**: "Trust the system completely or not at all"
- **Decision-support system**: "Trust the system for what it knows, verify what it doesn't"

The second is more realistic for executive decisions.

---

## Consequences

### Positive
1. Honest representation of reasoning limits
2. Enables continuous human feedback without full override requirement
3. Builds correct trust model (system + human > system alone)
4. Provides learning signal for adversarial cases (high fit / low confidence, etc.)
5. Establishes honest confidence semantics from the beginning

### Negative
1. Slightly more complex output structure
2. Requires education that "APPLY_IMMEDIATELY" doesn't mean certainty
3. Decision-support UX more complex than automation engine UX

### Neutral
1. v1.0 fields preserved (backward compatibility)
2. Existing recommendations do not change
3. Same policy weights still apply

---

## Verification

This decision is validated when:

1. ✅ Schema updated (decision.schema.json supports v1.1 fields)
2. ⏳ Golden fixture re-run with same recommendation, different confidence
   - Input: ServiceNow Principal, remote-available
   - Output: APPLY_IMMEDIATELY (same)
   - Old confidence: 1.0 (v1.0)
   - New confidence: 0.39-0.43 MEDIUM (v1.1)
3. ⏳ Unknowns correctly identified (compensation, company_trajectory, etc.)
4. ⏳ Adversarial fixtures prove the system can distinguish:
   - High alignment / low completeness (recommend with caution)
   - Low alignment / high completeness (investigate exceptions)
   - Strong match / fundamentally broken (avoid despite fit)
5. ⏳ Certification tier 2 (Decision Calibration Certified) updated to reflect this philosophy

---

## References

- CONFIDENCE_SEMANTICS_ROADMAP.md (implementation details)
- VALIDATION_REVIEW.md for principal-servicenow-role (evidence of the gap)
- certification-v1.0.0.json (pending_gates: Judgment Calibration Certification)

---

## Notes

This ADR formalizes the insight from the human validation review:

> "Perfect observational match ≠ good career move."

The system now must communicate this distinction explicitly, which is the maturation from automation to decision-support.
