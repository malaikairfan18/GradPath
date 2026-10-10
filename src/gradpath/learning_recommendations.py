
"""Explainable learning recommendations for GradPath skill-gap results."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_PATH = PROJECT_ROOT / "data" / "resources" / "learning_resources.csv"

SUPPORTED_ROLES = {"Data Analyst", "Data Scientist"}

REQUIRED_RESOURCE_COLUMNS = {
    "resource_id",
    "skill_id",
    "resource_title",
    "provider",
    "resource_url",
    "resource_type",
    "difficulty",
    "access_type",
    "role",
    "description",
}

ALLOWED_RESOURCE_TYPES = {
    "exercise",
    "tutorial",
    "course",
    "documentation",
}

ALLOWED_DIFFICULTIES = {
    "beginner",
    "intermediate",
    "advanced",
}

ALLOWED_ACCESS_TYPES = {"free", "paid", "freemium"}

ALLOWED_ROLES = {
    "Data Analyst",
    "Data Scientist",
    "Both",
}

RESOURCE_TYPE_ORDER = {
    "exercise": 0,
    "tutorial": 1,
    "course": 2,
    "documentation": 3,
}

DIFFICULTY_ORDER = {
    "beginner": 0,
    "intermediate": 1,
    "advanced": 2,
}


def _safe_number(value: Any, default: float = 0.0) -> float:
    """Convert a value to a finite float, using a default when invalid."""
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return default

    if not pd.notna(number):
        return default

    if number in (float("inf"), float("-inf")):
        return default

    return number


def _safe_rank(value: Any) -> int | None:
    """Convert a valid positive integer market rank; missing ranks sort last."""
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    number = _safe_number(value, default=float("nan"))

    if pd.isna(number) or number < 1 or not number.is_integer():
        return None

    return int(number)


def _safe_bool(value: Any) -> bool:
    """Parse booleans without treating the string 'False' as true."""
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().casefold()

        if normalized in {"true", "1", "yes"}:
            return True

        if normalized in {"false", "0", "no", ""}:
            return False

    if value is None:
        return False

    try:
        if pd.isna(value):
            return False
    except (TypeError, ValueError):
        pass

    raise ValueError(f"Invalid boolean value: {value!r}")


def _validate_gap(gap: dict, index: int) -> None:
    """Validate the minimum fields required from a Phase 4 skill-gap record."""
    if not isinstance(gap, dict):
        raise ValueError(
            f"Gap record at index {index} must be a dictionary."
        )

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
            f"{', '.join(missing)}"
        )

    if gap["target_role"] not in SUPPORTED_ROLES:
        raise ValueError(
            f"Unsupported target role in gap record at index {index}: "
            f"{gap['target_role']!r}"
        )

    for field in ("skill_id", "skill_name", "candidate_status"):
        if not isinstance(gap[field], str) or not gap[field].strip():
            raise ValueError(
                f"Gap record at index {index} has an invalid {field}."
            )

    valid_statuses = {
        "potential_gap",
        "insufficient_evidence",
        "mentioned_unverified",
        "rejected_evidence",
        "verified_skill_present",
    }

    if gap["candidate_status"] not in valid_statuses:
        raise ValueError(
            f"Unsupported candidate_status at index {index}: "
            f"{gap['candidate_status']!r}"
        )

    raw_priority = gap["priority_score"]

    try:
        priority = float(raw_priority)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(
            f"Invalid priority_score in gap record at index {index}: "
            f"{raw_priority!r}"
        ) from exc

    if pd.isna(priority):
        priority = 0.0
    elif not __import__("math").isfinite(priority):
        raise ValueError(
            f"Invalid priority_score in gap record at index {index}: "
            f"{raw_priority!r}"
        )

    gap["priority_score"] = priority

    rank = gap["market_priority_rank"]

    if rank is not None:
        try:
            rank_missing = bool(pd.isna(rank))
        except (TypeError, ValueError):
            rank_missing = False

        if not rank_missing:
            try:
                rank_number = float(rank)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(
                    f"Invalid market_priority_rank in gap record at "
                    f"index {index}: {rank!r}"
                ) from exc

            if (
                not pd.notna(rank_number)
                or rank_number < 1
                or not rank_number.is_integer()
            ):
                raise ValueError(
                    f"Invalid market_priority_rank in gap record at "
                    f"index {index}: {rank!r}"
                )

    for field in (
        "market_jobs_with_skill",
        "market_relevant_jobs_total",
    ):
        number = _safe_number(gap[field], default=float("nan"))

        if pd.isna(number) or number < 0:
            raise ValueError(
                f"Invalid {field} in gap record at index {index}: "
                f"{gap[field]!r}"
            )

    _safe_bool(gap["extraction_incomplete"])


def _validate_resources(resources: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize the learning resource catalogue."""
    if not isinstance(resources, pd.DataFrame):
        raise ValueError("resources must be a pandas DataFrame.")

    missing = sorted(REQUIRED_RESOURCE_COLUMNS - set(resources.columns))

    if missing:
        raise ValueError(
            "Resource catalogue is missing required columns: "
            + ", ".join(missing)
        )

    frame = resources.copy()

    for column in REQUIRED_RESOURCE_COLUMNS:
        frame[column] = frame[column].fillna("").astype(str).str.strip()

    required_nonempty = [
        "resource_id",
        "skill_id",
        "resource_title",
        "provider",
        "resource_url",
        "resource_type",
        "difficulty",
        "access_type",
        "role",
    ]

    for column in required_nonempty:
        empty = frame[column].eq("")

        if empty.any():
            row = frame.index[empty][0]
            raise ValueError(
                f"Resource catalogue contains an empty {column} at row {row}."
            )

    if frame["resource_id"].duplicated().any():
        duplicate = frame.loc[
            frame["resource_id"].duplicated(keep=False),
            "resource_id",
        ].iloc[0]

        raise ValueError(f"Duplicate resource_id: {duplicate!r}")

    # Validate URL structure, not whether the remote page is live.
    for row, value in frame["resource_url"].items():
        parsed = urlparse(value)

        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(
                f"Resource URL must be a valid HTTPS URL at row {row}: "
                f"{value!r}"
            )

    checks = [
        ("resource_type", ALLOWED_RESOURCE_TYPES),
        ("difficulty", ALLOWED_DIFFICULTIES),
        ("access_type", ALLOWED_ACCESS_TYPES),
    ]

    for column, allowed in checks:
        normalized = frame[column].str.casefold()
        invalid = ~normalized.isin(allowed)

        if invalid.any():
            row = frame.index[invalid][0]
            raise ValueError(
                f"Invalid {column} at row {row}: "
                f"{frame.loc[row, column]!r}"
            )

        frame[column] = normalized

    invalid_roles = ~frame["role"].isin(ALLOWED_ROLES)

    if invalid_roles.any():
        row = frame.index[invalid_roles][0]
        raise ValueError(
            f"Invalid role at row {row}: {frame.loc[row, 'role']!r}"
        )

    return frame


