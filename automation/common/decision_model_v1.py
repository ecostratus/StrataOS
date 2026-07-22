"""Deterministic reference pipeline for StrataOS decision-model contract tests.

This module is intentionally small and side-effect free. It provides a stable
baseline for validating architecture contracts before broader implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any


DECISION_MODEL_VERSION = "1.0.0"
ENGINE_VERSION = "decision-model-v1-reference"
FIXTURE_VERSION = "v1"


@dataclass(frozen=True)
class EvaluationBundle:
    evidence: list[dict[str, Any]]
    claims: list[dict[str, Any]]
    decision: dict[str, Any]
    recommendation: dict[str, Any]
    trace_artifact: dict[str, Any]


def _normalize_observations(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort observations by stable key to guarantee order independence."""
    return sorted(observations, key=lambda obs: str(obs.get("observation_id", "")))


def _stable_inputs_hash(
    person: dict[str, Any],
    opportunity: dict[str, Any],
    observations: list[dict[str, Any]],
    policy: dict[str, Any],
) -> str:
    obs_ids = sorted(str(obs.get("observation_id", "")) for obs in observations)
    person_id = str(person.get("person_id", ""))
    opportunity_id = str(opportunity.get("opportunity_id", ""))
    policy_id = str(policy.get("id", ""))
    return "|".join([person_id, opportunity_id, policy_id, ",".join(obs_ids)])


