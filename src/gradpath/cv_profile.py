
"""Build a structured GradPath candidate profile from a CV file."""

from pathlib import Path
import re

from gradpath.cv_reader import read_cv
from gradpath.cv_sections import split_cv_sections
from gradpath.cv_skills import extract_cv_skills


DATE_RANGE_PATTERN = re.compile(
    r"\b("
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
    r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
    r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}"
    r"|\d{4}"
    r")\s*(?:-|–|—|\bto\b)\s*("
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
    r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
    r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}"
    r"|\d{4}|present|current"
    r")\b",
    re.IGNORECASE,
)

DEGREE_PATTERN = re.compile(
    r"^\s*(?:"
    r"B\.?\s?S\.?|B\.?\s?Sc\.?|B\.?\s?A\.?|B\.?\s?E\.?|"
    r"M\.?\s?S\.?|M\.?\s?Sc\.?|M\.?\s?A\.?|M\.?\s?E\.?|"
    r"Ph\.?\s?D\.?|Bachelor(?:'s)?|Master(?:'s)?|Doctorate|"
    r"Associate(?:'s)?|Diploma"
    r")\b",
    re.IGNORECASE,
)

INSTITUTION_PATTERN = re.compile(
    r"\b(university|universities|college|institute|school|academy)\b",
    re.IGNORECASE,
)

ROLE_PATTERN = re.compile(
    r"\b("
    r"intern|analyst|engineer|developer|manager|specialist|"
    r"assistant|associate|consultant|researcher|coordinator|"
    r"officer|scientist|designer|executive|lead|director|"
    r"administrator|trainee|technician|accountant|professor|teacher|"
    r"representative"
    r")\b",
    re.IGNORECASE,
)

TECH_LABEL_PATTERN = re.compile(
    r"^\s*(?:tools?|technologies|tech(?:nology)? stack|"
    r"built with|frameworks)\s*:\s*(.*)$",
    re.IGNORECASE,
)


def _clean_lines(section_text: str) -> list[str]:
    """Clean bullet prefixes and blank lines without discarding content."""
    lines = []

    for raw_line in section_text.splitlines():
        line = re.sub(r"^\s*[-*•▪◦–—]\s*", "", raw_line).strip()
        if line:
            lines.append(line)

    return lines


def _date_range(line: str) -> tuple[str | None, str | None]:
    """Extract a recognizable date range without guessing missing dates."""
    match = DATE_RANGE_PATTERN.search(line)
    if not match:
        return None, None

    return match.group(1).strip(), match.group(2).strip()


def _institution_from_line(line: str) -> str | None:
    """Identify an institution when its name contains a known indicator."""
    candidates = re.split(r"\s*[|,]\s*", line)

    for candidate in candidates:
        if INSTITUTION_PATTERN.search(candidate):
            return candidate.strip()

    return None


def _is_degree_line(line: str) -> bool:
    return bool(DEGREE_PATTERN.search(line))


def _is_role_title(line: str) -> bool:
    """Recognize concise job-title-like lines, not full descriptions."""
    if len(line) > 100 or line.endswith((".", "!", "?", ";")):
        return False

    if re.match(r"^(worked|working|responsible|helped|created|built)\b", line, re.I):
        return False

    return bool(ROLE_PATTERN.search(line))



def _is_project_title(line: str) -> bool:
    """Recognize likely standalone project titles conservatively."""
    if len(line) > 100 or ":" in line or line.endswith((".", "!", "?", ";")):
        return False

    if TECH_LABEL_PATTERN.match(line):
        return False

    if "|" in line:
        return True

    words = line.split()
    if len(words) < 2:
        return False

    # Existing title-case format.
    if line == line.title():
        return True

    # Sentence-case titles are allowed when they are short and do not
    # look like a sentence or an action description.
    if len(words) <= 7:
        if re.match(
            r"^(built|created|developed|designed|implemented|"
            r"analyzed|analysed|used|worked|working|responsible|"
            r"helped|supported|using|leveraged|this|these|the)\b",
            line,
            re.IGNORECASE,
        ):
            return False

        return True

    return False


def _split_technologies(value: str) -> list[str]:
    """Split a recognizable technology list into individual items."""
    return [
        item.strip()
        for item in re.split(r"[,;|]", value)
        if item.strip()
    ]


