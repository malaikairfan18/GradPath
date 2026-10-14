
"""Project assignment and progress-history storage for GradPath."""

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from gradpath.progress_tracker import (
    DEFAULT_DATABASE_PATH,
    initialize_database,
    record_skill_evidence,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_CATALOGUE_PATH = (
    PROJECT_ROOT / "data" / "resources" / "project_catalogue.csv"
)

SKILL_VOCABULARY_PATH = (
    PROJECT_ROOT / "data" / "processed" / "initial_skill_vocabulary.csv"
)
SUPPORTED_SCHEMA_VERSION = 2

PROJECT_STATUSES = {
    "not_started",
    "in_progress",
    "completed",
    "abandoned",
}

ALLOWED_STATUS_TRANSITIONS = {
    "not_started": {"in_progress", "abandoned"},
    "in_progress": {"completed", "abandoned"},
    "completed": set(),
    "abandoned": set(),
}


def _utc_now() -> str:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _connect(database_path: str | Path) -> sqlite3.Connection:
    """Connect to the database and enable foreign-key enforcement."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _load_project_catalogue(
    project_path: str | Path = PROJECT_CATALOGUE_PATH,
) -> pd.DataFrame:
    """Load and minimally validate the canonical project catalogue."""
    path = Path(project_path)

    if not path.is_file():
        raise FileNotFoundError(f"Project catalogue not found: {path}")

    projects = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
    )

    required_columns = {
        "project_id",
        "project_title",
        "target_roles",
        "skill_ids",
    }

    missing = required_columns - set(projects.columns)
    if missing:
        raise ValueError(
            f"Project catalogue is missing columns: {sorted(missing)}"
        )

    if projects["project_id"].str.strip().eq("").any():
        raise ValueError("Project catalogue contains an empty project_id.")

    if projects["project_id"].duplicated().any():
        raise ValueError("Project catalogue contains duplicate project IDs.")

    return projects

def _validate_existing_schema_version(
    database_path: str | Path,
) -> None:
    """Reject unsupported database versions before initialization."""
    with closing(_connect(database_path)) as connection:
        table = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'schema_metadata'
            """
        ).fetchone()

        # A new database has no schema metadata yet.
        if table is None:
            return

        row = connection.execute(
            """
            SELECT value
            FROM schema_metadata
            WHERE key = 'schema_version'
            """
        ).fetchone()

        if row is None:
            raise ValueError(
                "Database schema version is missing."
            )

        try:
            version = int(row["value"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Database schema version is invalid."
            ) from exc

        if version < 1 or version > SUPPORTED_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported database schema version: {version}. "
                f"Supported versions are 1 to "
                f"{SUPPORTED_SCHEMA_VERSION}."
            )


