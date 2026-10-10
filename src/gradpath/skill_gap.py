"""Explainable, deterministic skill-gap analysis for GradPath."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VOCABULARY_PATH = (
    PROJECT_ROOT / "data" / "processed" / "initial_skill_vocabulary.csv"
)
MARKET_PRIORITY_PATH = (
    PROJECT_ROOT / "data" / "processed" / "skill_priority_scores.csv"
)
ESCO_SKILLS_PATH = (
    PROJECT_ROOT / "data" / "processed" / "esco_role_skills_clean.csv"
)

SUPPORTED_ROLES = {"Data Analyst", "Data Scientist"}

REQUIRED_VOCABULARY_COLUMNS = {
    "skill_id", "skill_name", "skill_category", "role", "source", "aliases"
}
REQUIRED_MARKET_COLUMNS = {
    "role_category", "skill_id", "skill_name", "jobs_with_skill",
    "relevant_jobs_total", "observed_frequency_pct", "evidence_level",
    "priority_rank", "scoring_method"
}
REQUIRED_ESCO_COLUMNS = {
    "GradPath Role", "relationship", "skillLabel"
}

# Only exact canonical-label matches are accepted in this initial version.
# No fuzzy or guessed mappings are made.
EXPLICIT_ESCO_LABELS = {
    "statistics": "Statistics",
    "data engineering": "Data Engineering",
}


def _require_columns(
    dataframe: pd.DataFrame,
    required: set[str],
    dataset_name: str,
) -> None:
    """Raise a readable error when a source dataset lacks required fields."""
    missing = required - set(dataframe.columns)
    if missing:
        raise ValueError(
            f"{dataset_name} is missing required columns: "
            f"{sorted(missing)}"
        )


def _normalise_role(role: str) -> str:
    """Validate and return a supported GradPath role."""
    if not isinstance(role, str):
        raise ValueError(
            "target_role must be 'Data Analyst' or 'Data Scientist'."
        )

    cleaned = role.strip().casefold()
    for supported_role in SUPPORTED_ROLES:
        if cleaned == supported_role.casefold():
            return supported_role

    raise ValueError(
        f"Unsupported target role: {role!r}. "
        "Choose 'Data Analyst' or 'Data Scientist'."
    )


def _load_sources(
    vocabulary: pd.DataFrame | None = None,
    market_priority: pd.DataFrame | None = None,
    esco_skills: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load or validate the three existing GradPath source datasets."""
    if vocabulary is None:
        vocabulary = pd.read_csv(VOCABULARY_PATH).fillna("")
    else:
        vocabulary = vocabulary.copy().fillna("")

    if market_priority is None:
        market_priority = pd.read_csv(MARKET_PRIORITY_PATH).fillna("")
    else:
        market_priority = market_priority.copy().fillna("")

    if esco_skills is None:
        esco_skills = pd.read_csv(ESCO_SKILLS_PATH).fillna("")
    else:
        esco_skills = esco_skills.copy().fillna("")

    _require_columns(vocabulary, REQUIRED_VOCABULARY_COLUMNS, "Vocabulary")
    _require_columns(
        market_priority, REQUIRED_MARKET_COLUMNS, "Market priority data"
    )
    _require_columns(esco_skills, REQUIRED_ESCO_COLUMNS, "ESCO skill data")

    if vocabulary["skill_id"].duplicated().any():
        raise ValueError("Vocabulary contains duplicate skill_id values.")

    return vocabulary, market_priority, esco_skills


def _profile_extraction_is_incomplete(profile: dict) -> bool:
    """Conservatively identify profiles whose missing skills are ambiguous."""
    source = profile.get("source_document", {})
    warnings = profile.get("extraction_warnings", [])

    status = str(source.get("extraction_status", "")).strip().casefold()
    char_count = source.get("text_char_count")

    incomplete_statuses = {
        "failed", "error", "empty", "no_text", "unsupported"
    }

    if status in incomplete_statuses:
        return True

    if not isinstance(char_count, int) or char_count < 1:
        return True

    if warnings:
        return True

    return False


