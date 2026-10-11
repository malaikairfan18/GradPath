"""Explainable, deterministic project recommendations for GradPath."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from gradpath.learning_recommendations import (
    SUPPORTED_ROLES,
    _safe_bool,
    _safe_number,
)
from gradpath.skill_gap import _normalise_role


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_CATALOGUE_PATH = (
    PROJECT_ROOT / "data" / "resources" / "project_catalogue.csv"
)
VOCABULARY_PATH = (
    PROJECT_ROOT / "data" / "processed" / "initial_skill_vocabulary.csv"
)

REQUIRED_PROJECT_COLUMNS = {
    "project_id",
    "project_title",
    "description",
    "target_roles",
    "skill_ids",
    "difficulty",
    "estimated_hours",
    "prerequisites",
    "deliverables",
    "evidence_criteria",
}

ALLOWED_PROJECT_ROLES = {"Both", "Data Analyst", "Data Scientist"}
ALLOWED_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}
ACTIONABLE_STATUSES = {
    "potential_gap",
    "insufficient_evidence",
    "mentioned_unverified",
    "rejected_evidence",
}
DIFFICULTY_ORDER = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}


def _validate_project_catalogue(
    projects: pd.DataFrame,
    valid_skill_ids: set[str],
    skill_roles: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Validate a project catalogue and return a normalized copy."""
    if not isinstance(projects, pd.DataFrame):
        raise ValueError("projects must be a pandas DataFrame.")

    missing = sorted(REQUIRED_PROJECT_COLUMNS - set(projects.columns))
    if missing:
        raise ValueError(
            "Project catalogue is missing required columns: "
            + ", ".join(missing)
        )

    frame = projects.copy()

    for column in REQUIRED_PROJECT_COLUMNS:
        frame[column] = frame[column].fillna("").astype(str).str.strip()

    required_nonempty = [
        "project_id",
        "project_title",
        "description",
        "target_roles",
        "skill_ids",
        "difficulty",
        "deliverables",
        "evidence_criteria",
    ]
    for column in required_nonempty:
        empty = frame[column].eq("")
        if empty.any():
            row = frame.index[empty][0]
            raise ValueError(
                f"Project catalogue contains an empty {column} at row {row}."
            )

    if frame["project_id"].duplicated().any():
        duplicate = frame.loc[
            frame["project_id"].duplicated(keep=False), "project_id"
        ].iloc[0]
        raise ValueError(f"Duplicate project_id: {duplicate!r}")

    invalid_roles = ~frame["target_roles"].isin(ALLOWED_PROJECT_ROLES)
    if invalid_roles.any():
        row = frame.index[invalid_roles][0]
        raise ValueError(
            f"Invalid target_roles at row {row}: "
            f"{frame.loc[row, 'target_roles']!r}"
        )

    invalid_difficulties = ~frame["difficulty"].isin(ALLOWED_DIFFICULTIES)
    if invalid_difficulties.any():
        row = frame.index[invalid_difficulties][0]
        raise ValueError(
            f"Invalid difficulty at row {row}: "
            f"{frame.loc[row, 'difficulty']!r}"
        )

    hours = pd.to_numeric(frame["estimated_hours"], errors="coerce")
    invalid_hours = hours.isna() | ~hours.map(
        lambda value: pd.notna(value) and value > 0 and float(value).is_integer()
    )
    if invalid_hours.any():
        row = frame.index[invalid_hours][0]
        raise ValueError(
            f"estimated_hours must be a positive integer at row {row}."
        )
    frame["estimated_hours"] = hours.astype(int)

    for row, value in frame["skill_ids"].items():
        ids = [item.strip() for item in value.split(";")]
        if not ids or any(not item for item in ids):
            raise ValueError(f"Invalid skill_ids at row {row}: {value!r}")
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate skill ID in project at row {row}.")
        unknown = sorted(set(ids) - valid_skill_ids)
        if unknown:
            raise ValueError(
                f"Unknown skill ID(s) at row {row}: {', '.join(unknown)}"
            )
        if skill_roles is not None:
            project_role = frame.loc[row, "target_roles"]
            for skill_id in ids:
                skill_role = skill_roles[skill_id]
                compatible = (
                    skill_role == "Both"
                    or project_role == "Both" and skill_role == "Both"
                    or project_role == skill_role
                )
                if not compatible:
                    raise ValueError(
                        f"Skill {skill_id} (role {skill_role!r}) is not "
                        f"compatible with project role {project_role!r} "
                        f"at row {row}."
                    )

    for row, value in frame["prerequisites"].items():
        if not value:
            continue
        ids = [item.strip() for item in value.split(";")]
        if any(not item for item in ids):
            raise ValueError(f"Invalid prerequisites at row {row}: {value!r}")
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate prerequisite at row {row}.")
        unknown = sorted(set(ids) - valid_skill_ids)
        if unknown:
            raise ValueError(
                f"Unknown prerequisite skill ID(s) at row {row}: "
                f"{', '.join(unknown)}"
            )
        if skill_roles is not None:
            project_role = frame.loc[row, "target_roles"]
            for skill_id in ids:
                skill_role = skill_roles[skill_id]
                compatible = (
                    skill_role == "Both"
                    or project_role != "Both" and skill_role == project_role
                )
                if not compatible:
                    raise ValueError(
                        f"Prerequisite {skill_id} (role {skill_role!r}) is "
                        f"not compatible with project role {project_role!r} "
                        f"at row {row}."
                    )

    return frame