def _extract_education(lines: list[str]) -> list[dict]:
    """Group related education lines until another degree begins."""
    entries = []
    current = None

    for line in lines:
        if current is not None and _is_degree_line(line) and current["degree"]:
            entries.append(current)
            current = None

        if current is None:
            current = {
                "degree": None,
                "institution": None,
                "start_date": None,
                "end_date": None,
                "details": "",
            }

        if _is_degree_line(line) and not current["degree"]:
            # If degree and institution share a line, separate them when
            # a recognizable institution indicator is present.
            institution = _institution_from_line(line)
            if institution and "," in line:
                parts = line.split(",", 1)
                current["degree"] = parts[0].strip()
                current["institution"] = institution
            else:
                current["degree"] = line

        institution = _institution_from_line(line)
        if institution:
            current["institution"] = institution

        start_date, end_date = _date_range(line)
        if start_date:
            current["start_date"] = start_date
            current["end_date"] = end_date
        elif re.fullmatch(r"\d{4}", line):
            # A single year is retained as a detail rather than assuming
            # whether it represents a start or end date.
            pass

        # Retain source lines even when structured fields were populated.
        # This prevents loss of context such as coursework or distinctions.
        if current["details"]:
            current["details"] += "\n"
        current["details"] += line

    if current is not None:
        entries.append(current)

    return entries


def _extract_experience(lines: list[str]) -> list[dict]:
    """Group role, organization, dates and responsibilities into records."""
    entries = []
    current = None

    for line in lines:
        if (
            current is not None
            and current["job_title"]
            and _is_role_title(line)
        ):
            entries.append(current)
            current = None

        if current is None:
            current = {
                "job_title": None,
                "organization": None,
                "start_date": None,
                "end_date": None,
                "description": "",
            }

        if not current["job_title"] and _is_role_title(line):
            current["job_title"] = line

        start_date, end_date = _date_range(line)
        if start_date:
            current["start_date"] = start_date
            current["end_date"] = end_date

        # Common CV layout: "Organization | June 2025 - August 2025".
        if "|" in line:
            left, right = line.split("|", 1)
            if _date_range(right)[0]:
                current["organization"] = left.strip()

        if current["description"]:
            current["description"] += "\n"
        current["description"] += line

    if current is not None:
        entries.append(current)

    return entries


def _extract_projects(lines: list[str]) -> list[dict]:
    """Group project titles, technology lists and descriptions."""
    entries = []
    current = None

    for line in lines:
        # Preserve support for the earlier "Project | Python, SQL" format.
        if "|" in line:
            name, technologies = line.split("|", 1)

            if current is not None:
                entries.append(current)

            current = {
                "name": name.strip() or None,
                "description": "",
                "technologies": _split_technologies(technologies),
            }
            continue

        technology_match = TECH_LABEL_PATTERN.match(line)
        if technology_match:
            if current is None:
                current = {
                    "name": None,
                    "description": "",
                    "technologies": [],
                }

            for technology in _split_technologies(technology_match.group(1)):
                if technology not in current["technologies"]:
                    current["technologies"].append(technology)
            continue

        if _is_project_title(line):
            if current is not None and current["name"] is None:
                # Upgrade a previously unclassified first line only when
                # it has not already accumulated a description.
                if not current["description"]:
                    current["name"] = line
                    continue

            if current is not None:
                entries.append(current)

            current = {
                "name": line,
                "description": "",
                "technologies": [],
            }
            continue

        if current is None:
            current = {
                "name": None,
                "description": "",
                "technologies": [],
            }

        if current["description"]:
            current["description"] += "\n"
        current["description"] += line

    if current is not None:
        entries.append(current)

    return entries


def extract_entries(section_text: str, section_name: str) -> list[dict]:
    """Create schema-aligned entries without inventing missing details."""
    lines = _clean_lines(section_text)

    if not lines:
        return []

    if section_name == "education":
        return _extract_education(lines)

    if section_name == "experience":
        return _extract_experience(lines)

    if section_name == "projects":
        return _extract_projects(lines)

    if section_name == "certifications":
        return [
            {"name": line, "issuer": None, "date": None}
            for line in lines
        ]

    return []


def build_candidate_profile(
    file_path: str | Path,
    candidate_id: str = "candidate_001",
) -> dict:
    """Read a CV and return a privacy-conscious structured profile."""
    document = read_cv(file_path)
    text = document["extracted_text"]
    sections = split_cv_sections(text)

    profile = {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "source_document": {
            "file_type": document["file_type"],
            "extraction_status": document["extraction_status"],
            "text_char_count": document["text_char_count"],
        },
        "education": extract_entries(
            sections.get("education", ""), "education"
        ),
        "experience": extract_entries(
            sections.get("experience", ""), "experience"
        ),
        "projects": extract_entries(
            sections.get("projects", ""), "projects"
        ),
        "certifications": extract_entries(
            sections.get("certifications", ""), "certifications"
        ),
        "skills": extract_cv_skills(text),
        "extraction_warnings": list(document["extraction_warnings"]),
    }

    if not text:
        profile["extraction_warnings"].append(
            "No text was extracted; the candidate profile may be incomplete."
        )

    return profile
