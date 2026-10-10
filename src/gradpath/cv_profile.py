"""Build a structured GradPath candidate profile from a CV file."""

from pathlib import Path
import re

from gradpath.cv_reader import read_cv
from gradpath.cv_sections import split_cv_sections
from gradpath.cv_skills import extract_cv_skills


def extract_entries(section_text: str, section_name: str) -> list[dict]:
    """Create schema-aligned entries without inventing missing details."""
    lines = []

    for line in section_text.splitlines():
        line = re.sub(r"^\s*[-*•]\s*", "", line).strip()
        if line:
            lines.append(line)

    entries = []

    for line in lines:
        if section_name == "education":
            entry = {
                "degree": None,
                "institution": None,
                "start_date": None,
                "end_date": None,
                "details": line,
            }
        elif section_name == "experience":
            entry = {
                "job_title": None,
                "organization": None,
                "start_date": None,
                "end_date": None,
                "description": line,
            }
        elif section_name == "projects":
            entry = {
                "name": None,
                "description": line,
                "technologies": [],
            }
        elif section_name == "certifications":
            entry = {
                "name": line,
                "issuer": None,
                "date": None,
            }
        else:
            continue

        entries.append(entry)

    return entries


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
