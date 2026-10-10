from gradpath.cv_skills import extract_cv_skills


sample_cv = """
Alex Example

EDUCATION
BS Data Science, Example University

TECHNICAL SKILLS
Python, SQL, Power BI

PROJECTS
Built a sales dashboard using Python and SQL.
"""

skills = extract_cv_skills(sample_cv)

for skill in skills:
    print(
        skill["skill_id"],
        skill["skill_name"],
        "verified=" + skill["verification_status"],
        "evidence_sections=" + ",".join(
            item["section"] for item in skill["evidence"]
        ),
    )

print("Total normalized skills:", len(skills))
print(
    "All skills unverified:",
    all(s["verification_status"] == "unverified" for s in skills),
)
