"""Integration tests for Phase 4 skill gaps and Phase 5 recommendations."""

from gradpath.skill_gap import analyze_skill_gaps
from gradpath.learning_recommendations import recommend_learning_actions


def make_profile(skills=None, warnings=None, char_count=500):
    return {
        "schema_version": "1.0",
        "candidate_id": "phase5_integration_candidate",
        "source_document": {
            "file_type": "pdf",
            "extraction_status": "success",
            "text_char_count": char_count,
        },
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "skills": skills or [],
        "extraction_warnings": warnings or [],
    }


def make_skill(skill_id, skill_name, status="unverified"):
    return {
        "skill_id": skill_id,
        "skill_name": skill_name,
        "skill_category": "Test",
        "role": "Both",
        "evidence": [{
            "section": "skills",
            "text": f"Used {skill_name}",
            "evidence_type": "skill_mention",
        }],
        "matched_alias": skill_name,
        "match_type": "canonical",
        "normalization_status": "matched",
        "verification_status": status,
    }


# Test 1: Real Phase 4 output flows into Phase 5 for Data Analyst.
profile = make_profile([make_skill("SK001", "Python", "verified")])
gaps = analyze_skill_gaps(profile, "Data Analyst")
recommendations = recommend_learning_actions(gaps, "Data Analyst")

assert gaps, "Phase 4 should return skill-gap records."
assert recommendations, "Phase 5 should return recommendations."
assert all(item["target_role"] == "Data Analyst" for item in recommendations)
assert all(item["recommended_action"] != "maintain" for item in recommendations)
print("1. Data Analyst Phase 4-to-5 pipeline: PASS")


# Test 2: Real Phase 4 output flows into Phase 5 for Data Scientist.
profile = make_profile([make_skill("SK016", "Machine Learning", "verified")])
gaps = analyze_skill_gaps(profile, "Data Scientist")
recommendations = recommend_learning_actions(gaps, "Data Scientist")

assert gaps, "Phase 4 should return skill-gap records."
assert recommendations, "Phase 5 should return recommendations."
assert all(item["target_role"] == "Data Scientist" for item in recommendations)
assert all(item["recommended_action"] != "maintain" for item in recommendations)
print("2. Data Scientist Phase 4-to-5 pipeline: PASS")


# Test 3: A potential gap produces a learning action with a real catalogue resource.
profile = make_profile()
gaps = analyze_skill_gaps(profile, "Data Analyst")
recommendations = recommend_learning_actions(gaps, "Data Analyst")

sql_recommendation = next(
    item for item in recommendations if item["skill_id"] == "SK003"
)
assert sql_recommendation["recommended_action"] == "learn"
assert sql_recommendation["resource_id"]
assert sql_recommendation["resource_url"].startswith("https://")
print("3. Potential gap maps to a catalogue resource: PASS")


# Test 4: Incomplete extraction leads to investigation, not an assumed learning gap.
profile = make_profile(
    warnings=["Document extraction may be incomplete"]
)
gaps = analyze_skill_gaps(profile, "Data Analyst")
recommendations = recommend_learning_actions(gaps, "Data Analyst")

sql_recommendation = next(
    item for item in recommendations if item["skill_id"] == "SK003"
)
assert sql_recommendation["recommended_action"] == "investigate"
assert not sql_recommendation["resource_id"]
print("4. Incomplete extraction triggers investigation: PASS")


# Test 5: An unverified mention is not labelled as a confirmed skill.
profile = make_profile([make_skill("SK001", "Python", "unverified")])
gaps = analyze_skill_gaps(profile, "Data Scientist")
recommendations = recommend_learning_actions(gaps, "Data Scientist")

python_recommendation = next(
    item for item in recommendations if item["skill_id"] == "SK001"
)
assert python_recommendation["candidate_status"] == "mentioned_unverified"
assert python_recommendation["recommended_action"] in {"practice", "investigate"}
print("5. Unverified evidence is handled cautiously: PASS")


print(
    "\nAll 5 Phase 4-to-5 integration tests passed."
)
