
"""Persistent CV analysis history for authenticated GradPath users."""

import json
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from gradpath.auth import (
    DEFAULT_AUTH_DATABASE_PATH,
    initialize_auth_database,
)


def _utc_now() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _connect(database_path: str | Path) -> sqlite3.Connection:
    """Open a database connection with row access by column name."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_cv_history_database(
    database_path: str | Path = DEFAULT_AUTH_DATABASE_PATH,
) -> None:
    """Create CV history storage alongside the authentication tables."""
    initialize_auth_database(database_path=database_path)

    with closing(_connect(database_path)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cv_analyses (
                cv_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                candidate_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_type TEXT NOT NULL
                    CHECK (file_type IN ('pdf', 'docx')),
                created_at TEXT NOT NULL,
                profile_json TEXT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_cv_analyses_user_created
            ON cv_analyses(user_id, created_at DESC)
            """
        )

        connection.commit()


def save_cv_analysis(
    *,
    user_id: str,
    original_filename: str,
    file_type: str,
    profile: dict,
    database_path: str | Path = DEFAULT_AUTH_DATABASE_PATH,
) -> dict:
    """Save a structured CV analysis for its authenticated owner."""
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("user_id must be a non-empty string.")

    if not isinstance(original_filename, str) or not original_filename.strip():
        raise ValueError("original_filename must be a non-empty string.")

    normalized_type = file_type.lower().lstrip(".")
    if normalized_type not in {"pdf", "docx"}:
        raise ValueError("Unsupported CV file type.")

    if not isinstance(profile, dict):
        raise ValueError("profile must be a dictionary.")

    # JSON serialization also checks that the profile can be stored safely.
    profile_json = json.dumps(
        profile,
        ensure_ascii=False,
        allow_nan=False,
    )

    cv_id = str(uuid.uuid4())
    candidate_id = f"user_{user_id.strip()}"
    created_at = _utc_now()

    initialize_cv_history_database(database_path)

    with closing(_connect(database_path)) as connection:
        connection.execute(
            """
            INSERT INTO cv_analyses (
                cv_id,
                user_id,
                candidate_id,
                original_filename,
                file_type,
                created_at,
                profile_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cv_id,
                user_id.strip(),
                candidate_id,
                Path(original_filename).name,
                normalized_type,
                created_at,
                profile_json,
            ),
        )
        connection.commit()

    return {
        "cv_id": cv_id,
        "candidate_id": candidate_id,
        "original_filename": Path(original_filename).name,
        "file_type": normalized_type,
        "created_at": created_at,
        "profile": json.loads(profile_json),
    }


def list_cv_analyses(
    *,
    user_id: str,
    database_path: str | Path = DEFAULT_AUTH_DATABASE_PATH,
) -> list[dict]:
    """List CV analyses belonging only to the specified user."""
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("user_id must be a non-empty string.")

    initialize_cv_history_database(database_path)

    with closing(_connect(database_path)) as connection:
        rows = connection.execute(
            """
            SELECT
                cv_id,
                candidate_id,
                original_filename,
                file_type,
                created_at
            FROM cv_analyses
            WHERE user_id = ?
            ORDER BY created_at DESC, cv_id DESC
            """,
            (user_id.strip(),),
        ).fetchall()

    return [dict(row) for row in rows]


def get_cv_analysis(
    *,
    cv_id: str,
    user_id: str,
    database_path: str | Path = DEFAULT_AUTH_DATABASE_PATH,
) -> dict | None:
    """Return one CV analysis only if it belongs to the requesting user."""
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("user_id must be a non-empty string.")

    if not isinstance(cv_id, str) or not cv_id.strip():
        raise ValueError("cv_id must be a non-empty string.")

    initialize_cv_history_database(database_path)

    with closing(_connect(database_path)) as connection:
        row = connection.execute(
            """
            SELECT
                cv_id,
                candidate_id,
                original_filename,
                file_type,
                created_at,
                profile_json
            FROM cv_analyses
            WHERE cv_id = ? AND user_id = ?
            """,
            (cv_id.strip(), user_id.strip()),
        ).fetchone()

    if row is None:
        return None

    result = dict(row)
    result["profile"] = json.loads(result.pop("profile_json"))
    return result