def _esco_evidence(
    role: str,
    skill_name: str,
    esco_skills: pd.DataFrame,
) -> dict:
    """Return ESCO evidence only when an explicit label mapping exists."""
    canonical_label = EXPLICIT_ESCO_LABELS.get(skill_name.casefold())

    result = {
        "esco_mapping_status": "not_mapped",
        "esco_relationship": "none",
        "esco_label": None,
    }

    if canonical_label is None:
        return result

    role_rows = esco_skills[
        esco_skills["GradPath Role"].astype(str).str.casefold()
        == role.casefold()
    ]

    matching_rows = role_rows[
        role_rows["skillLabel"].astype(str).str.strip().str.casefold()
        == canonical_label.casefold()
    ]

    if matching_rows.empty:
        return result

    relationships = {
        str(value).strip().casefold()
        for value in matching_rows["relationship"].tolist()
    }

    if "essential" in relationships:
        relationship = "essential"
    elif "optional" in relationships:
        relationship = "optional"
    else:
        relationship = sorted(relationships)[0] if relationships else "none"

    return {
        "esco_mapping_status": "exact_label_match",
        "esco_relationship": relationship,
        "esco_label": canonical_label,
    }


def _candidate_evidence(profile: dict) -> dict[str, dict]:
    """Index extracted profile skills by canonical skill ID."""
    result = {}

    for skill in profile.get("skills", []):
        if not isinstance(skill, dict):
            continue

        skill_id = skill.get("skill_id")
        if not isinstance(skill_id, str) or not skill_id.strip():
            continue

        # If a malformed profile contains duplicate IDs, preserve all evidence
        # while avoiding an accidental upgrade of verification status.
        if skill_id not in result:
            result[skill_id] = {
                "skill": skill,
                "evidence": list(skill.get("evidence", []))
                if isinstance(skill.get("evidence"), list)
                else [],
            }
        else:
            result[skill_id]["evidence"].extend(
                item for item in skill.get("evidence", [])
                if item not in result[skill_id]["evidence"]
            )

            current_status = result[skill_id]["skill"].get(
                "verification_status", "unverified"
            )
            incoming_status = skill.get("verification_status", "unverified")

            # Conflicting duplicate records should not be treated as verified.
            if current_status != incoming_status:
                result[skill_id]["skill"] = {
                    **result[skill_id]["skill"],
                    "verification_status": "unverified",
                }

    return result


