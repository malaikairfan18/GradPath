
"""SQLite persistence for GradPath learning progress."""

from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from contextlib import closing

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = (
    PROJECT_ROOT / "data" / "processed" / "gradpath_progress.db"
)
RESOURCE_PATH = PROJECT_ROOT / "data" / "resources" / "learning_resources.csv"

SUPPORTED_ROLES = {"Data Analyst", "Data Scientist"}

ACTIVITY_STATUSES = {
    "not_started",
    "in_progress",
    "completed",
    "abandoned",
}

ASSESSMENT_TYPES = {
    "quiz",
    "coding_exercise",
    "project_evaluation",
    "other",
}

EVIDENCE_TYPES = {
    "assessment",
    "project",
    "certification",
    "portfolio",
    "other",
}

VERIFICATION_STATUSES = {
    "unverified",
    "assessed",
    "verified",
    "rejected",
}


def _utc_now() -> str:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _connect(database_path: str | Path) -> sqlite3.Connection:
    """Open a SQLite connection with foreign-key enforcement enabled."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _load_resource_catalogue(
    resource_path: str | Path = RESOURCE_PATH,
) -> pd.DataFrame:
    """Load and minimally validate the existing learning resource catalogue."""
    path = Path(resource_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Learning resource catalogue not found: {path}"
        )

    resources = pd.read_csv(path, dtype=str).fillna("")

    required = {
        "resource_id",
        "skill_id",
        "resource_title",
        "role",
    }
    missing = sorted(required - set(resources.columns))

    if missing:
        raise ValueError(
            "Resource catalogue is missing columns: "
            + ", ".join(missing)
        )

    for column in required:
        resources[column] = resources[column].astype(str).str.strip()

    for column in ("resource_id", "skill_id", "resource_title", "role"):
        if resources[column].eq("").any():
            raise ValueError(
                f"Resource catalogue contains an empty {column}."
            )

    if resources["resource_id"].duplicated().any():
        raise ValueError("Resource catalogue contains duplicate resource IDs.")

    if not resources["role"].isin(
        {"Both", *SUPPORTED_ROLES}
    ).all():
        raise ValueError("Resource catalogue contains an unsupported role.")

    return resources


def _validate_resource_assignment(
    resource_id: str,
    skill_id: str,
    target_role: str,
    resource_path: str | Path = RESOURCE_PATH,
) -> dict[str, str]:
    """Validate a resource, its skill, and its compatibility with a role."""
    if target_role not in SUPPORTED_ROLES:
        raise ValueError(
            f"Unsupported target role: {target_role!r}. "
            f"Supported roles: {', '.join(sorted(SUPPORTED_ROLES))}."
        )

    if not isinstance(resource_id, str) or not resource_id.strip():
        raise ValueError("resource_id must be a non-empty string.")

    if not isinstance(skill_id, str) or not skill_id.strip():
        raise ValueError("skill_id must be a non-empty string.")

    resources = _load_resource_catalogue(resource_path)
    matches = resources.loc[resources["resource_id"] == resource_id]

    if matches.empty:
        raise ValueError(f"Unknown resource_id: {resource_id!r}")

    resource = matches.iloc[0]

    if resource["skill_id"] != skill_id:
        raise ValueError(
            f"Resource {resource_id!r} belongs to skill "
            f"{resource['skill_id']!r}, not {skill_id!r}."
        )

    if resource["role"] not in {target_role, "Both"}:
        raise ValueError(
            f"Resource {resource_id!r} is not compatible with "
            f"target role {target_role!r}."
        )

    return {
        "resource_id": resource["resource_id"],
        "skill_id": resource["skill_id"],
        "resource_title": resource["resource_title"],
        "role": resource["role"],
    }


def assign_learning_activity(
    candidate_id: str,
    resource_id: str,
    skill_id: str,
    target_role: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
    resource_path: str | Path = RESOURCE_PATH,
) -> dict[str, Any]:
    """Assign a validated learning resource to a candidate."""
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string.")

    resource = validate_resource_assignment(
        resource_id=resource_id,
        skill_id=skill_id,
        target_role=target_role,
        resource_path=resource_path,
    )

    now = _utc_now()

    with closing(_connect(database_path)) as connection:
        try:
            connection.execute("BEGIN")

            cursor = connection.execute(
                """
                INSERT INTO learning_activities (
                    candidate_id,
                    resource_id,
                    skill_id,
                    target_role,
                    status,
                    progress_percent,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, 'not_started', 0, ?, ?)
                """,
                (
                    candidate_id.strip(),
                    resource["resource_id"],
                    resource["skill_id"],
                    target_role,
                    now,
                    now,
                ),
            )

            activity_id = cursor.lastrowid

            connection.execute(
                """
                INSERT INTO progress_events (
                    activity_id,
                    event_type,
                    previous_status,
                    new_status,
                    progress_percent,
                    occurred_at,
                    details_json
                )
                VALUES (?, 'assigned', NULL, 'not_started', 0, ?, ?)
                """,
                (
                    activity_id,
                    now,
                    json.dumps({
                        "resource_title": resource["resource_title"],
                        "target_role": target_role,
                    }),
                ),
            )

            connection.commit()

        except sqlite3.IntegrityError as error:
            connection.rollback()
            if "UNIQUE constraint failed" in str(error):
                raise ValueError(
                    "This learning resource is already assigned "
                    "to this candidate for this target role."
                ) from error
            raise

        except Exception:
            connection.rollback()
            raise

        row = connection.execute(
            """
            SELECT *
            FROM learning_activities
            WHERE activity_id = ?
            """,
            (activity_id,),
        ).fetchone()

        return dict(row)


def update_learning_progress(
    activity_id: int,
    progress_percent: int,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, Any]:
    """Update activity progress and record the change in event history."""
    if (
        isinstance(progress_percent, bool)
        or not isinstance(progress_percent, int)
        or not 0 <= progress_percent <= 100
    ):
        raise ValueError("progress_percent must be an integer from 0 to 100.")

    now = _utc_now()

    with closing(_connect(database_path)) as connection:
        try:
            connection.execute("BEGIN")

            activity = connection.execute(
                """
                SELECT *
                FROM learning_activities
                WHERE activity_id = ?
                """,
                (activity_id,),
            ).fetchone()

            if activity is None:
                raise ValueError(
                    f"Learning activity not found: {activity_id}"
                )

            previous_status = activity["status"]
            previous_progress = activity["progress_percent"]

            if previous_status == "abandoned":
                raise ValueError(
                    "Cannot update progress for an abandoned activity."
                )

            if previous_status == "completed" and progress_percent < 100:
                raise ValueError(
                    "A completed activity cannot be moved below 100%."
                )

            if progress_percent == 100:
                new_status = "completed"
            elif progress_percent > 0:
                new_status = "in_progress"
            else:
                new_status = "not_started"

            started_at = activity["started_at"]
            completed_at = activity["completed_at"]

            if progress_percent > 0 and started_at is None:
                started_at = now

            if new_status == "completed":
                completed_at = completed_at or now
            else:
                completed_at = None

            connection.execute(
                """
                UPDATE learning_activities
                SET status = ?,
                    progress_percent = ?,
                    started_at = ?,
                    completed_at = ?,
                    updated_at = ?
                WHERE activity_id = ?
                """,
                (
                    new_status,
                    progress_percent,
                    started_at,
                    completed_at,
                    now,
                    activity_id,
                ),
            )

            if (
                new_status != previous_status
                or progress_percent != previous_progress
            ):
                connection.execute(
                    """
                    INSERT INTO progress_events (
                        activity_id,
                        event_type,
                        previous_status,
                        new_status,
                        progress_percent,
                        occurred_at,
                        details_json
                    )
                    VALUES (?, 'progress_updated', ?, ?, ?, ?, ?)
                    """,
                    (
                        activity_id,
                        previous_status,
                        new_status,
                        progress_percent,
                        now,
                        json.dumps({
                            "previous_progress_percent": previous_progress,
                        }),
                    ),
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        updated = connection.execute(
            """
            SELECT *
            FROM learning_activities
            WHERE activity_id = ?
            """,
            (activity_id,),
        ).fetchone()

        return dict(updated)


def initialize_database(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> None:
    """Create the Phase 6 schema if it does not already exist."""
    schema = """
    CREATE TABLE IF NOT EXISTS learning_activities (
        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT NOT NULL CHECK (length(trim(candidate_id)) > 0),
        resource_id TEXT NOT NULL CHECK (length(trim(resource_id)) > 0),
        skill_id TEXT NOT NULL CHECK (length(trim(skill_id)) > 0),
        target_role TEXT NOT NULL
            CHECK (target_role IN ('Data Analyst', 'Data Scientist')),
        status TEXT NOT NULL DEFAULT 'not_started'
            CHECK (status IN (
                'not_started', 'in_progress', 'completed', 'abandoned'
            )),
        progress_percent INTEGER NOT NULL DEFAULT 0
            CHECK (progress_percent BETWEEN 0 AND 100),
        started_at TEXT,
        completed_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE (candidate_id, resource_id, target_role)
    );

    CREATE TABLE IF NOT EXISTS progress_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_id INTEGER NOT NULL,
        event_type TEXT NOT NULL,
        previous_status TEXT,
        new_status TEXT NOT NULL,
        progress_percent INTEGER NOT NULL
            CHECK (progress_percent BETWEEN 0 AND 100),
        occurred_at TEXT NOT NULL,
        details_json TEXT,
        FOREIGN KEY (activity_id)
            REFERENCES learning_activities(activity_id)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS assessment_attempts (
        attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT NOT NULL CHECK (length(trim(candidate_id)) > 0),
        activity_id INTEGER,
        skill_id TEXT NOT NULL CHECK (length(trim(skill_id)) > 0),
        assessment_type TEXT NOT NULL
            CHECK (assessment_type IN (
                'quiz', 'coding_exercise', 'project_evaluation', 'other'
            )),
        score REAL,
        max_score REAL,
        passed INTEGER CHECK (passed IN (0, 1) OR passed IS NULL),
        attempted_at TEXT NOT NULL,
        assessment_metadata_json TEXT,
        CHECK (
            (score IS NULL AND max_score IS NULL)
            OR
            (score IS NOT NULL AND max_score IS NOT NULL
                AND max_score > 0 AND score >= 0 AND score <= max_score)
        ),
        FOREIGN KEY (activity_id)
            REFERENCES learning_activities(activity_id)
            ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS skill_evidence (
        evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT NOT NULL CHECK (length(trim(candidate_id)) > 0),
        skill_id TEXT NOT NULL CHECK (length(trim(skill_id)) > 0),
        evidence_type TEXT NOT NULL
            CHECK (evidence_type IN (
                'assessment', 'project', 'certification', 'portfolio', 'other'
            )),
        source_id TEXT,
        verification_status TEXT NOT NULL DEFAULT 'unverified'
            CHECK (verification_status IN (
                'unverified', 'assessed', 'verified', 'rejected'
            )),
        proficiency_level TEXT,
        recorded_at TEXT NOT NULL,
        explanation TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_activities_candidate
        ON learning_activities(candidate_id);

    CREATE INDEX IF NOT EXISTS idx_activities_candidate_role
        ON learning_activities(candidate_id, target_role);

    CREATE INDEX IF NOT EXISTS idx_events_activity_time
        ON progress_events(activity_id, occurred_at);

    CREATE INDEX IF NOT EXISTS idx_attempts_candidate_skill
        ON assessment_attempts(candidate_id, skill_id, attempted_at);

    CREATE INDEX IF NOT EXISTS idx_evidence_candidate_skill
        ON skill_evidence(candidate_id, skill_id, recorded_at);
    """

    with closing(_connect(database_path)) as connection:
        connection.executescript(schema)
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO schema_metadata (key, value)
            VALUES ('schema_version', '1')
            ON CONFLICT(key) DO NOTHING
            """
        )
        connection.commit()

        
def validate_resource_assignment(
    resource_id: str,
    skill_id: str,
    target_role: str,
    resource_path: str | Path = RESOURCE_PATH,
) -> dict[str, str]:
    """Public wrapper for learning resource assignment validation."""
    return _validate_resource_assignment(
        resource_id=resource_id,
        skill_id=skill_id,
        target_role=target_role,
        resource_path=resource_path,
    )


def record_assessment_attempt(
    candidate_id: str,
    skill_id: str,
    assessment_type: str,
    score: float | None = None,
    max_score: float | None = None,
    passed: bool | None = None,
    activity_id: int | None = None,
    assessment_metadata: dict[str, Any] | None = None,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, Any]:
    """Record one assessment attempt without automatically verifying skills."""
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string.")

    if not isinstance(skill_id, str) or not skill_id.strip():
        raise ValueError("skill_id must be a non-empty string.")

    if assessment_type not in ASSESSMENT_TYPES:
        raise ValueError(
            f"Unsupported assessment_type: {assessment_type!r}."
        )

    if passed is not None and not isinstance(passed, bool):
        raise ValueError("passed must be True, False, or None.")

    if (score is None) != (max_score is None):
        raise ValueError(
            "score and max_score must either both be provided or both be None."
        )

    if score is not None:
        if isinstance(score, bool) or isinstance(max_score, bool):
            raise ValueError("Scores must be numeric, not boolean.")

        try:
            score = float(score)
            max_score = float(max_score)
        except (TypeError, ValueError) as error:
            raise ValueError("Scores must be numeric.") from error

        if (
            not math.isfinite(score)
            or not math.isfinite(max_score)
            or max_score <= 0
            or score < 0
            or score > max_score
        ):
            raise ValueError(
                "Scores must be finite, with 0 <= score <= max_score "
                "and max_score > 0."
            )

    if assessment_metadata is not None:
        if not isinstance(assessment_metadata, dict):
            raise ValueError("assessment_metadata must be a dictionary.")
        try:
            metadata_json = json.dumps(assessment_metadata)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "assessment_metadata must contain JSON-serializable values."
            ) from error
    else:
        metadata_json = None

    now = _utc_now()

    with closing(_connect(database_path)) as connection:
        try:
            connection.execute("BEGIN")

            if activity_id is not None:
                activity = connection.execute(
                    """
                    SELECT candidate_id, skill_id
                    FROM learning_activities
                    WHERE activity_id = ?
                    """,
                    (activity_id,),
                ).fetchone()

                if activity is None:
                    raise ValueError(
                        f"Learning activity not found: {activity_id}"
                    )

                if (
                    activity["candidate_id"] != candidate_id.strip()
                    or activity["skill_id"] != skill_id.strip()
                ):
                    raise ValueError(
                        "The activity must belong to the same candidate "
                        "and skill as the assessment attempt."
                    )

            cursor = connection.execute(
                """
                INSERT INTO assessment_attempts (
                    candidate_id,
                    activity_id,
                    skill_id,
                    assessment_type,
                    score,
                    max_score,
                    passed,
                    attempted_at,
                    assessment_metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate_id.strip(),
                    activity_id,
                    skill_id.strip(),
                    assessment_type,
                    score,
                    max_score,
                    None if passed is None else int(passed),
                    now,
                    metadata_json,
                ),
            )

            attempt_id = cursor.lastrowid
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        row = connection.execute(
            """
            SELECT *
            FROM assessment_attempts
            WHERE attempt_id = ?
            """,
            (attempt_id,),
        ).fetchone()

        return dict(row)


def record_skill_evidence(
    candidate_id: str,
    skill_id: str,
    evidence_type: str,
    source_id: str | None = None,
    verification_status: str = "unverified",
    proficiency_level: str | None = None,
    explanation: str | None = None,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, Any]:
    """Record skill evidence without assuming that it is verified."""
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string.")

    if not isinstance(skill_id, str) or not skill_id.strip():
        raise ValueError("skill_id must be a non-empty string.")

    if evidence_type not in EVIDENCE_TYPES:
        raise ValueError(
            f"Unsupported evidence_type: {evidence_type!r}."
        )

    if verification_status not in VERIFICATION_STATUSES:
        raise ValueError(
            f"Unsupported verification_status: {verification_status!r}."
        )

    optional_fields = {
        "source_id": source_id,
        "proficiency_level": proficiency_level,
        "explanation": explanation,
    }
    for field_name, value in optional_fields.items():
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string or None.")

    now = _utc_now()

    with closing(_connect(database_path)) as connection:
        cursor = connection.execute(
            """
            INSERT INTO skill_evidence (
                candidate_id,
                skill_id,
                evidence_type,
                source_id,
                verification_status,
                proficiency_level,
                recorded_at,
                explanation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate_id.strip(),
                skill_id.strip(),
                evidence_type,
                source_id,
                verification_status,
                proficiency_level,
                now,
                explanation,
            ),
        )
        evidence_id = cursor.lastrowid
        connection.commit()
        row = connection.execute(
            """
            SELECT *
            FROM skill_evidence
            WHERE evidence_id = ?
            """,
            (evidence_id,),
        ).fetchone()

        return dict(row)


