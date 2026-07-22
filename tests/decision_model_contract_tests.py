"""Decision-model v1 contract tests.

These tests enforce deterministic replay and full traceability across:
Observation -> Evidence -> Claim -> Decision -> Recommendation.
"""

from __future__ import annotations

import json
import os
import sys


_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_COMMON_DIR = os.path.join(_REPO_ROOT, "automation", "common")
if _COMMON_DIR not in sys.path:
    sys.path.insert(0, _COMMON_DIR)

import decision_model_v1  # type: ignore


_FIXTURE_DIR = os.path.join(_REPO_ROOT, "tests", "fixtures", "v1", "principal-servicenow-role")


def _load_json(name: str):
    path = os.path.join(_FIXTURE_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_fixture_inputs():
    person = _load_json("person.json")
    opportunity = _load_json("opportunity.json")
    observations = _load_json("observations.json")
    policy = _load_json("policy.json")
    return person, opportunity, observations, policy


def test_replay_determinism_same_input_same_output():
    person, opportunity, observations, policy = _load_fixture_inputs()

    run1 = decision_model_v1.evaluate(person, opportunity, observations, policy)
    run2 = decision_model_v1.evaluate(person, opportunity, observations, policy)

    assert run1.evidence == run2.evidence
    assert run1.claims == run2.claims
    assert run1.decision == run2.decision
    assert run1.recommendation == run2.recommendation
    assert run1.decision["inputs_hash"] == run2.decision["inputs_hash"]


def test_order_independence_observation_permutation_same_output():
    person, opportunity, observations, policy = _load_fixture_inputs()

    permuted = [observations[2], observations[0], observations[1]]
    run_original = decision_model_v1.evaluate(person, opportunity, observations, policy)
    run_permuted = decision_model_v1.evaluate(person, opportunity, permuted, policy)

    assert run_original.evidence == run_permuted.evidence
    assert run_original.claims == run_permuted.claims
    assert run_original.decision == run_permuted.decision
    assert run_original.recommendation == run_permuted.recommendation


def test_idempotence_repeat_runs_no_duplicates_or_drift():
    person, opportunity, observations, policy = _load_fixture_inputs()

    run1 = decision_model_v1.evaluate(person, opportunity, observations, policy)
    run2 = decision_model_v1.evaluate(person, opportunity, observations, policy)
    run3 = decision_model_v1.evaluate(person, opportunity, observations, policy)

    assert run1.evidence == run2.evidence == run3.evidence
    assert run1.claims == run2.claims == run3.claims
    assert run1.decision == run2.decision == run3.decision
    assert run1.recommendation == run2.recommendation == run3.recommendation

    evidence_ids = [ev["evidence_id"] for ev in run1.evidence]
    claim_ids = [cl["claim_id"] for cl in run1.claims]
    assert len(evidence_ids) == len(set(evidence_ids))
    assert len(claim_ids) == len(set(claim_ids))


def test_end_to_end_traceability_matches_golden_fixture():
    person, opportunity, observations, policy = _load_fixture_inputs()
    run = decision_model_v1.evaluate(person, opportunity, observations, policy)

    expected_evidence = _load_json("expected_evidence.json")
    expected_claims = _load_json("expected_claims.json")
    expected_decision = _load_json("expected_decision.json")
    expected_recommendation = _load_json("expected_recommendation.json")
    expected_trace_artifact = _load_json("expected_trace_artifact.json")

    assert run.evidence == expected_evidence
    assert run.claims == expected_claims
    assert run.decision == expected_decision
    assert run.recommendation == expected_recommendation
    assert run.trace_artifact == expected_trace_artifact

    claim_ids = {c["claim_id"] for c in run.claims}
    evidence_ids = {e["evidence_id"] for e in run.evidence}
    observation_ids = {o["observation_id"] for o in observations}

    # Recommendation -> Decision
    assert run.recommendation["decision_id"] == run.decision["id"]

    # Decision -> Claims
    assert set(run.decision["claim_ids"]).issubset(claim_ids)

    # Claims -> Evidence
    for claim in run.claims:
        assert set(claim["evidence_ids"]).issubset(evidence_ids)

    # Evidence -> Observations
    for evidence in run.evidence:
        assert set(evidence["observation_ids"]).issubset(observation_ids)

    # Trace rows must link every layer
    for row in run.trace_artifact["trace"]:
        assert row["observation_id"] in observation_ids
        assert row["evidence_id"] in evidence_ids
        assert row["claim_id"] in claim_ids


def test_snapshot_artifacts_match_golden_files():
    person, opportunity, observations, policy = _load_fixture_inputs()
    run = decision_model_v1.evaluate(person, opportunity, observations, policy)

    assert run.decision == _load_json("expected_decision.json")
    assert run.recommendation == _load_json("expected_recommendation.json")
    assert run.trace_artifact == _load_json("expected_trace_artifact.json")


def test_v1_v1_1_migration_recommendation_consistency():
    """Verify v1.1 preserves v1 recommendations while adding uncertainty explanation.
    
    This test validates the key architectural transition:
    - v1.0 output is preserved (backward compatible)
    - v1.1 output is added (forward compatible)
    - Recommendation stays the same (action not diluted)
    - Confidence changes to reflect unknowns (honest reasoning)
    """
    person, opportunity, observations, policy = _load_fixture_inputs()
    run = decision_model_v1.evaluate(person, opportunity, observations, policy)
    decision = run.decision

    # Verify v1.0 fields are preserved unchanged
    assert "recommendation" in decision
    assert "score" in decision
    assert "evidence_confidence" in decision
    assert "prediction_confidence" in decision
    assert decision["recommendation"] == "APPLY_IMMEDIATELY"
    
    # Verify v1.1 fields are added
    assert "alignment" in decision
    assert "completeness" in decision
    assert "evidence_quality" in decision
    assert "decision_confidence" in decision
    assert "unknowns" in decision

    # Verify recommendation is NOT changed by v1.1 enrichment
    # (same action, different confidence interpretation)
    assert decision["recommendation"] == "APPLY_IMMEDIATELY"

    # Verify alignment is high (all observed factors match)
    assert decision["alignment"]["score"] >= 0.9
    assert len(decision["alignment"]["factors"]) >= 3

    # Verify completeness is moderate (only 3 of 7 decision factors known)
    completeness = decision["completeness"]["score"]
    assert 0.35 <= completeness <= 0.50, (
        f"Expected completeness around 43% (3 of 7 factors), got {completeness:.1%}"
    )

    # Verify unknowns are identified
    assert len(decision["unknowns"]) > 0
    unknown_factors = {u["factor"] for u in decision["unknowns"]}
    assert "compensation_level" in unknown_factors
    assert "company_trajectory" in unknown_factors

    # Verify decision_confidence is MEDIUM (not HIGH despite perfect alignment)
    decision_conf = decision["decision_confidence"]
    assert decision_conf["level"] in ["MEDIUM", "LOW"]
    # Score should be lower than v1.0's prediction_confidence due to incompleteness
    assert decision_conf["score"] < decision["prediction_confidence"]

    # Verify confidence components are captured
    assert "components" in decision_conf
    assert "alignment" in decision_conf["components"]
    assert "completeness" in decision_conf["components"]
    assert "evidence_quality" in decision_conf["components"]
    
    # Verify rationale explains the gap
    rationale = str(decision_conf.get("rationale", ""))
    assert "strong alignment" in rationale.lower() or "high match" in rationale.lower()
    assert "incomplete" in rationale.lower() or "unknown" in rationale.lower()