def analyze_skill_gaps(
    candidate_profile: dict,
    target_role: str,
    vocabulary: pd.DataFrame | None = None,
    market_priority: pd.DataFrame | None = None,
    esco_skills: pd.DataFrame | None = None,
) -> list[dict]:
    """
    Analyse candidate evidence against role-specific market and ESCO evidence.

    A missing CV mention is never treated as proof of missing proficiency.
    Returned priority scores are heuristic ranking aids, not readiness scores.
    """
    if not isinstance(candidate_profile, dict):
        raise ValueError("candidate_profile must be a dictionary.")

    role = _normalise_role(target_role)
    vocabulary, market_priority, esco_skills = _load_sources(
        vocabulary, market_priority, esco_skills
    )

    candidate_skills = _candidate_evidence(candidate_profile)
    incomplete_profile = _profile_extraction_is_incomplete(candidate_profile)

    role_market = market_priority[
        market_priority["role_category"].astype(str).str.casefold()
        == role.casefold()
    ].copy()

    market_by_id = {}
    for _, row in role_market.iterrows():
        skill_id = str(row["skill_id"])
        if skill_id not in market_by_id:
            market_by_id[skill_id] = row.to_dict()

    vocabulary_by_id = {
        str(row["skill_id"]): row.to_dict()
        for _, row in vocabulary.iterrows()
    }

    results = []

    for skill_id, vocab_row in vocabulary_by_id.items():
        taxonomy_role = str(vocab_row.get("role", "")).strip().casefold()
        if taxonomy_role not in {"both", role.casefold()}:
            continue

        market = market_by_id.get(skill_id, {})
        candidate_record = candidate_skills.get(skill_id)
        skill_name = str(vocab_row["skill_name"])

        if candidate_record is None:
            verification_status = "not_detected"
            candidate_status = (
                "insufficient_evidence"
                if incomplete_profile
                else "potential_gap"
            )
            evidence = []
        else:
            skill = candidate_record["skill"]
            verification_status = str(
                skill.get("verification_status", "unverified")
            ).strip().casefold()
            evidence = candidate_record["evidence"]

            if verification_status == "verified":
                candidate_status = "verified_skill_present"
            elif verification_status == "rejected":
                candidate_status = "rejected_evidence"
            else:
                candidate_status = "mentioned_unverified"

        jobs_with_skill = pd.to_numeric(
            market.get("jobs_with_skill", 0), errors="coerce"
        )
        relevant_jobs_total = pd.to_numeric(
            market.get("relevant_jobs_total", 0), errors="coerce"
        )
        frequency = pd.to_numeric(
            market.get("observed_frequency_pct", 0), errors="coerce"
        )
        priority_rank = pd.to_numeric(
            market.get("priority_rank", 0), errors="coerce"
        )

        jobs_with_skill = (
            int(jobs_with_skill) if pd.notna(jobs_with_skill) else 0
        )
        relevant_jobs_total = (
            int(relevant_jobs_total)
            if pd.notna(relevant_jobs_total)
            else 0
        )
        frequency = float(frequency) if pd.notna(frequency) else 0.0
        priority_rank = int(priority_rank) if pd.notna(priority_rank) else None

        esco = _esco_evidence(role, skill_name, esco_skills)

        # Market-only 0-100 score. ESCO importance remains a separate field
        # and cannot override the observed market ranking.
        # This is a descriptive heuristic, not a probability or readiness score.
        priority_score = round(min(max(frequency, 0.0), 100.0), 2)

        if jobs_with_skill == 0:
            market_evidence_status = "no_observed_matches"
        elif jobs_with_skill <= 5:
            market_evidence_status = "limited_observed_evidence"
        elif jobs_with_skill <= 10:
            market_evidence_status = "moderate_observed_evidence"
        else:
            market_evidence_status = "stronger_observed_evidence"

        if candidate_status == "verified_skill_present":
            explanation = (
                "The profile marks this skill as verified. Review the "
                "supporting evidence before relying on that status."
            )
        elif candidate_status == "mentioned_unverified":
            explanation = (
                "The skill is mentioned in the CV, but the mention does "
                "not independently establish proficiency."
            )
        elif candidate_status == "rejected_evidence":
            explanation = (
                "The profile marks this skill evidence as rejected; "
                "it is not counted as a demonstrated skill."
            )
        elif candidate_status == "insufficient_evidence":
            explanation = (
                "The skill was not detected, but extraction warnings or "
                "missing text mean the CV evidence is insufficient."
            )
        else:
            explanation = (
                "The skill was not detected in the extracted CV. This is a "
                "potential gap to investigate, not proof that the candidate "
                "lacks the skill."
            )

        if esco["esco_relationship"] == "essential":
            explanation += " ESCO labels it essential for this role."
        elif esco["esco_relationship"] == "optional":
            explanation += " ESCO labels it optional for this role."

        if jobs_with_skill == 0:
            explanation += (
                " No matches were observed in the current job dataset; "
                "this does not establish zero real-world demand."
            )

        results.append({
            "target_role": role,
            "skill_id": skill_id,
            "skill_name": skill_name,
            "skill_category": vocab_row.get("skill_category", ""),
            "candidate_status": candidate_status,
            "verification_status": verification_status,
            "candidate_evidence": evidence,
            "market_jobs_with_skill": jobs_with_skill,
            "market_relevant_jobs_total": relevant_jobs_total,
            "market_observed_frequency_pct": frequency,
            "market_priority_rank": priority_rank,
            "market_evidence_level": market.get("evidence_level", ""),
            "market_evidence_status": market_evidence_status,
            "esco_mapping_status": esco["esco_mapping_status"],
            "esco_relationship": esco["esco_relationship"],
            "esco_label": esco["esco_label"],
            "priority_score": priority_score,
            "priority_score_method": (
                "Capped observed market frequency percentage (0-100); "
                "market-only descriptive heuristic, not a probability, "
                "candidate readiness score, or measure of total skill importance"
            ),
            "extraction_incomplete": incomplete_profile,
            "explanation": explanation,
        })

    # Higher priority first; retain canonical skill ID as deterministic tie-break.
    results.sort(
        key=lambda item: (
            -item["priority_score"],
            item["market_priority_rank"] is None,
            item["market_priority_rank"] or 10**9,
            item["skill_id"],
        )
    )

    return results