def _load_resources(
    resources: pd.DataFrame | None,
) -> pd.DataFrame:
    """Load the default catalogue or validate a supplied catalogue."""
    if resources is None:
        if not RESOURCE_PATH.exists():
            raise FileNotFoundError(
                f"Learning resource catalogue not found: {RESOURCE_PATH}"
            )

        resources = pd.read_csv(
            RESOURCE_PATH,
            dtype=str,
        ).fillna("")

    return _validate_resources(resources)


def _find_resource(
    resources: pd.DataFrame,
    skill_id: str,
    target_role: str,
    action: str,
) -> dict | None:
    """Find a deterministic, role-compatible resource for a skill."""
    compatible = resources[
        (resources["skill_id"] == skill_id)
        & resources["role"].isin([target_role, "Both"])
    ].copy()

    if compatible.empty:
        return None

    # Resource types and difficulty levels define deterministic preferences.
    # The action parameter is reserved for future action-specific filtering.
    compatible["_type_order"] = compatible["resource_type"].map(
        RESOURCE_TYPE_ORDER
    )
    compatible["_difficulty_order"] = compatible["difficulty"].map(
        DIFFICULTY_ORDER
    )

    compatible = compatible.sort_values(
        [
            "_type_order",
            "_difficulty_order",
            "resource_title",
            "resource_id",
        ],
        key=lambda column: (
            column.str.casefold()
            if column.name in {"resource_title", "resource_id"}
            else column
        ),
        kind="stable",
    )

    row = compatible.iloc[0]

    return {
        column: row[column]
        for column in REQUIRED_RESOURCE_COLUMNS
    }


def _build_explanation(
    gap: dict,
    action: str,
    resource: dict | None,
) -> str:
    """Explain candidate, market, and ESCO evidence separately."""
    parts = [
        f"{gap['skill_name']}: recommended action is {action}."
    ]

    status = gap["candidate_status"]

    if status == "potential_gap":
        parts.append(
            "The skill was not found in available candidate evidence; "
            "this is a potential gap, not proof the candidate lacks it."
        )
    elif status == "insufficient_evidence":
        parts.append(
            "CV/profile extraction is incomplete, so investigate the skill "
            "status before treating it as a gap."
        )
    elif status == "mentioned_unverified":
        parts.append(
            "The skill is mentioned but not verified; practice or evidence "
            "can help establish proficiency."
        )
    elif status == "rejected_evidence":
        parts.append(
            "Existing evidence was rejected, so reassess the evidence "
            "before making a learning decision."
        )
    elif status == "verified_skill_present":
        parts.append(
            "The skill is already verified; maintenance is optional."
        )

    market_count = _safe_number(
        gap.get("market_jobs_with_skill"),
        0.0,
    )
    total_count = _safe_number(
        gap.get("market_relevant_jobs_total"),
        0.0,
    )

    parts.append(
        f"Market evidence: {market_count:g} of {total_count:g} relevant "
        f"jobs were observed with this skill "
        f"(evidence level: {gap.get('market_evidence_level', 'unknown')}; "
        f"status: {gap.get('market_evidence_status', 'unknown')}). "
        "This is the collected sample, not the entire job market or a "
        "measure of candidate readiness."
    )

    esco = (
        "ESCO evidence: mapping status "
        f"{gap.get('esco_mapping_status', 'unknown')}, "
        f"relationship {gap.get('esco_relationship', 'unknown')}"
    )

    label = str(gap.get("esco_label", "")).strip()

    if label:
        esco += f", label {label}"

    parts.append(
        esco
        + ". ESCO evidence is kept separate from observed market frequency."
    )

    if resource:
        parts.append(
            f"Suggested resource: {resource['resource_title']} "
            f"({resource['provider']}, {resource['difficulty']})."
        )
    else:
        parts.append(
            "No compatible catalogue resource was available for this action."
        )

    return " ".join(parts)


