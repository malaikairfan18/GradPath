from gradpath.cv_skills import extract_cv_skills


# 1. Empty input should return no skills.
empty_result = extract_cv_skills("")
print("Empty input returns no skills:", empty_result == [])

# 2. Repeated Python mentions should produce one normalized skill,
#    with evidence retained from both sections.
duplicate_cv = """
TECHNICAL SKILLS
Python, Python programming

PROJECTS
Built a Python data analysis project.
"""
duplicate_result = extract_cv_skills(duplicate_cv)
python_matches = [
    skill for skill in duplicate_result
    if skill["skill_id"] == "SK001"
]
print("Python appears once in normalized results:", len(python_matches) == 1)
print(
    "Python evidence includes both sections:",
    bool(python_matches)
    and {e["section"] for e in python_matches[0]["evidence"]}
    == {"skills", "projects"},
)

# 3. Unknown phrases should not receive invented skill IDs.
unknown_cv = """
TECHNICAL SKILLS
Quantum Banana Engineering
"""
unknown_result = extract_cv_skills(unknown_cv)
print("Unknown phrase does not create a skill:", unknown_result == [])

# 4. A lone 'R' should not match inside ordinary words.
r_cv = """
PROJECTS
Created a report about customer growth.
"""
r_result = extract_cv_skills(r_cv)
r_matches = [
    skill for skill in r_result
    if skill["skill_id"] == "SK002"
]
print("R not falsely matched inside words:", r_matches == [])

# 5. A standalone R mention should be matched only if supported
#    by the existing vocabulary aliases.
standalone_r_cv = """
TECHNICAL SKILLS
R programming
"""
standalone_r_result = extract_cv_skills(standalone_r_cv)
standalone_r_matches = [
    skill for skill in standalone_r_result
    if skill["skill_id"] == "SK002"
]
print("R programming alias detected:", bool(standalone_r_matches))
