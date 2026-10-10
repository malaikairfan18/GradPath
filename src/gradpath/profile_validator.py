"""Validate the structure and consistency of GradPath candidate profiles."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gradpath.cv_skills import load_skill_vocabulary


REQUIRED_PROFILE_FIELDS = {
    "schema_version",
    "candidate_id",
    "source_document",
    "education",
    "experience",
    "projects",
    "certifications",
    "skills",
    "extraction_warnings",
}

REQUIRED_SOURCE_FIELDS = {
    "file_type",
    "extraction_status",
    "text_char_count",
}

REQUIRED_SKILL_FIELDS = {
    "skill_id",
    "skill_name",
    "skill_category",
    "role",
    "evidence",
    "matched_alias",
    "match_type",
    "normalization_status",
    "verification_status",
}

VALID_VERIFICATION_STATUSES = {
    "unverified",
    "verified",
    "rejected",
}


def validate_candidate_profile(
    profile: dict,
    vocabulary=None,
) -> list[str]:
    """Return validation errors; an empty list means the profile is valid."""
    errors = []

    if not isinstance(profile, dict):
        return ["Profile must be a dictionary."]

    missing_fields = REQUIRED_PROFILE_FIELDS - profile.keys()
    if missing_fields:
        errors.append(
            f"Missing profile fields: {sorted(missing_fields)}"
        )

    source = profile.get("source_document")
    if not isinstance(source, dict):
        errors.append("'source_document' must be a dictionary.")
    else:
        missing_source_fields = REQUIRED_SOURCE_FIELDS - source.keys()
        if missing_source_fields:
            errors.append(
                "Missing source_document fields: "
                f"{sorted(missing_source_fields)}"
            )

        if source.get("text_char_count") is not None:
            if not isinstance(source["text_char_count"], int):
                errors.append("'text_char_count' must be an integer.")
            elif source["text_char_count"] < 0:
                errors.append("'text_char_count' cannot be negative.")

    for field in (
        "education",
        "experience",
        "projects",
        "certifications",
        "skills",
        "extraction_warnings",
    ):
        if field in profile and not isinstance(profile[field], list):
            errors.append(f"'{field}' must be a list.")

    if "extracted_text" in profile:
        errors.append(
            "Full extracted CV text must not be stored in the profile."
        )

    known_skills = {}
    if vocabulary is None:
        try:
            vocabulary = load_skill_vocabulary()
        except Exception as exc:
            errors.append(f"Could not load skill vocabulary: {exc}")
            vocabulary = None

    if vocabulary is not None:
        for _, row in vocabulary.iterrows():
            known_skills[row["skill_id"]] = {
                "skill_name": row["skill_name"],
                "skill_category": row["skill_category"],
            }

    for index, skill in enumerate(profile.get("skills", [])):
        prefix = f"skills[{index}]"

        if not isinstance(skill, dict):
            errors.append(f"{prefix} must be a dictionary.")
            continue

        missing_skill_fields = REQUIRED_SKILL_FIELDS - skill.keys()
        if missing_skill_fields:
            errors.append(
                f"{prefix} missing fields: {sorted(missing_skill_fields)}"
            )
            continue

        skill_id = skill.get("skill_id")

        if known_skills and skill_id not in known_skills:
            errors.append(f"{prefix} has unknown skill_id: {skill_id}")
        elif skill_id in known_skills:
            canonical = known_skills[skill_id]

            if skill.get("skill_name") != canonical["skill_name"]:
                errors.append(
                    f"{prefix} skill_name does not match its skill_id."
                )

            if skill.get("skill_category") != canonical["skill_category"]:
                errors.append(
                    f"{prefix} skill_category does not match its skill_id."
                )

        if not isinstance(skill.get("evidence"), list):
            errors.append(f"{prefix} evidence must be a list.")
        else:
            for evidence_index, evidence in enumerate(skill["evidence"]):
                if not isinstance(evidence, dict):
                    errors.append(
                        f"{prefix} evidence[{evidence_index}] "
                        "must be a dictionary."
                    )
                    continue

                if not evidence.get("text", "").strip():
                    errors.append(
                        f"{prefix} evidence[{evidence_index}] "
                        "must contain non-empty text."
                    )

        if skill.get("verification_status") not in VALID_VERIFICATION_STATUSES:
            errors.append(
                f"{prefix} has an invalid verification_status."
            )

        if skill.get("normalization_status") != "matched":
            errors.append(
                f"{prefix} has an unexpected normalization_status."
            )

    return errors
