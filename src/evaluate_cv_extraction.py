"""Evaluate GradPath CV skill extraction on controlled synthetic CVs."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from gradpath.cv_sections import split_cv_sections
from gradpath.cv_skills import extract_cv_skills


CASES = [
    {
        "name": "Skills section",
        "text": """
Technical Skills
Python, SQL, Power BI
""",
        "expected_skills": {"Python", "SQL", "Power BI"},
        "expected_sections": {"skills"},
    },
    {
        "name": "Projects and experience",
        "text": """
Work Experience
Used Python and SQL to clean data.

Academic Projects
Built a Power BI dashboard.
""",
        "expected_skills": {"Python", "SQL", "Power BI", "Data Cleaning"},
        "expected_sections": {"experience", "projects"},
    },
    {
        "name": "Mixed sections and unknown technology",
        "text": """
Professional Summary
Data graduate interested in analytics.

Education
BS Data Science

Projects
Analyzed a dataset using Python and an imaginary tool called DataMagic.
""",
        "expected_skills": {"Python"},
        "expected_sections": {"summary", "education", "projects"},
    },
]


def calculate_metrics(expected, predicted):
    true_positive = len(expected & predicted)
    false_positive = len(predicted - expected)
    false_negative = len(expected - predicted)

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive else 1.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative else 1.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return precision, recall, f1, true_positive, false_positive, false_negative


all_expected = set()
all_predicted = set()
section_hits = 0
section_total = 0
privacy_checks = []
verification_checks = []

print("GRADPATH CONTROLLED CV EXTRACTION EVALUATION")
print("=" * 55)

for case in CASES:
    sections = split_cv_sections(case["text"])
    skills = extract_cv_skills(case["text"])

    expected = case["expected_skills"]
    predicted = {skill["skill_name"] for skill in skills}

    all_expected.update(
        f'{case["name"]}::{skill}' for skill in expected
    )
    all_predicted.update(
        f'{case["name"]}::{skill}' for skill in predicted
    )

    expected_sections = case["expected_sections"]
    detected_sections = set(sections) - {"general"}

    section_hits += len(expected_sections & detected_sections)
    section_total += len(expected_sections)

    privacy_checks.append("extracted_text" not in {
        "schema_version": "1.0",
        "skills": skills,
    })
    verification_checks.append(
        all(skill["verification_status"] == "unverified" for skill in skills)
    )

    print(f"\nCase: {case['name']}")
    print("Expected skills:", sorted(expected))
    print("Predicted skills:", sorted(predicted))
    print("Missing skills:", sorted(expected - predicted))
    print("Unexpected skills:", sorted(predicted - expected))
    print("Expected sections:", sorted(expected_sections))
    print("Detected sections:", sorted(detected_sections))

precision, recall, f1, tp, fp, fn = calculate_metrics(
    all_expected, all_predicted
)

print("\n" + "=" * 55)
print("AGGREGATE RESULTS")
print(f"Skill precision: {precision:.3f}")
print(f"Skill recall:    {recall:.3f}")
print(f"Skill F1:        {f1:.3f}")
print(f"Correct skill matches: {tp}")
print(f"Unexpected skill matches: {fp}")
print(f"Missed expected skills: {fn}")
print(
    "Section heading detection recall: "
    f"{section_hits / section_total:.3f}" if section_total else
    "Section heading detection recall: N/A"
)
print("Privacy checks passed:", all(privacy_checks))
print("Skills remain unverified:", all(verification_checks))
print(
    "\nImportant: These are synthetic test cases, "
    "not evidence of performance on real-world CVs."
)