def _validate_gap(gap: dict[str, Any], index: int, target_role: str) -> None:
    """Validate required fields from a Phase 4 skill-gap record."""
    if not isinstance(gap, dict):
        raise ValueError(f"Gap record at index {index} must be a dictionary.")

    required = {
        "target_role",
        "skill_id",
        "skill_name",
        "candidate_status",
        "priority_score",
        "market_priority_rank",
        "market_jobs_with_skill",
        "market_relevant_jobs_total",
        "market_evidence_level",
        "market_evidence_status",
        "esco_mapping_status",
        "esco_relationship",
        "esco_label",
        "extraction_incomplete",
    }
    missing = sorted(required - set(gap))
    if missing:
        raise ValueError(
            f"Gap record at index {index} is missing required fields: "
            + ", ".join(missing)
        )

    if gap["target_role"] != target_role:
        raise ValueError(
            f"Gap record at index {index} has target_role "
            f"{gap['target_role']!r}; expected {target_role!r}."
        )

    for field in ("skill_id", "skill_name"):
        if not isinstance(gap[field], str) or not gap[field].strip():
            raise ValueError(
                f"Gap record at index {index} has an invalid {field}."
            )

    if gap["candidate_status"] not in (
        ACTIONABLE_STATUSES | {"verified_skill_present"}
    ):
        raise ValueError(
            f"Unsupported candidate_status at index {index}: "
            f"{gap['candidate_status']!r}"
        )

    priority = _safe_number(gap["priority_score"], default=float("nan"))
    if pd.isna(priority) or not 0 <= priority <= 100:
        raise ValueError(
            f"Invalid priority_score at index {index}: "
            f"{gap['priority_score']!r}"
        )

    rank = gap["market_priority_rank"]
    if rank is not None and not pd.isna(rank):
        number = _safe_number(rank, default=float("nan"))
        if pd.isna(number) or number < 1 or not number.is_integer():
            raise ValueError(
                f"Invalid market_priority_rank at index {index}: {rank!r}"
            )

    for field in ("market_jobs_with_skill", "market_relevant_jobs_total"):
        number = _safe_number(gap[field], default=float("nan"))
        if pd.isna(number) or number < 0:
            raise ValueError(
                f"Invalid {field} at index {index}: {gap[field]!r}"
            )

    _safe_bool(gap["extraction_incomplete"])


def _load_project_catalogue(
    project_path: str | Path,
    valid_skill_ids: set[str],
) -> pd.DataFrame:
    """Load and validate a project catalogue from CSV."""
    path = Path(project_path)
    if not path.is_file():
        raise ValueError(f"Project catalogue does not exist: {path}")
    try:
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    except (OSError, pd.errors.ParserError, UnicodeError) as exc:
        raise ValueError(f"Could not read project catalogue: {path}") from exc
    return _validate_project_catalogue(frame, valid_skill_ids)


