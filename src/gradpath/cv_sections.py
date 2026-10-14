"""Detect common sections in extracted CV text."""

import re


SECTION_PATTERNS = {
    "summary": [
        r"professional summary",
        r"career summary",
        r"profile",
        r"about me",
        r"objective",
        r"career objective",
    ],
    "education": [
        r"education",
        r"academic background",
        r"educational background",
        r"qualifications",
    ],
    "experience": [
        r"experience",
        r"work experience",
        r"professional experience",
        r"employment history",
        r"work history",
        r"internship experience",
    ],
    "projects": [
        r"projects",
        r"personal projects",
        r"academic projects",
        r"selected projects",
        r"project experience",
        r"academic\s*&\s*t\s*e\s*c\s*h\s*n\s*i\s*c\s*a\s*l\s+projects",
    ],
    "skills": [
        r"skills",
        r"technical skills",
        r"core skills",
        r"technical competencies",
        r"key competencies",
        r"competencies",
    ],
    "certifications": [
        r"certifications",
        r"certificates",
        r"licenses and certifications",
        r"professional certifications",
    ],
}


def normalize_heading(line: str) -> str:
    """Normalize a potential heading for comparison."""
    line = line.strip().lower()
    line = re.sub(r"[\s:|—–-]+$", "", line)
    line = re.sub(r"^[\s:|—–-]+", "", line)
    return line.strip()


def identify_section_heading(line: str) -> str | None:
    """Return a known section name when the line is a heading."""
    heading = normalize_heading(line)

    if not heading or len(heading) > 60:
        return None

    # Remove common Markdown heading markers and numbering.
    heading = re.sub(r"^#+\s*", "", heading)
    heading = re.sub(r"^\d+[\s.)-]+", "", heading).strip()

    for section_name, patterns in SECTION_PATTERNS.items():
        for pattern in patterns:
            if re.fullmatch(pattern, heading):
                return section_name

    return None

def is_non_profile_heading(line: str) -> bool:
    """Identify headings that end a profile section but aren't stored separately."""
    heading = normalize_heading(line)
    heading = re.sub(r"^#+\s*", "", heading)
    heading = re.sub(r"^\d+[\s.)-]+", "", heading).strip()

    return heading in {
        "research & additional information",
        "ai research",
        "developer tools",
    }

def split_cv_sections(text: str) -> dict[str, str]:
    """
    Split extracted CV text into named sections.

    Text before a recognized heading is stored under 'general'.
    Repeated sections with the same name are combined in order.
    Heading lines are not included in section content.
    """
    sections = {"general": []}
    current_section = "general"

    for line in text.splitlines():
        if is_non_profile_heading(line):
            current_section = "general"
            continue

        detected_section = identify_section_heading(line)

        if detected_section:
            current_section = detected_section
            sections.setdefault(current_section, [])
            continue

        sections.setdefault(current_section, []).append(line)

    return {
        name: "\n".join(lines).strip()
        for name, lines in sections.items()
        if "\n".join(lines).strip()
    }
