from gradpath.cv_sections import split_cv_sections

text = """
Alex Example
Data analyst interested in analytics

EDUCATION
BS Data Science, Example University

TECHNICAL SKILLS:
Python, SQL, Power BI

PROJECTS
Built a sales dashboard using Python
"""

sections = split_cv_sections(text)

print("Sections:", list(sections.keys()))
print(
    "Education detected:",
    "Example University" in sections.get("education", "")
)
print(
    "Skills detected:",
    "Power BI" in sections.get("skills", "")
)
print(
    "Projects detected:",
    "sales dashboard" in sections.get("projects", "")
)