def recommend_projects(
    skill_gaps: list[dict[str, Any]],
    target_role: str,
    projects: pd.DataFrame | None = None,
    vocabulary: pd.DataFrame | None = None,
    project_path: str | Path = PROJECT_CATALOGUE_PATH,
    max_hours: int | None = None,
    max_difficulty: str | None = None,
    include_maintenance: bool = False,
) -> list[dict[str, Any]]:
    """Recommend projects for actionable Phase 4 skill gaps.

    Ranking is deterministic and uses relevant gap coverage, observed market
    frequency, role compatibility, and project effort. It is a heuristic,
    not a validated prediction of employability or skill mastery.
    """
    role = _normalise_role(target_role)
    if role not in SUPPORTED_ROLES:
        raise ValueError(f"Unsupported target role: {target_role!r}")

    if not isinstance(skill_gaps, list):
        raise ValueError("skill_gaps must be a list of gap dictionaries.")
    if not isinstance(include_maintenance, bool):
        raise ValueError("include_maintenance must be a boolean.")

    if max_hours is not None:
        if isinstance(max_hours, bool) or not isinstance(max_hours, int) or max_hours <= 0:
            raise ValueError("max_hours must be a positive integer or None.")

    if max_difficulty is not None and max_difficulty not in DIFFICULTY_ORDER:
        raise ValueError(
            "max_difficulty must be Beginner, Intermediate, Advanced, or None."
        )

    for index, gap in enumerate(skill_gaps):
        _validate_gap(gap, index, role)

    if vocabulary is None:
        if not VOCABULARY_PATH.is_file():
            raise ValueError(f"Skill vocabulary does not exist: {VOCABULARY_PATH}")
        try:
            vocabulary = pd.read_csv(VOCABULARY_PATH).fillna("")
        except (OSError, pd.errors.ParserError, UnicodeError) as exc:
            raise ValueError("Could not read the skill vocabulary.") from exc
    if not isinstance(vocabulary, pd.DataFrame):
        raise ValueError("vocabulary must be a pandas DataFrame.")
    missing_vocabulary_columns = {"skill_id", "skill_name", "role"} - set(vocabulary.columns)
    if missing_vocabulary_columns:
        raise ValueError(
            "Skill vocabulary is missing required columns: "
            + ", ".join(sorted(missing_vocabulary_columns))
        )
    vocabulary = vocabulary.copy().fillna("")
    vocabulary["skill_id"] = vocabulary["skill_id"].astype(str).str.strip()
    vocabulary["skill_name"] = vocabulary["skill_name"].astype(str).str.strip()
    vocabulary["role"] = vocabulary["role"].astype(str).str.strip()
    if vocabulary["skill_id"].eq("").any() or vocabulary["skill_id"].duplicated().any():
        raise ValueError("Skill vocabulary contains empty or duplicate skill IDs.")
    if vocabulary["skill_name"].eq("").any():
        raise ValueError("Skill vocabulary contains an empty skill name.")
    if not vocabulary["role"].isin(ALLOWED_PROJECT_ROLES).all():
        raise ValueError("Skill vocabulary contains an unsupported role value.")
    valid_skill_ids = set(vocabulary["skill_id"])
    skill_names = dict(zip(vocabulary["skill_id"], vocabulary["skill_name"]))
    skill_roles = dict(zip(vocabulary["skill_id"], vocabulary["role"]))

    gap_by_id: dict[str, dict[str, Any]] = {}
    for gap in skill_gaps:
        if gap["skill_id"] not in valid_skill_ids:
            raise ValueError(f"Unknown skill_id in gap records: {gap['skill_id']!r}")
        if gap["skill_id"] in gap_by_id:
            raise ValueError(f"Duplicate skill gap for skill_id: {gap['skill_id']!r}")
        gap_by_id[gap["skill_id"]] = gap

    if projects is None:
        project_frame = _load_project_catalogue(project_path, valid_skill_ids)
        project_frame = _validate_project_catalogue(
            project_frame, valid_skill_ids, skill_roles
        )
    else:
        project_frame = _validate_project_catalogue(
            projects, valid_skill_ids, skill_roles
        )

    if max_difficulty is None:
        max_difficulty_rank = DIFFICULTY_ORDER["Advanced"]
    else:
        max_difficulty_rank = DIFFICULTY_ORDER[max_difficulty]

    actionable = {
        skill_id: gap
        for skill_id, gap in gap_by_id.items()
        if gap["candidate_status"] in ACTIONABLE_STATUSES
        or include_maintenance and gap["candidate_status"] == "verified_skill_present"
    }

    recommendations: list[dict[str, Any]] = []
    for _, project in project_frame.iterrows():
        if project["target_roles"] not in {"Both", role}:
            continue
        if int(project["estimated_hours"]) > max_hours if max_hours is not None else False:
            continue
        if DIFFICULTY_ORDER[project["difficulty"]] > max_difficulty_rank:
            continue

        covered_ids = [
            skill_id
            for skill_id in project["skill_ids"].split(";")
            if skill_id in actionable
        ]
        if not covered_ids:
            continue

        covered_gaps = [actionable[skill_id] for skill_id in covered_ids]
        market_supported_gaps = [
            gap
            for gap in covered_gaps
            if gap["market_jobs_with_skill"] > 0
            and gap["market_relevant_jobs_total"] > 0
            and gap["market_evidence_status"] != "no_observed_matches"
        ]
        market_supported_ids = [
            gap["skill_id"] for gap in market_supported_gaps
        ]
        market_unobserved_ids = [
            gap["skill_id"]
            for gap in covered_gaps
            if gap["market_jobs_with_skill"] <= 0
            or gap["market_relevant_jobs_total"] <= 0
            or gap["market_evidence_status"] == "no_observed_matches"
        ]
        mean_market_priority = (
            sum(float(gap["priority_score"]) for gap in market_supported_gaps)
            / len(market_supported_gaps)
            if market_supported_gaps
            else None
        )
        uncertain_ids = [
            gap["skill_id"]
            for gap in covered_gaps
            if gap["candidate_status"] != "potential_gap"
            or gap["extraction_incomplete"]
        ]

        coverage_score = len(covered_ids) / max(len(actionable), 1) * 100
        ranking_score = coverage_score

        explanations = [
            f"Covers {len(covered_ids)} actionable skill gap(s): "
            + ", ".join(
                f"{skill_id} ({skill_names[skill_id]})"
                for skill_id in covered_ids
            )
            + ".",
            (
                f"Role fit: {project['target_roles']}; estimated effort: "
                f"{int(project['estimated_hours'])} hours; difficulty: "
                f"{project['difficulty']}."
            ),
        ]
        if market_supported_ids:
            explanations.append(
                "Observed market evidence exists for: "
                + ", ".join(market_supported_ids)
                + "; this reflects the current dataset only."
            )
        if market_unobserved_ids:
            explanations.append(
                "No usable observed market matches are available for: "
                + ", ".join(market_unobserved_ids)
                + ". This does not mean these skills have no real-world demand."
            )
        if uncertain_ids:
            explanations.append(
                "Review CV evidence before treating these as confirmed gaps: "
                + ", ".join(uncertain_ids)
                + "."
            )
        if project["prerequisites"]:
            explanations.append(
                "Prerequisites are advisory and have not been confirmed: "
                + project["prerequisites"]
                + "."
            )

        recommendations.append(
            {
                "project_id": project["project_id"],
                "project_title": project["project_title"],
                "description": project["description"],
                "target_role": role,
                "project_roles": project["target_roles"],
                "skill_ids": project["skill_ids"].split(";"),
                "covered_skill_ids": covered_ids,
                "covered_skills": [skill_names[item] for item in covered_ids],
                "covered_gap_count": len(covered_ids),
                "total_actionable_gaps": len(actionable),
                "coverage_score": round(coverage_score, 2),
                "mean_market_priority": (
                    round(mean_market_priority, 2)
                    if mean_market_priority is not None
                    else None
                ),
                "market_supported_skill_ids": market_supported_ids,
                "uncertain_skill_ids": uncertain_ids,
                "difficulty": project["difficulty"],
                "estimated_hours": int(project["estimated_hours"]),
                "prerequisites": (
                    project["prerequisites"].split(";")
                    if project["prerequisites"]
                    else []
                ),
                "deliverables": project["deliverables"],
                "evidence_criteria": project["evidence_criteria"],
                "ranking_score": ranking_score,
                "ranking_method": (
                    "Coverage-first ranking: actionable gap count descending; "
                    "market priority is used as a tie-break only when every "
                    "eligible recommendation has comparable observed market "
                    "evidence; then coverage per estimated hour descending, "
                    "estimated hours ascending, and project_id ascending. "
                    "Not an employability prediction."
                ),
                "explanation": " ".join(explanations),
                "evidence_type_for_tracking": "project",
                "initial_verification_status": "unverified",
            }
        )

    market_ranking_enabled = bool(recommendations) and all(
        item["mean_market_priority"] is not None
        for item in recommendations
    )

    for item in recommendations:
        item["market_priority_used_for_ranking"] = market_ranking_enabled
        if not market_ranking_enabled:
            item["ranking_method"] = (
                "Actionable gap count descending; market priority reported "
                "but not used because observed market evidence is incomplete "
                "across eligible recommendations; then coverage per estimated "
                "hour descending, estimated hours ascending, and project_id "
                "ascending. Not an employability prediction."
            )

    recommendations.sort(
        key=lambda item: (
            -item["covered_gap_count"],
            -item["mean_market_priority"] if market_ranking_enabled else 0,
            -(item["covered_gap_count"] / item["estimated_hours"]),
            item["estimated_hours"],
            item["project_id"],
        )
    )
    return recommendations
