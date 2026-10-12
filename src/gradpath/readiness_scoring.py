"""Read-only, explainable skill-coverage reporting for GradPath Phase 9."""

import csv
import math
import sqlite3
from collections import defaultdict
from contextlib import closing
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = (
    PROJECT_ROOT / "data" / "processed" / "gradpath_progress.db"
)
DEFAULT_VOCABULARY_PATH = (
    PROJECT_ROOT / "data" / "processed" / "initial_skill_vocabulary.csv"
)

SUPPORTED_SCHEMA_VERSIONS = {1, 2}
SUPPORTED_ROLES = {"Data Analyst", "Data Scientist"}
REQUIRED_VOCABULARY_COLUMNS = {"skill_id", "skill_name", "role"}
REQUIRED_TABLES = {
    "schema_metadata",
    "learning_activities",
    "assessment_attempts",
    "skill_evidence",
}
ASSESSMENT_TYPES = {"quiz", "coding_exercise", "project_evaluation", "other"}
EVIDENCE_STATUSES = {"unverified", "assessed", "verified", "rejected"}


def _load_role_skills(
    target_role: str,
    vocabulary_path: str | Path,
) -> list[dict[str, str]]:
    """Load the canonical skills eligible for one target role."""
    path = Path(vocabulary_path)
    if not path.is_file():
        raise FileNotFoundError(f"Skill vocabulary not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_VOCABULARY_COLUMNS - columns
        if missing:
            raise ValueError(
                f"Skill vocabulary is missing columns: {sorted(missing)}"
            )

        rows = list(reader)

    seen_ids: set[str] = set()
    eligible: list[dict[str, str]] = []

    for row in rows:
        skill_id = (row.get("skill_id") or "").strip()
        skill_name = (row.get("skill_name") or "").strip()
        role = (row.get("role") or "").strip()

        if not skill_id or not skill_name or not role:
            raise ValueError(
                "Skill vocabulary contains a blank skill ID, name, or role."
            )
        if skill_id in seen_ids:
            raise ValueError(
                f"Skill vocabulary contains duplicate skill ID: {skill_id}"
            )
        seen_ids.add(skill_id)

        if role not in {"Both", *SUPPORTED_ROLES}:
            raise ValueError(
                f"Unsupported role label {role!r} for skill {skill_id}."
            )

        if role in {"Both", target_role}:
            eligible.append(
                {"skill_id": skill_id, "skill_name": skill_name, "role": role}
            )

    # An empty eligible set is valid input; the caller will report
    # that coverage cannot be calculated for this role.
    return eligible


def _open_read_only(database_path: str | Path) -> sqlite3.Connection:
    """Open an existing SQLite database without permitting writes."""
    path = Path(database_path)
    if not path.is_file():
        raise FileNotFoundError(f"Progress database not found: {path}")

    connection = sqlite3.connect(
        path.resolve().as_uri() + "?mode=ro",
        uri=True,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def _validate_database(connection: sqlite3.Connection) -> int:
    """Validate the existing schema version and required Phase 6 tables."""
    tables = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    missing = REQUIRED_TABLES - tables
    if missing:
        raise ValueError(
            f"Progress database is missing required tables: {sorted(missing)}"
        )

    metadata = connection.execute(
        """
        SELECT value
        FROM schema_metadata
        WHERE key = 'schema_version'
        """
    ).fetchone()

    if metadata is None:
        raise ValueError("Database schema version is missing.")

    try:
        version = int(metadata["value"])
    except (TypeError, ValueError) as error:
        raise ValueError("Database schema version is invalid.") from error

    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(
            f"Unsupported database schema version: {version}. "
            f"Supported versions are {sorted(SUPPORTED_SCHEMA_VERSIONS)}."
        )

    return version


def _empty_assessment_group() -> dict[str, Any]:
    return {
        "attempt_count": 0,
        "scored_attempt_count": 0,
        "scoreless_attempt_count": 0,
        "invalid_score_count": 0,
        "average_score_percent": None,
    }


def _summarize_assessments(
    attempts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarize scores within assessment types, never across types."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for attempt in attempts:
        grouped[attempt["assessment_type"]].append(attempt)

    result: dict[str, Any] = {}
    for assessment_type in sorted(ASSESSMENT_TYPES):
        items = grouped.get(assessment_type, [])
        percentages: list[float] = []
        scoreless = 0
        invalid = 0

        for item in items:
            score = item["score"]
            maximum = item["max_score"]

            if score is None and maximum is None:
                scoreless += 1
                continue

            if score is None or maximum is None:
                invalid += 1
                continue

            try:
                score_value = float(score)
                max_value = float(maximum)
            except (TypeError, ValueError):
                invalid += 1
                continue

            if (
                not math.isfinite(score_value)
                or not math.isfinite(max_value)
                or max_value <= 0
                or score_value < 0
                or score_value > max_value
            ):
                invalid += 1
                continue

            percentages.append(score_value / max_value * 100.0)

        result[assessment_type] = {
            "attempt_count": len(items),
            "scored_attempt_count": len(percentages),
            "scoreless_attempt_count": scoreless,
            "invalid_score_count": invalid,
            "average_score_percent": (
                round(sum(percentages) / len(percentages), 2)
                if percentages else None
            ),
        }

    return result


def score_readiness(
    candidate_id: str,
    target_role: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
    vocabulary_path: str | Path = DEFAULT_VOCABULARY_PATH,
) -> dict[str, Any]:
    """Report verified skill coverage and role-attributed assessments.

    The coverage metric is not a hiring probability or a complete measure
    of job readiness. Only canonical role skills with verified evidence
    and no rejected-evidence conflict count in its numerator.
    This function does not initialize or modify the database.
    """
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string.")
    candidate_id = candidate_id.strip()

    if target_role not in SUPPORTED_ROLES:
        raise ValueError(
            f"Unsupported target_role: {target_role!r}. "
            f"Choose one of {sorted(SUPPORTED_ROLES)}."
        )

    eligible_skills = _load_role_skills(target_role, vocabulary_path)
    skill_ids = {skill["skill_id"] for skill in eligible_skills}

    with closing(_open_read_only(database_path)) as connection:
        schema_version = _validate_database(connection)

        evidence_rows = connection.execute(
            """
            SELECT skill_id, verification_status
            FROM skill_evidence
            WHERE candidate_id = ?
            """,
            (candidate_id,),
        ).fetchall()

        attempt_rows = connection.execute(
            """
            SELECT
                a.attempt_id,
                a.skill_id,
                a.assessment_type,
                a.score,
                a.max_score,
                a.activity_id,
                l.candidate_id AS activity_candidate_id,
                l.skill_id AS activity_skill_id,
                l.target_role AS activity_target_role
            FROM assessment_attempts AS a
            LEFT JOIN learning_activities AS l
                ON l.activity_id = a.activity_id
            WHERE a.candidate_id = ?
            ORDER BY a.attempt_id
            """,
            (candidate_id,),
        ).fetchall()

    statuses_by_skill: dict[str, set[str]] = defaultdict(set)
    for row in evidence_rows:
        status = row["verification_status"]
        if status not in EVIDENCE_STATUSES:
            raise ValueError(
                f"Database contains unsupported evidence status: {status!r}."
            )
        if row["skill_id"] in skill_ids:
            statuses_by_skill[row["skill_id"]].add(status)

    skill_details: list[dict[str, Any]] = []
    verified_count = 0
    conflict_count = 0

    for skill in eligible_skills:
        statuses = statuses_by_skill.get(skill["skill_id"], set())
        has_verified = "verified" in statuses
        has_rejected = "rejected" in statuses
        conflict = has_verified and has_rejected

        if conflict:
            coverage_status = "conflicting_evidence"
            conflict_count += 1
        elif has_verified:
            coverage_status = "verified"
            verified_count += 1
        elif statuses:
            coverage_status = "evidence_not_verified"
        else:
            coverage_status = "no_recorded_evidence"

        skill_details.append({
            "skill_id": skill["skill_id"],
            "skill_name": skill["skill_name"],
            "vocabulary_role": skill["role"],
            "evidence_statuses": sorted(statuses),
            "coverage_status": coverage_status,
            "counts_toward_coverage": coverage_status == "verified",
        })

    denominator = len(eligible_skills)
    coverage_percent = (
        round(verified_count / denominator * 100.0, 2)
        if denominator > 0
        else None
    )
    coverage_calculation_status = (
        "calculated" if denominator > 0 else "no_eligible_skills"
    )

    role_attempts: dict[str, list[dict[str, Any]]] = {
        role: [] for role in sorted(SUPPORTED_ROLES)
    }
    unattributed_attempts: list[dict[str, Any]] = []

    for row in attempt_rows:
        attempt = dict(row)
        activity_matches = (
            attempt["activity_id"] is not None
            and attempt["activity_candidate_id"] == candidate_id
            and attempt["activity_skill_id"] == attempt["skill_id"]
            and attempt["activity_target_role"] in SUPPORTED_ROLES
        )

        if activity_matches:
            role_attempts[attempt["activity_target_role"]].append(attempt)
        else:
            unattributed_attempts.append(attempt)

    return {
        "candidate_id": candidate_id,
        "target_role": target_role,
        "metric_name": "Verified Skill Coverage",
        "coverage_percent": coverage_percent,
        "coverage_calculation_status": coverage_calculation_status,
        "verified_skill_count": verified_count,
        "eligible_skill_count": denominator,
        "evidence_conflict_count": conflict_count,
        "coverage_status_counts": {
            status: sum(
                detail["coverage_status"] == status
                for detail in skill_details
            )
            for status in (
                "verified",
                "conflicting_evidence",
                "evidence_not_verified",
                "no_recorded_evidence",
            )
        },
        "skills": skill_details,
        "assessments": {
            "target_role": target_role,
            "by_type": _summarize_assessments(role_attempts[target_role]),
            "unattributed": {
                "attempt_count": len(unattributed_attempts),
                "by_type": _summarize_assessments(unattributed_attempts),
            },
            "other_role_attempt_count": sum(
                len(items)
                for role, items in role_attempts.items()
                if role != target_role
            ),
        },
        "limitations": [
            "Coverage describes only the current canonical skill vocabulary.",
            "Missing evidence does not prove that a candidate lacks a skill.",
            "CV mentions, course completion, and project completion do not "
            "automatically verify skills.",
            "Conflicting verified and rejected evidence is excluded until "
            "the conflict is resolved.",
            "Assessment averages are reported separately by assessment type.",
            "Assessments without a valid role-linked learning activity are "
            "reported as unattributed.",
            "This metric is not a probability of hiring or a full measure "
            "of job readiness.",
        ],
        "database_schema_version": schema_version,
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Report GradPath verified skill coverage."
    )
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument(
        "--target-role",
        required=True,
        choices=sorted(SUPPORTED_ROLES),
    )
    parser.add_argument(
        "--database",
        default=str(DEFAULT_DATABASE_PATH),
    )
    parser.add_argument(
        "--vocabulary",
        default=str(DEFAULT_VOCABULARY_PATH),
    )
    arguments = parser.parse_args()

    report = score_readiness(
        candidate_id=arguments.candidate_id,
        target_role=arguments.target_role,
        database_path=arguments.database,
        vocabulary_path=arguments.vocabulary,
    )
    print(json.dumps(report, indent=2))
