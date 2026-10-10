"""Tests for the GradPath learning recommendation engine."""

import pandas as pd

from gradpath.learning_recommendations import (
    recommend_learning_actions,
)


def make_gap(
    skill_id="SK001",
    skill_name="Python",
    status="potential_gap",
    priority=10.0,
    rank=1,
    role="Data Scientist",
    incomplete=False,
):
    """Create a controlled Phase 4-style record."""
    return {
        "target_role": role,
        "skill_id": skill_id,
        "skill_name": skill_name,
        "skill_category": "Programming",
        "candidate_status": status,
        "verification_status": (
            "not_detected"
            if status in {"potential_gap", "insufficient_evidence"}
            else "verified"
            if status == "verified_skill_present"
            else "rejected"
            if status == "rejected_evidence"
            else "unverified"
        ),
        "priority_score": priority,
        "market_priority_rank": rank,
        "market_jobs_with_skill": 5,
        "market_relevant_jobs_total": 100,
        "market_evidence_level": "limited",
        "market_evidence_status": "limited_observed_evidence",
        "esco_mapping_status": "mapped",
        "esco_relationship": "essential",
        "esco_label": skill_name,
        "extraction_incomplete": incomplete,
    }


def run_tests():
    # 1. Potential gaps receive learning recommendations.
    results = recommend_learning_actions(
        [make_gap()], "Data Scientist"
    )
    assert len(results) == 1
    assert results[0]["recommended_action"] == "learn"
    assert results[0]["resource_url"].startswith("https://")

    # 2. Incomplete CV evidence triggers investigation, not learning.
    results = recommend_learning_actions(
        [
            make_gap(
                status="insufficient_evidence",
                incomplete=True,
            )
        ],
        "Data Scientist",
    )
    assert len(results) == 1
    assert results[0]["recommended_action"] == "investigate"
    assert results[0]["resource_id"] is None

    # 3. An unverified skill mention triggers practical assessment.
    results = recommend_learning_actions(
        [make_gap(status="mentioned_unverified")],
        "Data Scientist",
    )
    assert len(results) == 1
    assert results[0]["recommended_action"] == "practice"
    assert results[0]["resource_id"] != ""

    # 4. Rejected evidence triggers reassessment.
    results = recommend_learning_actions(
        [make_gap(status="rejected_evidence")],
        "Data Scientist",
    )
    assert len(results) == 1
    assert results[0]["recommended_action"] == "reassess"
    assert results[0]["resource_id"] is None

    # 5. Verified skills are excluded by default.
    results = recommend_learning_actions(
        [make_gap(status="verified_skill_present")],
        "Data Scientist",
    )
    assert results == []

    # 6. Maintenance is optional.
    results = recommend_learning_actions(
        [make_gap(status="verified_skill_present")],
        "Data Scientist",
        include_maintenance=True,
    )
    assert len(results) == 1
    assert results[0]["recommended_action"] == "maintain"

    # 7. Results are deterministically ordered by market priority.
    gaps = [
        make_gap("SK003", "SQL", priority=4.0, rank=3),
        make_gap("SK001", "Python", priority=10.0, rank=1),
    ]
    first = recommend_learning_actions(gaps, "Data Scientist")
    second = recommend_learning_actions(gaps, "Data Scientist")
    assert [r["skill_id"] for r in first] == ["SK001", "SK003"]
    assert first == second

    # 8. Resource role compatibility is respected.
    analyst_gap = make_gap(
        skill_id="SK011",
        skill_name="Power BI",
        role="Data Analyst",
    )
    analyst_results = recommend_learning_actions(
        [analyst_gap], "Data Analyst"
    )
    assert len(analyst_results) == 1
    assert analyst_results[0]["resource_id"] == "LR011"

    # 9. Unsupported roles are rejected.
    try:
        recommend_learning_actions([], "Data Engineer")
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported role should raise ValueError.")

    # 10. Malformed gap records are rejected.
    try:
        recommend_learning_actions([{"skill_id": "SK001"}], "Data Scientist")
    except ValueError:
        pass
    else:
        raise AssertionError("Malformed gap should raise ValueError.")

    # 11. Malformed resource catalogues are rejected.
    bad_resources = pd.DataFrame([{"skill_id": "SK001"}])
    try:
        recommend_learning_actions(
            [make_gap()], "Data Scientist", resources=bad_resources
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid resource schema should raise ValueError.")

    # 12. Missing resources do not create fabricated learning actions.
    resources = pd.read_csv(
        "data/resources/learning_resources.csv",
        dtype=str,
    )
    no_python = resources[resources["skill_id"] != "SK001"]
    results = recommend_learning_actions(
        [make_gap()], "Data Scientist", resources=no_python
    )
    assert results == []

    # 13. Market and ESCO evidence remain separate in explanations.
    results = recommend_learning_actions(
        [make_gap()], "Data Scientist"
    )
    explanation = results[0]["explanation"]
    assert "market evidence" in explanation.lower()
    assert "ESCO" in explanation
    assert "candidate readiness" in explanation

    print("PASS: 13 learning recommendation tests")


if __name__ == "__main__":
    run_tests()