def initialize_project_tracking_database(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> None:
    """Initialize Phase 6 tables and create Phase 8 tracking tables."""
    # Reuse Phase 6 initialization instead of duplicating its schema.
        # Reject unsupported schemas before modifying the database.
    _validate_existing_schema_version(database_path)

    # Reuse Phase 6 initialization instead of duplicating its schema.
    initialize_database(database_path=database_path)

    with closing(_connect(database_path)) as connection:
        connection.execute("BEGIN")

        try:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS project_assignments (
                    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id TEXT NOT NULL
                        CHECK (length(trim(candidate_id)) > 0),
                    project_id TEXT NOT NULL,
                    target_role TEXT NOT NULL
                        CHECK (
                            target_role IN (
                                'Data Analyst',
                                'Data Scientist'
                            )
                        ),
                    status TEXT NOT NULL DEFAULT 'not_started'
                        CHECK (
                            status IN (
                                'not_started',
                                'in_progress',
                                'completed',
                                'abandoned'
                            )
                        ),
                    started_at TEXT,
                    completed_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE (candidate_id, project_id, target_role)
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS project_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    previous_status TEXT,
                    new_status TEXT NOT NULL
                        CHECK (
                            new_status IN (
                                'not_started',
                                'in_progress',
                                'completed',
                                'abandoned'
                            )
                        ),
                    occurred_at TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (assignment_id)
                        REFERENCES project_assignments(assignment_id)
                        ON DELETE CASCADE
                )
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS
                    idx_project_assignments_candidate
                ON project_assignments(candidate_id)
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS
                    idx_project_events_assignment_time
                ON project_events(assignment_id, occurred_at)
            """)



            connection.execute(
                """
                UPDATE schema_metadata
                SET value = ?
                WHERE key = 'schema_version'
                """,
                (str(SUPPORTED_SCHEMA_VERSION),),
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise


def get_candidate_project_assignments(
    candidate_id: str,
    target_role: str | None = None,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
    project_path: str | Path = PROJECT_CATALOGUE_PATH,
) -> list[dict]:
    """Return a candidate's project assignments with catalogue details."""
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string.")

    if target_role is not None and target_role not in {
        "Data Analyst",
        "Data Scientist",
    }:
        raise ValueError("Unsupported target_role.")

    projects = _load_project_catalogue(project_path)
    project_details = projects[
        ["project_id", "project_title", "target_roles", "skill_ids"]
    ]

    initialize_project_tracking_database(database_path)

    query = """
        SELECT
            assignment_id,
            candidate_id,
            project_id,
            target_role,
            status,
            started_at,
            completed_at,
            created_at,
            updated_at
        FROM project_assignments
        WHERE candidate_id = ?
    """
    parameters: list[str] = [candidate_id.strip()]

    if target_role is not None:
        query += " AND target_role = ?"
        parameters.append(target_role)

    query += " ORDER BY created_at DESC, assignment_id DESC"

    with closing(_connect(database_path)) as connection:
        rows = connection.execute(query, parameters).fetchall()

    assignments = pd.DataFrame([dict(row) for row in rows])

    if assignments.empty:
        return []

    assignments = assignments.merge(
        project_details,
        on="project_id",
        how="left",
        validate="many_to_one",
    )

    return assignments.where(pd.notna(assignments), None).to_dict(
        orient="records"
    )


def assign_project(
    candidate_id: str,
    project_id: str,
    target_role: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
    project_path: str | Path = PROJECT_CATALOGUE_PATH,
) -> int:
    """Assign a catalogue project and return its assignment ID."""
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string.")

    if not isinstance(project_id, str) or not project_id.strip():
        raise ValueError("project_id must be a non-empty string.")

    if target_role not in {"Data Analyst", "Data Scientist"}:
        raise ValueError("Unsupported target_role.")

    projects = _load_project_catalogue(project_path)
    matches = projects.loc[projects["project_id"] == project_id]

    if matches.empty:
        raise ValueError(f"Unknown project_id: {project_id}")

    project = matches.iloc[0]
    allowed_roles = {
        role.strip()
        for role in project["target_roles"].split(";")
        if role.strip()
    }

    if "Both" not in allowed_roles and target_role not in allowed_roles:
        raise ValueError(
            f"Project {project_id} is not compatible with {target_role}."
        )

    initialize_project_tracking_database(database_path)
    timestamp = _utc_now()

    with closing(_connect(database_path)) as connection:
        try:
            connection.execute("BEGIN")

            cursor = connection.execute("""
                INSERT INTO project_assignments (
                    candidate_id,
                    project_id,
                    target_role,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, 'not_started', ?, ?)
            """, (
                candidate_id.strip(),
                project_id,
                target_role,
                timestamp,
                timestamp,
            ))

            assignment_id = cursor.lastrowid

            connection.execute("""
                INSERT INTO project_events (
                    assignment_id,
                    event_type,
                    previous_status,
                    new_status,
                    occurred_at,
                    details
                )
                VALUES (?, 'assigned', NULL, 'not_started', ?, NULL)
            """, (assignment_id, timestamp))

            connection.commit()
            return int(assignment_id)

        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ValueError(
                "This project is already assigned to the candidate "
                "for the selected role."
            ) from error
        except Exception:
            connection.rollback()
            raise

def update_project_status(
    assignment_id: int,
    new_status: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> None:
    """Update a project status and record the transition in project history."""
    if (
        isinstance(assignment_id, bool)
        or not isinstance(assignment_id, int)
        or assignment_id <= 0
    ):
        raise ValueError("assignment_id must be a positive integer.")

    if not isinstance(new_status, str) or new_status not in PROJECT_STATUSES:
        raise ValueError(
            f"Invalid project status. Allowed values: "
            f"{sorted(PROJECT_STATUSES)}"
        )

    initialize_project_tracking_database(database_path)
    timestamp = _utc_now()

    with closing(_connect(database_path)) as connection:
        try:
            connection.execute("BEGIN")

            assignment = connection.execute(
                """
                SELECT status
                FROM project_assignments
                WHERE assignment_id = ?
                """,
                (assignment_id,),
            ).fetchone()

            if assignment is None:
                raise ValueError(
                    f"Unknown project assignment: {assignment_id}"
                )

            previous_status = assignment["status"]
            allowed_next = ALLOWED_STATUS_TRANSITIONS[previous_status]

            if new_status not in allowed_next:
                raise ValueError(
                    f"Invalid status transition: {previous_status} "
                    f"-> {new_status}."
                )

            started_at = timestamp if new_status == "in_progress" else None
            completed_at = timestamp if new_status == "completed" else None

            connection.execute(
                """
                UPDATE project_assignments
                SET
                    status = ?,
                    started_at = COALESCE(started_at, ?),
                    completed_at = COALESCE(?, completed_at),
                    updated_at = ?
                WHERE assignment_id = ?
                """,
                (
                    new_status,
                    started_at,
                    completed_at,
                    timestamp,
                    assignment_id,
                ),
            )

            connection.execute(
                """
                INSERT INTO project_events (
                    assignment_id,
                    event_type,
                    previous_status,
                    new_status,
                    occurred_at,
                    details
                )
                VALUES (?, 'status_changed', ?, ?, ?, NULL)
                """,
                (
                    assignment_id,
                    previous_status,
                    new_status,
                    timestamp,
                ),
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise


def submit_project_skill_evidence(
    assignment_id: int,
    candidate_id: str,
    skill_id: str,
    explanation: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
    project_path: str | Path = PROJECT_CATALOGUE_PATH,
    skill_vocabulary_path: str | Path = SKILL_VOCABULARY_PATH,
) -> dict:
    """Submit project evidence for a canonical skill as unverified."""
    if (
        isinstance(assignment_id, bool)
        or not isinstance(assignment_id, int)
        or assignment_id <= 0
    ):
        raise ValueError("assignment_id must be a positive integer.")

    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string.")

    if not isinstance(skill_id, str) or not skill_id.strip():
        raise ValueError("skill_id must be a non-empty string.")

    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError("explanation must be a non-empty string.")

    normalized_candidate = candidate_id.strip()
    normalized_skill = skill_id.strip()

    # Validate that the skill exists in GradPath's canonical vocabulary.
    vocabulary_path = Path(skill_vocabulary_path)
    if not vocabulary_path.is_file():
        raise FileNotFoundError(
            f"Skill vocabulary not found: {vocabulary_path}"
        )

    vocabulary = pd.read_csv(
        vocabulary_path,
        dtype=str,
        keep_default_na=False,
    )

    if "skill_id" not in vocabulary.columns:
        raise ValueError("Skill vocabulary is missing the skill_id column.")

    if not vocabulary["skill_id"].eq(normalized_skill).any():
        raise ValueError(f"Unknown skill_id: {normalized_skill}")

    # Validate the project catalogue and locate the assignment's project.
    projects = _load_project_catalogue(project_path)

    initialize_project_tracking_database(database_path)

    with closing(_connect(database_path)) as connection:
        assignment = connection.execute(
            """
            SELECT candidate_id, project_id
            FROM project_assignments
            WHERE assignment_id = ?
            """,
            (assignment_id,),
        ).fetchone()

    if assignment is None:
        raise ValueError(f"Unknown project assignment: {assignment_id}")

    if assignment["candidate_id"] != normalized_candidate:
        raise ValueError(
            "The assignment does not belong to this candidate."
        )

    project_matches = projects.loc[
        projects["project_id"] == assignment["project_id"]
    ]

    if project_matches.empty:
        raise ValueError(
            f"Assigned project {assignment['project_id']} "
            "is missing from the project catalogue."
        )

    project_skill_ids = {
        item.strip()
        for item in project_matches.iloc[0]["skill_ids"].split(";")
        if item.strip()
    }

    if normalized_skill not in project_skill_ids:
        raise ValueError(
            f"Skill {normalized_skill} is not listed for project "
            f"{assignment['project_id']}."
        )

    # Phase 6 stores the evidence; Phase 8 links it to this assignment.
    return record_skill_evidence(
        candidate_id=normalized_candidate,
        skill_id=normalized_skill,
        evidence_type="project",
        source_id=str(assignment_id),
        verification_status="unverified",
        explanation=explanation.strip(),
        database_path=database_path,
    )
