"""Test section detection with heading variations and ordinary text."""

from gradpath.cv_sections import identify_section_heading, split_cv_sections


HEADING_CASES = [
    ("Skills", "skills"),
    ("Technical Skills:", "skills"),
    ("## Education", "education"),
    ("1. Work Experience", "experience"),
    ("Academic Projects —", "projects"),
    ("Professional Certifications", "certifications"),
    ("Career Objective", "summary"),
    ("Academic & Technical Projects", "projects"),
]

NEGATIVE_CASES = [
    "I have strong technical skills in Python.",
    "My education helped me learn data science.",
    "I completed projects during university.",
    "I have experience with SQL and Power BI.",
    "This is a summary of my academic project.",
    "Research & Additional Information",
]

print("SECTION HEADING VARIATION TEST")
print("=" * 50)

heading_passes = 0

for heading, expected in HEADING_CASES:
    actual = identify_section_heading(heading)
    passed = actual == expected
    heading_passes += int(passed)
    print(
        f"{'PASS' if passed else 'FAIL'} | "
        f"{heading!r} | expected={expected!r}, actual={actual!r}"
    )

print("\nORDINARY TEXT FALSE-POSITIVE TEST")
print("=" * 50)

negative_passes = 0

for line in NEGATIVE_CASES:
    actual = identify_section_heading(line)
    passed = actual is None
    negative_passes += int(passed)
    print(
        f"{'PASS' if passed else 'FAIL'} | "
        f"{line!r} | actual={actual!r}"
    )

print("\nSECTION SPLITTING TEST")
print("=" * 50)

sample = """
Malaika Irfan
Data Science Graduate

1. Education
BS Data Science

Technical Skills:
Python, SQL, Power BI
"""

sections = split_cv_sections(sample)

print("Detected sections:", sorted(sections))
print("Education content retained:", "BS Data Science" in sections.get("education", ""))
print("Skills content retained:", "Python, SQL, Power BI" in sections.get("skills", ""))

print("\nSUMMARY")
print(f"Heading variations passed: {heading_passes}/{len(HEADING_CASES)}")
print(f"Ordinary-text checks passed: {negative_passes}/{len(NEGATIVE_CASES)}")
