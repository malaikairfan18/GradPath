"""Controlled tests for the GradPath skill-gap analysis engine."""

from gradpath.skill_gap import analyze_skill_gaps


def make_profile(skills=None, warnings=None, char_count=500):
    return {
        "schema_version": "1.0",
        "candidate_id": "test_candidate",
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


def get_skill(results, skill_id):
    return next(row for row in results if row["skill_id"] == skill_id)


# Test 1: A mentioned skill remains unverified.
results = analyze_skill_gaps(
    make_profile([make_skill("SK001", "Python")]),
    "Data Scientist",
)
python_result = get_skill(results, "SK001")
assert python_result["candidate_status"] == "mentioned_unverified"
assert python_result["verification_status"] == "unverified"
assert python_result["candidate_evidence"]
print("1. Mentioned skill remains unverified: PASS")


# Test 2: A skill explicitly marked verified is represented as such.
results = analyze_skill_gaps(
    make_profile([make_skill("SK001", "Python", "verified")]),
    "Data Scientist",
)
assert get_skill(results, "SK001")["candidate_status"] == "verified_skill_present"
print("2. Verified status is preserved: PASS")


# Test 3: Missing skill in a usable profile is only a potential gap.
results = analyze_skill_gaps(make_profile(), "Data Analyst")
sql_result = get_skill(results, "SK003")
assert sql_result["candidate_status"] == "potential_gap"
assert "not proof" in sql_result["explanation"]
print("3. Missing mention is not treated as confirmed lack: PASS")


# Test 4: Extraction warnings make missing skills insufficient evidence.
results = analyze_skill_gaps(
    make_profile(warnings=["Document extraction may be incomplete"]),
    "Data Analyst",
)
assert get_skill(results, "SK003")["candidate_status"] == "insufficient_evidence"
print("4. Incomplete extraction is handled cautiously: PASS")


# Test 5: Rejected evidence is not counted as a demonstrated skill.
results = analyze_skill_gaps(
    make_profile([make_skill("SK001", "Python", "rejected")]),
    "Data Scientist",
)
assert get_skill(results, "SK001")["candidate_status"] == "rejected_evidence"
print("5. Rejected evidence is not counted as demonstrated: PASS")


# Test 6: Output includes both market and occupation evidence fields.
results = analyze_skill_gaps(make_profile(), "Data Scientist")
stats_result = get_skill(results, "SK009")
assert "market_observed_frequency_pct" in stats_result
assert "esco_relationship" in stats_result
assert "priority_score_method" in stats_result
print("6. Market and ESCO evidence are traceable: PASS")


# Test 7: Unsupported role names are rejected.
try:
    analyze_skill_gaps(make_profile(), "Machine Learning Engineer")
except ValueError:
    print("7. Unsupported role is rejected: PASS")
else:
    raise AssertionError("Unsupported role should raise ValueError.")


# Test 8: Invalid candidate input is rejected.
try:
    analyze_skill_gaps([], "Data Analyst")
except ValueError:
    print("8. Invalid candidate profile is rejected: PASS")
else:
    raise AssertionError("Invalid profile should raise ValueError.")


# Test 9: Results are deterministic and sorted by score.
first = analyze_skill_gaps(make_profile(), "Data Scientist")
second = analyze_skill_gaps(make_profile(), "Data Scientist")
assert first == second
scores = [row["priority_score"] for row in first]
assert scores == sorted(scores, reverse=True)
print("9. Output is deterministic and priority-sorted: PASS")



# Test 10: ESCO importance must not override observed market demand.
data_scientist_results = analyze_skill_gaps(
    make_profile(), "Data Scientist"
)
ml_result = get_skill(data_scientist_results, "SK016")
data_engineering_result = get_skill(data_scientist_results, "SK025")

assert ml_result["market_jobs_with_skill"] > 0
assert data_engineering_result["market_jobs_with_skill"] == 0
assert ml_result["priority_score"] > data_engineering_result["priority_score"]
assert ml_result["priority_score_method"] == data_engineering_result["priority_score_method"]
print("10. Market priority is independent of ESCO importance: PASS")


print(f"\nAll 10 skill-gap tests passed. Data Scientist rows: {len(first)}")