def _canonical_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _build_evidence(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for obs in _normalize_observations(observations):
        observation_id = str(obs["observation_id"])
        evidence.append(
            {
                "evidence_id": f"ev-{observation_id}",
                "person_id": str(obs["person_id"]),
                "opportunity_id": str(obs["opportunity_id"]),
                "observation_ids": [observation_id],
                "kind": str(obs.get("key", "unknown")),
                "quality": float(obs.get("quality", 1.0)),
                "provenance": {
                    "source": str(obs.get("source", "unknown")),
                    "captured_at": str(obs.get("captured_at", "2026-01-01T00:00:00Z")),
                    "parser": "observation-parser-v1",
                    "normalizer": "observation-normalizer-v1",
                    "evidence_builder": "evidence-builder-v1",
                    "claim_generator": "claim-generator-v1",
                },
            }
        )
    return evidence


def _build_claims(
    person: dict[str, Any],
    opportunity: dict[str, Any],
    observations: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    person_id = str(person["person_id"])
    opportunity_id = str(opportunity["opportunity_id"])
    skills = set(person.get("profile", {}).get("skills", []))
    seniority = str(person.get("attributes", {}).get("seniority", "")).lower()

    evidence_by_obs_id = {
        ev["observation_ids"][0]: ev["evidence_id"]
        for ev in evidence
        if ev.get("observation_ids")
    }

    claims: dict[str, dict[str, Any]] = {}
    for obs in _normalize_observations(observations):
        observation_id = str(obs["observation_id"])
        key = str(obs.get("key", "")).lower()
        value = str(obs.get("value", ""))
        value_lower = value.lower()
        evidence_id = evidence_by_obs_id[observation_id]

        if key == "required_skill" and value in skills:
            claim_id = f"cl-skill-{value_lower.replace(' ', '-')}-match"
            claims[claim_id] = {
                "claim_id": claim_id,
                "decision_model_version": DECISION_MODEL_VERSION,
                "person_id": person_id,
                "opportunity_id": opportunity_id,
                "predicate": "skill_match",
                "value": value,
                "polarity": "positive",
                "confidence": 1.0,
                "evidence_ids": [evidence_id],
            }
        elif key == "role_level":
            polarity = "positive" if value_lower == seniority else "negative"
            claim_id = f"cl-seniority-{polarity}"
            claims[claim_id] = {
                "claim_id": claim_id,
                "decision_model_version": DECISION_MODEL_VERSION,
                "person_id": person_id,
                "opportunity_id": opportunity_id,
                "predicate": "seniority_alignment",
                "value": value,
                "polarity": polarity,
                "confidence": 1.0,
                "evidence_ids": [evidence_id],
            }
        elif key == "work_mode":
            requires_remote = bool(person.get("constraints", {}).get("remote_only", False))
            polarity = "positive" if (not requires_remote or value_lower == "remote") else "negative"
            claim_id = f"cl-remote-{polarity}"
            claims[claim_id] = {
                "claim_id": claim_id,
                "decision_model_version": DECISION_MODEL_VERSION,
                "person_id": person_id,
                "opportunity_id": opportunity_id,
                "predicate": "remote_alignment",
                "value": value,
                "polarity": polarity,
                "confidence": 1.0,
                "evidence_ids": [evidence_id],
            }

    return [claims[k] for k in sorted(claims.keys())]


def _build_decision(
    person: dict[str, Any],
    opportunity: dict[str, Any],
    claims: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    policy: dict[str, Any],
) -> dict[str, Any]:
    weights = policy.get("weights", {})
    thresholds = policy.get("thresholds", {})

    score = 0.0
    positive_explanations: list[dict[str, Any]] = []
    negative_explanations: list[dict[str, Any]] = []
    evidence_confidences: list[float] = []
    prediction_confidences: list[float] = []
    claim_ids: list[str] = []

    for claim in claims:
        predicate = str(claim["predicate"])
        claim_weight = float(weights.get(predicate, 0.0))
        sign = 1.0 if claim["polarity"] == "positive" else -1.0
        contribution = sign * claim_weight
        score += contribution
        claim_ids.append(str(claim["claim_id"]))
        evidence_confidences.append(float(claim["confidence"]))
        prediction_confidences.append(float(claim["confidence"]))

        explanation = {
            "direction": "positive" if sign > 0 else "negative",
            "claim_ref": str(claim["claim_id"]),
            "message": f"{predicate} -> {contribution:+.2f}",
        }
        if sign > 0:
            positive_explanations.append(explanation)
        else:
            negative_explanations.append(explanation)

    if score >= float(thresholds.get("apply_immediately", 0.8)):
        recommendation = "APPLY_IMMEDIATELY"
    elif score >= float(thresholds.get("high_priority_review", 0.6)):
        recommendation = "HIGH_PRIORITY_REVIEW"
    elif score >= float(thresholds.get("network_first", 0.4)):
        recommendation = "NETWORK_FIRST"
    elif score >= float(thresholds.get("monitor", 0.2)):
        recommendation = "MONITOR"
    else:
        recommendation = "IGNORE"

    policy_id = str(policy["id"])
    person_id = str(person["person_id"])
    opportunity_id = str(opportunity["opportunity_id"])
    decision_id = f"dec-{person_id}-{opportunity_id}-{policy_id}"
    inputs_hash = _stable_inputs_hash(person, opportunity, observations, policy)
    policy_hash = _canonical_hash(policy)
    engine_hash = _canonical_hash({"engine_version": ENGINE_VERSION, "decision_model_version": DECISION_MODEL_VERSION})
    fixture_hash = _canonical_hash(
        {
            "fixture_version": FIXTURE_VERSION,
            "person": person,
            "opportunity": opportunity,
            "observations": _normalize_observations(observations),
            "policy": policy,
        }
    )

    return {
        "id": decision_id,
        "decision_model_version": DECISION_MODEL_VERSION,
        "person_id": person_id,
        "opportunity_id": opportunity_id,
        "policy_id": policy_id,
        "recommendation": recommendation,
        "score": round(score, 4),
        "evidence_confidence": round(sum(evidence_confidences) / max(len(evidence_confidences), 1), 4),
        "prediction_confidence": round(sum(prediction_confidences) / max(len(prediction_confidences), 1), 4),
        "claim_ids": sorted(claim_ids),
        "explanations": positive_explanations + negative_explanations,
        "inputs_hash": inputs_hash,
        "policy_hash": policy_hash,
        "engine_hash": engine_hash,
        "fixture_hash": fixture_hash,
        "engine_version": ENGINE_VERSION,
        "created_at": "2026-01-01T00:00:00Z",
    }


def _build_recommendation(decision: dict[str, Any]) -> dict[str, Any]:
    drivers = [
        {
            "direction": str(expl["direction"]),
            "message": str(expl["message"]),
            "claim_ref": str(expl["claim_ref"]),
        }
        for expl in decision.get("explanations", [])
    ]
    return {
        "decision_id": str(decision["id"]),
        "decision_model_version": DECISION_MODEL_VERSION,
        "action": str(decision["recommendation"]),
        "summary": f"Action {decision['recommendation']} based on weighted claim evidence",
        "drivers": drivers,
    }


def _build_trace_artifact(
    observations: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    claims: list[dict[str, Any]],
) -> dict[str, Any]:
    observation_by_id = {str(obs["observation_id"]): obs for obs in observations}
    evidence_by_id = {str(ev["evidence_id"]): ev for ev in evidence}

    trace_rows: list[dict[str, Any]] = []
    for claim in sorted(claims, key=lambda c: str(c["claim_id"])):
        claim_id = str(claim["claim_id"])
        evidence_id = str(claim["evidence_ids"][0])
        evidence_item = evidence_by_id[evidence_id]
        observation_id = str(evidence_item["observation_ids"][0])
        obs = observation_by_id[observation_id]
        trace_rows.append(
            {
                "observation_id": observation_id,
                "evidence_id": evidence_id,
                "claim_id": claim_id,
                "decision_factor": str(claim["predicate"]),
                "recommendation_driver": "positive" if claim["polarity"] == "positive" else "negative",
                "source": str(obs.get("source", "unknown")),
            }
        )

    return {"decision_model_version": DECISION_MODEL_VERSION, "trace": trace_rows}


# ============================================================================
# V1.1 Reasoning Layer (Additive — preserves v1 output untouched)
# ============================================================================
# This layer adds uncertainty-aware reasoning on top of the deterministic engine.
# It does NOT modify existing outputs. New fields are added only.

DECISION_CRITICAL_FACTORS = [
    "required_skill",
    "role_level",
    "work_mode",
    "compensation_level",
    "company_trajectory",
    "team_maturity",
    "reporting_structure",
]


def _calculate_alignment(
    claims: list[dict[str, Any]],
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate how well known facts match stated criteria.
    
    Returns alignment score (0-1) and factor breakdown.
    This measures observational accuracy, not completeness.
    """
    # Extract alignment factors from claims
    factors: list[dict[str, Any]] = []
    for claim in claims:
        predicate = str(claim["predicate"])
        if predicate in ["skill_match", "seniority_alignment", "remote_alignment"]:
            factors.append({
                "factor": predicate.replace("_", " ").title(),
                "score": float(claim["confidence"]),
                "evidence_ids": claim.get("evidence_ids", []),
            })
    
    # Overall alignment is the average of factor scores
    overall = sum(f["score"] for f in factors) / max(len(factors), 1) if factors else 0.0
    
    return {
        "score": round(overall, 4),
        "interpretation": (
            "High match with stated criteria" if overall >= 0.9
            else "Moderate match with stated criteria" if overall >= 0.7
            else "Weak match with stated criteria"
        ),
        "factors": factors,
    }


def _calculate_completeness(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate what fraction of decision-critical information is available.
    
    Returns completeness score (0-1) and gap analysis.
    """
    observed_keys = set(str(obs.get("key", "")) for obs in observations)
    required_keys = set(DECISION_CRITICAL_FACTORS)
    
    known_factors = list(observed_keys & required_keys)
    missing_factors = list(required_keys - observed_keys)
    
    known_count = len(known_factors)
    required_count = len(required_keys)
    completeness_score = known_count / max(required_count, 1)
    
    gap_analysis = {factor: "unknown" for factor in sorted(missing_factors)}
    
    return {
        "score": round(completeness_score, 4),
        "known_factors": sorted(known_factors),
        "required_factors": required_count,
        "observed_factors": known_count,
        "gap_analysis": gap_analysis,
    }


def _identify_unknowns(
    observations: list[dict[str, Any]],
    person: dict[str, Any],
    opportunity: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract unknowns as first-class reasoning objects.
    
    Maps missing factors to their impact on the decision.
    """
    observed_keys = set(str(obs.get("key", "")) for obs in observations)
    required_keys = set(DECISION_CRITICAL_FACTORS)
    missing_factors = required_keys - observed_keys
    
    impact_map = {
        "compensation_level": {"impact": "HIGH", "decision_effect": "may_affect_financial_viability"},
        "company_trajectory": {"impact": "HIGH", "decision_effect": "may_affect_stability_and_growth"},
        "team_maturity": {"impact": "MEDIUM", "decision_effect": "may_affect_execution_risk"},
        "reporting_structure": {"impact": "MEDIUM", "decision_effect": "may_affect_scope_clarity"},
    }
    
    unknowns: list[dict[str, Any]] = []
    for factor in sorted(missing_factors):
        info = impact_map.get(str(factor), {
            "impact": "MEDIUM",
            "decision_effect": "additional_context_needed"
        })
        unknowns.append({
            "factor": str(factor),
            "impact": info["impact"],
            "decision_effect": info["decision_effect"],
            "resolution_strategy": f"research_{factor.replace('_', '_')}",
        })
    
    return unknowns


def _calculate_evidence_quality(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Assess the reliability of extracted evidence.
    
    Higher quality sources increase evidence confidence.
    """
    if not observations:
        return {"score": 0.0, "source_quality": "UNKNOWN"}
    
    qualities = [float(obs.get("quality", 0.5)) for obs in observations]
    average_quality = sum(qualities) / len(qualities)
    
    quality_level = (
        "HIGH" if average_quality >= 0.8
        else "MEDIUM" if average_quality >= 0.5
        else "LOW"
    )
    
    return {
        "score": round(average_quality, 4),
        "source_quality": quality_level,
    }


def _calculate_decision_confidence(
    alignment_score: float,
    completeness_score: float,
    evidence_quality_score: float,
) -> dict[str, Any]:
    """Calculate justified certainty in the recommendation.
    
    Uses conservative interpretation: does not premultiply.
    Stores components separately for policy evolution.
    """
    # Conservative interpretation-based confidence
    # (avoids false precision from multiplication)
    
    if alignment_score >= 0.9 and completeness_score >= 0.7:
        confidence_level = "HIGH"
        confidence_score = 0.85
    elif alignment_score >= 0.8 and completeness_score >= 0.5:
        confidence_level = "MEDIUM"
        confidence_score = 0.55
    elif alignment_score >= 0.6 or completeness_score >= 0.3:
        confidence_level = "MEDIUM"
        confidence_score = 0.45
    else:
        confidence_level = "LOW"
        confidence_score = 0.25
    
    # Adjust if evidence quality is low
    if evidence_quality_score < 0.7:
        confidence_level = (
            "MEDIUM" if confidence_level == "HIGH" else "LOW"
        )
        confidence_score *= 0.8
    
    rationale_parts = []
    if alignment_score >= 0.9:
        rationale_parts.append("strong alignment with stated criteria")
    elif alignment_score >= 0.7:
        rationale_parts.append("moderate alignment with stated criteria")
    else:
        rationale_parts.append("weak alignment with stated criteria")
    
    if completeness_score < 0.7:
        rationale_parts.append(
            f"incomplete information ({int(completeness_score * 100)}% of decision factors known)"
        )
    
    rationale = ", but ".join(rationale_parts) if len(rationale_parts) > 1 else rationale_parts[0]
    
    return {
        "score": round(confidence_score, 4),
        "level": confidence_level,
        "rationale": rationale,
        "components": {
            "alignment": round(alignment_score, 4),
            "completeness": round(completeness_score, 4),
            "evidence_quality": round(evidence_quality_score, 4),
        },
        "confidence_model": "v1_weighted_conservative",
    }


def _enrich_decision_output(
    decision: dict[str, Any],
    person: dict[str, Any],
    opportunity: dict[str, Any],
    observations: list[dict[str, Any]],
    claims: list[dict[str, Any]],
) -> dict[str, Any]:
    """Add v1.1 reasoning fields to decision output.
    
    Preserves all v1.0 fields. New fields are purely additive.
    This enables comparison between v1.0 and v1.1 outputs.
    """
    alignment = _calculate_alignment(claims, observations)
    completeness = _calculate_completeness(observations)
    evidence_quality = _calculate_evidence_quality(observations)
    unknowns = _identify_unknowns(observations, person, opportunity)
    decision_confidence = _calculate_decision_confidence(
        alignment["score"],
        completeness["score"],
        evidence_quality["score"],
    )
    
    # Add v1.1 fields (decision_model_version stays v1.0 for compatibility)
    enriched = {**decision}
    enriched["alignment"] = alignment
    enriched["completeness"] = completeness
    enriched["evidence_quality"] = evidence_quality
    enriched["decision_confidence"] = decision_confidence
    enriched["unknowns"] = unknowns
    
    return enriched


def evaluate(
    person: dict[str, Any],
    opportunity: dict[str, Any],
    observations: list[dict[str, Any]],
    policy: dict[str, Any],
) -> EvaluationBundle:
    """Run deterministic evaluation from observations to recommendation and trace.
    
    v1.0: Builds evidence → claims → decision → recommendation
    v1.1: Adds uncertainty-aware reasoning layer to decision (additive, preserves v1.0)
    """
    evidence = _build_evidence(observations)
    claims = _build_claims(person, opportunity, observations, evidence)
    decision = _build_decision(person, opportunity, claims, observations, policy)
    
    # NEW: Enrich decision with v1.1 reasoning layer (additive, preserves v1.0 fields)
    decision = _enrich_decision_output(decision, person, opportunity, observations, claims)
    
    recommendation = _build_recommendation(decision)
    trace_artifact = _build_trace_artifact(observations, evidence, claims)
    return EvaluationBundle(
        evidence=evidence,
        claims=claims,
        decision=decision,
        recommendation=recommendation,
        trace_artifact=trace_artifact,
    )