def _choose_action(
    gap: dict,
    resources: pd.DataFrame,
    target_role: str,
    include_maintenance: bool,
) -> tuple[str, dict | None]:
    """Select an action based on the candidate's evidence status."""
    status = gap["candidate_status"]
    skill_id = gap["skill_id"]

    if status == "potential_gap":
        resource = _find_resource(
            resources,
            skill_id,
            target_role,
            "learn",
        )
        return ("learn", resource) if resource else (None, None)

    if status == "insufficient_evidence":
        return "investigate", None

    if status == "mentioned_unverified":
        resource = _find_resource(
            resources,
            skill_id,
            target_role,
            "practice",
        )
        return ("practice", resource) if resource else ("investigate", None)

    if status == "rejected_evidence":
        return "reassess", None

    if status == "verified_skill_present":
        if not include_maintenance:
            return "maintain", None

        resource = _find_resource(
            resources,
            skill_id,
            target_role,
            "maintain",
        )
        return "maintain", resource

    raise ValueError(f"Unsupported candidate_status: {status!r}")


def recommend_learning_actions(
    skill_gaps: list[dict],
    target_role: str,
    resources: pd.DataFrame | None = None,
    include_maintenance: bool = False,
) -> list[dict]:
    """Convert Phase 4 skill gaps into explainable, role-compatible actions.

    Priority scores provide heuristic ordering only. They do not predict
    readiness, hiring outcomes, or employment probability.
    """
    if target_role not in SUPPORTED_ROLES:
        raise ValueError(
            f"Unsupported target role: {target_role!r}. "
            f"Supported roles: {', '.join(sorted(SUPPORTED_ROLES))}."
        )

    if not isinstance(skill_gaps, list):
        raise ValueError("skill_gaps must be a list of dictionaries.")

    if not isinstance(include_maintenance, bool):
        raise ValueError("include_maintenance must be a boolean.")

    resource_frame = _load_resources(resources)
    output = []

    for index, gap in enumerate(skill_gaps):
        _validate_gap(gap, index)

        if gap["target_role"] != target_role:
            raise ValueError(
                f"Gap record at index {index} targets "
                f"{gap['target_role']!r}, not requested role "
                f"{target_role!r}."
            )

        # Verified skills are omitted by default. Maintenance is opt-in.
        if (
            gap["candidate_status"] == "verified_skill_present"
            and not include_maintenance
        ):
            continue

        action, resource = _choose_action(
            gap,
            resource_frame,
            target_role,
            include_maintenance,
        )
        if action is None:
            continue

        rank = _safe_rank(gap.get("market_priority_rank"))
        priority = _safe_number(gap.get("priority_score"), 0.0)
        jobs = _safe_number(gap.get("market_jobs_with_skill"), 0.0)
        total = _safe_number(gap.get("market_relevant_jobs_total"), 0.0)
        incomplete = _safe_bool(gap.get("extraction_incomplete"))

        output.append(
            {
                "target_role": target_role,
                "skill_id": gap["skill_id"],
                "skill_name": gap["skill_name"],
                "candidate_status": gap["candidate_status"],
                "recommended_action": action,
                "priority_score": priority,
                "market_priority_rank": rank,
                "market_jobs_with_skill": jobs,
                "market_relevant_jobs_total": total,
                "market_evidence_level": gap["market_evidence_level"],
                "market_evidence_status": gap["market_evidence_status"],
                "esco_mapping_status": gap["esco_mapping_status"],
                "esco_relationship": gap["esco_relationship"],
                "esco_label": gap["esco_label"],
                "extraction_incomplete": incomplete,
                "explanation": _build_explanation(
                    gap,
                    action,
                    resource,
                ),
                "resource_id": resource["resource_id"] if resource else None,
                "resource_title": (
                    resource["resource_title"] if resource else None
                ),
                "provider": resource["provider"] if resource else None,
                "resource_url": resource["resource_url"] if resource else None,
                "resource_type": (
                    resource["resource_type"] if resource else None
                ),
                "difficulty": resource["difficulty"] if resource else None,
                "access_type": resource["access_type"] if resource else None,
                "resource_description": (
                    resource["description"] if resource else None
                ),
            }
        )

    output.sort(
        key=lambda item: (
            -item["priority_score"],
            (
                item["market_priority_rank"]
                if item["market_priority_rank"] is not None
                else 10**9
            ),
            item["skill_id"],
        )
    )

    return output
