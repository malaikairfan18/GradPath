
"""Server-side session management for GradPath."""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gradpath.auth import (
    DEFAULT_AUTH_DATABASE_PATH,
    _connect,
    initialize_auth_database,
)


DEFAULT_SESSION_TTL_SECONDS = 60 * 60 * 24 * 7


def _utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _token_hash(token: str) -> str:
    """Hash a session token before storing or looking it up."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def initialize_session_database(
    database_path: str | Path = DEFAULT_AUTH_DATABASE_PATH,
) -> None:
    """Create the session table in the authentication database."""
    initialize_auth_database(database_path)

    with closing(_connect(database_path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    revoked_at TEXT,
                    FOREIGN KEY (user_id)
                        REFERENCES users(user_id)
                        ON DELETE CASCADE
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sessions_user_id
                ON sessions(user_id)
                """
            )


def create_session(
    user_id: str,
    database_path: str | Path = DEFAULT_AUTH_DATABASE_PATH,
    ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS,
) -> dict[str, str]:
    """Create a session and return its raw token and expiry."""
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("A valid user ID is required.")

    if (
        not isinstance(ttl_seconds, int)
        or isinstance(ttl_seconds, bool)
        or ttl_seconds <= 0
    ):
        raise ValueError("Session lifetime must be a positive integer.")

    initialize_session_database(database_path)

    now = _utc_now()
    expires_at = now + timedelta(seconds=ttl_seconds)
    token = secrets.token_urlsafe(32)

    with closing(_connect(database_path)) as connection:
        with connection:
            user = connection.execute(
                "SELECT user_id FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()

            if user is None:
                raise ValueError("The account does not exist.")

            connection.execute(
                """
                INSERT INTO sessions (
                    token_hash,
                    user_id,
                    created_at,
                    expires_at,
                    revoked_at
                )
                VALUES (?, ?, ?, ?, NULL)
                """,
                (
                    _token_hash(token),
                    user_id,
                    now.isoformat(),
                    expires_at.isoformat(),
                ),
            )

    # The raw token is returned once and is never stored in SQLite.
    return {
        "token": token,
        "expires_at": expires_at.isoformat(),
    }


def get_session_user(
    token: str | None,
    database_path: str | Path = DEFAULT_AUTH_DATABASE_PATH,
) -> dict[str, str] | None:
    """Return the session owner's identity if the session is valid."""
    if not isinstance(token, str) or not token:
        return None

    initialize_session_database(database_path)
    now = _utc_now().isoformat()

    with closing(_connect(database_path)) as connection:
        row = connection.execute(
            """
            SELECT
                users.user_id,
                users.username,
                users.email
            FROM sessions
            JOIN users ON users.user_id = sessions.user_id
            WHERE sessions.token_hash = ?
              AND sessions.revoked_at IS NULL
              AND sessions.expires_at > ?
            """,
            (_token_hash(token), now),
        ).fetchone()

    if row is None:
        return None

    return {
        "user_id": row["user_id"],
        "username": row["username"],
        "email": row["email"],
    }


def revoke_session(
    token: str | None,
    database_path: str | Path = DEFAULT_AUTH_DATABASE_PATH,
) -> bool:
    """Revoke a session token; return whether a session was revoked."""
    if not isinstance(token, str) or not token:
        return False

    initialize_session_database(database_path)

    with closing(_connect(database_path)) as connection:
        with connection:
            cursor = connection.execute(
                """
                UPDATE sessions
                SET revoked_at = ?
                WHERE token_hash = ?
                  AND revoked_at IS NULL
                """,
                (_utc_now().isoformat(), _token_hash(token)),
            )

    return cursor.rowcount > 0
