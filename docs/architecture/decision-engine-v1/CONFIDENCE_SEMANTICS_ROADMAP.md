# Decision Model v1.1: Confidence Semantics Roadmap

**Status**: Schema Implementation Complete — Ready for Model Implementation  
**Objective**: Separate measurement (alignment) from interpretation (confidence); distinguish evidence quality from decision quality  
**Architectural Milestone**: Transition from **automation engine** to **decision-support system**  
**Blockers**: None (schema deployed)

---

## The Core Problem

The current model conflates two distinct questions:

```
Question 1: How well do known facts match the stated criteria?
            (Alignment measurement)

Question 2: How confident should the user be in this recommendation?
            (Decision guidance)
```

**Current (v1.0) Assumption**:
```
more matching evidence = more confidence
```

**Reality**:
```
More matching evidence ≠ more justified confidence
(if decision-critical factors are unknown)
```

### The Evidence of the Problem

The golden fixture reveals this gap:

```
Input:    ServiceNow ✓, Principal ✓, Remote ✓
v1.0:     recommendation="APPLY_IMMEDIATELY", confidence=1.0
Reality:  Missing compensation, company trajectory, team maturity
Expected: recommendation="APPLY_IMMEDIATELY", confidence=MEDIUM
```

The recommendation is correct. The confidence is wrong.

---

## Separating Two Confidence Concepts

The user must know two things about a recommendation:

### 1. Evidence Confidence
**Question**: "How sure are we our extracted facts are correct?"  
**Example**: Role description says "remote":
```
Evidence Confidence: HIGH (fact is clear and verifiable)
```

**Example**: Company structure from LinkedIn:
```
Evidence Confidence: MEDIUM (may have changed)
```

### 2. Decision Confidence
**Question**: "How sure should you be that this recommendation is the right action?"  
**Example**: Role with clear remote availability but unknown compensation:
```
Decision Confidence: MEDIUM (alignment high, but missing strategic context)
```

**Example**: Perfect technical match at a company in bankruptcy:
```
Decision Confidence: LOW (alignment high, but fundamentals broken)
```

---

## The v1.1 Contract

### What Changes
- Three independent dimensions: alignment, completeness, evidence_quality
- Two explicit confidence levels: evidence_confidence, decision_confidence
- Unknowns as first-class reasoning objects (not errors)
- Components stored separately (avoid premature multiplication)

### What Doesn't Change
- **Recommendation stays the same**: "APPLY_IMMEDIATELY" is still correct
- **Action is not diluted**: The system still says "pursue this"
- **Backward compatibility**: v1.0 fields remain for migration path

### Example: v1.1 Decision Object

```json
{
  "recommendation": "APPLY_IMMEDIATELY",

  "alignment": {
    "score": 0.95,
    "interpretation": "High match with stated criteria",
    "factors": [
      {
        "factor": "ServiceNow expertise",
        "score": 1.0,
        "evidence_ids": ["evidence_001"]
      },
      {
        "factor": "Leadership scope",
        "score": 0.9,
        "evidence_ids": ["evidence_002"]
      }
    ]
  },

  "completeness": {
    "score": 0.43,
    "known_factors": 3,
    "required_factors": 7,
    "gap_analysis": {
      "compensation": "unknown",
      "company_trajectory": "unknown",
      "team_maturity": "unknown",
      "reporting_structure": "unknown"
    }
  },

  "evidence_quality": {
    "score": 0.90,
    "source_quality": "HIGH"
  },

  "decision_confidence": {
    "score": 0.39,
    "level": "MEDIUM",
    "rationale": "Strong alignment with stated criteria, but insufficient compensation and company trajectory data to make high-confidence career decision",
    "components": {
      "alignment": 0.95,
      "completeness": 0.43,
      "evidence_quality": 0.90
    },
    "confidence_model": "v1_weighted"
  },

  "unknowns": [
    {
      "factor": "compensation",
      "impact": "HIGH",
      "decision_effect": "could_affect_financial_viability",
      "resolution_strategy": "research_compensation_bands"
    },
    {
      "factor": "company_trajectory",
      "impact": "HIGH",
      "decision_effect": "could_affect_stability_and_growth",
      "resolution_strategy": "research_company_growth_metrics"
    },
    {
      "factor": "team_maturity",
      "impact": "MEDIUM",
      "decision_effect": "could_affect_execution_risk",
      "resolution_strategy": "evaluate_team_during_interviews"
    }
  ],

  "legacy_v1_fields": {
    "score": 0.8,
    "evidence_confidence": 1.0,
    "prediction_confidence": 1.0
  }
}
```

**Key Interpretation**:
- ✅ System says: "Pursue this opportunity"
- ⚠️ System also says: "But you should validate these unknowns before committing"
- 🎯 This is the difference between automation and guidance

---

## Why Avoid Multiplicative Collapse (Initially)