def get_learning_progress_summary(
    candidate_id: str,
    target_role: str | None = None,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, Any]:
    """Summarize learning activity and evidence counts for a candidate."""
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string.")

    if target_role is not None and target_role not in SUPPORTED_ROLES:
        raise ValueError(
            f"Unsupported target_role: {target_role!r}."
        )

    with closing(_connect(database_path)) as connection:
        parameters: list[Any] = [candidate_id.strip()]
        role_filter = ""

        if target_role is not None:
            role_filter = " AND target_role = ?"
            parameters.append(target_role)

        activity_summary = connection.execute(
            f"""
            SELECT
                COUNT(*) AS total_activities,
                SUM(CASE WHEN status = 'not_started' THEN 1 ELSE 0 END)
                    AS not_started,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END)
                    AS in_progress,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)
                    AS completed,
                SUM(CASE WHEN status = 'abandoned' THEN 1 ELSE 0 END)
                    AS abandoned,
                COALESCE(AVG(progress_percent), 0) AS average_progress_percent
            FROM learning_activities
            WHERE candidate_id = ? {role_filter}
            """,
            parameters,
        ).fetchone()

        evidence_summary = connection.execute(
            """
            SELECT
                COUNT(*) AS total_evidence_records,
                SUM(
                    CASE WHEN verification_status = 'verified'
                    THEN 1 ELSE 0 END
                ) AS verified_evidence_records,
                COUNT(DISTINCT CASE
                    WHEN verification_status = 'verified' THEN skill_id
                END) AS skills_with_verified_evidence
            FROM skill_evidence
            WHERE candidate_id = ?
            """,
            (candidate_id.strip(),),
        ).fetchone()

        assessment_summary = connection.execute(
            """
            SELECT
                COUNT(*) AS total_assessment_attempts,
                COUNT(DISTINCT skill_id) AS skills_assessed,
                AVG(
                    CASE
                        WHEN score IS NOT NULL AND max_score > 0
                        THEN score * 100.0 / max_score
                    END
                ) AS average_assessment_score_percent
            FROM assessment_attempts
            WHERE candidate_id = ?
            """,
            (candidate_id.strip(),),
        ).fetchone()

        return {
            "candidate_id": candidate_id.strip(),
            "target_role": target_role,
            "learning_activities": {
                "total": activity_summary["total_activities"],
                "not_started": activity_summary["not_started"] or 0,
                "in_progress": activity_summary["in_progress"] or 0,
                "completed": activity_summary["completed"] or 0,
                "abandoned": activity_summary["abandoned"] or 0,
                "average_progress_percent": round(
                    activity_summary["average_progress_percent"], 2
                ),
            },
            "assessments": {
                "total_attempts": assessment_summary["total_assessment_attempts"],
                "skills_assessed": assessment_summary["skills_assessed"],
                "average_score_percent": (
                    round(
                        assessment_summary[
                            "average_assessment_score_percent"
                        ],
                        2,
                    )
                    if assessment_summary[
                        "average_assessment_score_percent"
                    ] is not None
                    else None
                ),
            },
            "skill_evidence": {
                "total_records": evidence_summary["total_evidence_records"],
                "verified_records": (
                    evidence_summary["verified_evidence_records"] or 0
                ),
                "skills_with_verified_evidence": (
                    evidence_summary["skills_with_verified_evidence"] or 0
                ),
            },
        }
