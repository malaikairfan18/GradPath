"""Extract normalized skills and evidence from CV sections."""

from pathlib import Path
import re
import sys

import pandas as pd

from gradpath.cv_sections import split_cv_sections


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VOCABULARY_PATH = (
    PROJECT_ROOT / "data" / "processed" / "initial_skill_vocabulary.csv"
)

# The existing Phase 2 matcher lives in src/, outside the gradpath package.
SRC_PATH = Path(__file__).resolve().parents[1]
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from extract_baseline_skills import (  # noqa: E402
    extract_skills,
    prepare_vocabulary,
)


SECTION_EVIDENCE_TYPES = {
    "projects": "project_mention",
    "experience": "experience_mention",
    "education": "education_mention",
    "certifications": "certification_mention",
    "skills": "skill_mention",
    "summary": "skill_mention",
    "general": "skill_mention",
}


def load_skill_vocabulary(
    vocabulary_path: str | Path = VOCABULARY_PATH,
) -> pd.DataFrame:
    """Load and prepare the existing GradPath skill vocabulary."""
    path = Path(vocabulary_path)

    if not path.exists():
        raise FileNotFoundError(
            f"GradPath skill vocabulary not found: {path}"
        )

    vocabulary = pd.read_csv(path).fillna("")
    required_columns = {
        "skill_id",
        "skill_name",
        "skill_category",
        "role",
        "source",
        "aliases",
    }

    missing = required_columns - set(vocabulary.columns)
    if missing:
        raise ValueError(
            f"Skill vocabulary is missing columns: {sorted(missing)}"
        )

    return prepare_vocabulary(vocabulary)


def find_evidence_snippet(
    section_text: str,
    matched_alias: str,
    max_length: int = 240,
) -> str:
    """Return a short line containing the matched alias when possible."""
    lines = [line.strip() for line in section_text.splitlines() if line.strip()]

    for line in lines:
        if re.search(
            rf"(?<![a-z0-9]){re.escape(matched_alias)}(?![a-z0-9])",
            line,
            flags=re.IGNORECASE,
        ):
            if len(line) <= max_length:
                return line
            return line[: max_length - 3].rstrip() + "..."

    # Fall back to the first non-empty line if the alias appears across
    # unusual punctuation or formatting that the simple search missed.
    if lines:
        line = lines[0]
        return line if len(line) <= max_length else line[: max_length - 3] + "..."

    return ""


def extract_cv_skills(
    text: str,
    vocabulary: pd.DataFrame | None = None,
) -> list[dict]:
    """Extract vocabulary-matched skills with section-level evidence."""
    if not isinstance(text, str) or not text.strip():
        return []

    if vocabulary is None:
        vocabulary = load_skill_vocabulary()

    sections = split_cv_sections(text)
    matches_by_id = {}

    for section_name, section_text in sections.items():
        if not section_text.strip():
            continue

        for match in extract_skills(section_text, vocabulary):
            skill_id = match["skill_id"]
            evidence_type = SECTION_EVIDENCE_TYPES.get(
                section_name,
                "skill_mention",
            )
            snippet = find_evidence_snippet(
                section_text,
                match["matched_alias"],
            )

            evidence = {
                "section": section_name,
                "text": snippet,
                "evidence_type": evidence_type,
            }

            if skill_id not in matches_by_id:
                matches_by_id[skill_id] = {
                    "skill_id": match["skill_id"],
                    "skill_name": match["skill_name"],
                    "skill_category": match["skill_category"],
                    "role": match["role"],
                    "evidence": [],
                    "matched_alias": match["matched_alias"],
                    "match_type": match["match_type"],
                    "normalization_status": "matched",
                    "verification_status": "unverified",
                }

            if evidence not in matches_by_id[skill_id]["evidence"]:
                matches_by_id[skill_id]["evidence"].append(evidence)

    return list(matches_by_id.values())