The formula `Confidence = Alignment × Completeness × Evidence` is philosophically correct but operationally dangerous:

### Example 1: Good signal
```
Alignment:        1.0
Completeness:     0.5
Evidence Quality: 1.0
---
Result:           0.5 (good)
```

### Example 2: Collapse
```
Alignment:        0.7
Completeness:     0.3
Evidence Quality: 0.8
---
Result:           0.168 (everything looks terrible)
```

### Solution: Component Preservation

Store components independently:
```json
{
  "alignment": 0.70,
  "completeness": 0.30,
  "evidence_quality": 0.80,
  "confidence_model": "v1_weighted"
}
```

This allows:
1. **Human interpretation** (policy decides weighting)
2. **Future model evolution** (upgrade to v1_multiplicative or v1_bayesian)
3. **Better diagnostics** (see which component failed)

---

## Version Transition: Preserve Migration Path

### v1.0 (Legacy)
```json
{
  "recommendation": "APPLY_IMMEDIATELY",
  "score": 0.8,
  "evidence_confidence": 1.0,
  "prediction_confidence": 1.0
}
```

### v1.1 (Honest Reasoning)
```json
{
  "recommendation": "APPLY_IMMEDIATELY",
  "alignment": { ... },
  "completeness": { ... },
  "evidence_quality": { ... },
  "decision_confidence": { ... },
  "unknowns": [ ... ]
}
```

### Both Coexist (First Phase)
Keep v1.0 fields in decision object. Don't delete.
- Enables backward compatibility
- Preserves evidence of flaw
- Allows A/B testing consumer code

---

## The New Success Criterion

### v1.0 Success Metric
```
Same inputs → Same output
```

### v1.1 Success Metric
```
Same inputs + Same evidence + Same policy
→
Same recommendation + Same uncertainty explanation
```

The uncertainty explanation becomes part of the product.

---

## Implementation Phases

### Phase 1: Schema ✅ COMPLETE
- [x] Updated decision.schema.json to include alignment, completeness, evidence_quality, decision_confidence, unknowns
- [x] Made new v1.1 fields optional (backward compatible with existing fixtures)
- [x] Preserved v1.0 field structure for migration path

### Phase 2: Decision Model Implementation (NEXT)
1. Modify `_build_evidence()` to track observation completeness
2. Create `_calculate_alignment()` to score factor matching (replaces part of current scoring)
3. Create `_calculate_completeness()` to measure known vs. required factors
4. Create `_calculate_evidence_quality()` to assess source quality
5. Create `_calculate_decision_confidence()` to combine components
6. Create `_identify_unknowns()` to extract and score missing factors
7. Modify `_build_decision()` to populate new v1.1 fields while preserving v1.0 compatibility

### Phase 3: Fixture Re-validation
1. Re-run principal-servicenow-role fixture
2. Verify: Same recommendation (APPLY_IMMEDIATELY)
3. Verify: Confidence drops from 1.0 to ~0.39-0.43
4. Verify: Unknowns correctly identified
5. Generate new expected_decision.json with both v1.0 and v1.1 fields

### Phase 4: Validation Review Update
1. Update VALIDATION_REVIEW.md with new decision structure
2. Show how new model addresses human assessment gap
3. Document confidence breakdown reasoning

### Phase 5: Adversarial Fixtures (After Phase 4 proof)
Only create after Phase 4 validates the new semantics:

1. **High Fit / Insufficient Evidence**
   - Good keyword match, strong resume alignment
   - But missing critical context (new startup, unknown team)
   - Should recommend APPLY_IMMEDIATELY with LOW decision confidence

2. **Low Fit / Unexpected Upside**
   - Weak keyword match, lower seniority requirement
   - But exceptional upside (founder opportunity, board seat)
   - Should recommend HIGH_PRIORITY_REVIEW with MEDIUM-HIGH decision confidence despite low alignment

3. **Strong Resume Match / Bad Strategic Move**
   - Perfect skill alignment, clear level match
   - But company in distress, declining market, hostile culture
   - Should recommend NETWORK_FIRST with LOW decision confidence (or MONITOR)

4. **Weak Keyword Match / Excellent Executive Opportunity**
   - No direct skill overlap
   - But C-level role at well-capitalized, high-growth company
   - Should recommend RESEARCH_COMPANY / HIGH_PRIORITY_REVIEW

---

## Why This Matters

### v1.0 Proved
> The system can execute deterministically and reproduce results

### v1.1 Should Prove
> The system can reason honestly about its own limits

That distinction defines the product:

- **Automation Engine**: Replaces human judgment
- **Decision-Support System**: Informs human judgment while being transparent about uncertainty

StrataOS aims for the latter.

---

## The Philosophical Boundary

This release establishes the line between:

```
"I am confident in this answer"
(Automation engine claim)

vs.

"I recommend this action, but here is what I don't know"
(Decision-support system claim)
```

The first can fail. The second can educate.

That is the real intelligence milestone.

