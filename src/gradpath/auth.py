
"""Account registration and authentication for GradPath."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUTH_DATABASE_PATH = (
    PROJECT_ROOT / "data" / "processed" / "gradpath_auth.db"
)

# PBKDF2-HMAC-SHA256 with a unique salt for each account.
HASH_NAME = "sha256"
HASH_ITERATIONS = 600_000
SALT_BYTES = 32
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 1024


def _utc_now() -> str:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _connect(database_path: str | Path) -> sqlite3.Connection:
    """Open the authentication database."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _normalize_username(username: str) -> str:
    """Validate and normalize a username."""
    if not isinstance(username, str):
        raise ValueError("Username must be text.")

    normalized = username.strip().lower()

    if not re.fullmatch(r"[a-z0-9_.-]{3,32}", normalized):
        raise ValueError(
            "Username must contain 3–32 letters, numbers, "
            "periods, underscores, or hyphens."
        )

    return normalized


def _normalize_email(email: str) -> str:
    """Validate and normalize an email address."""
    if not isinstance(email, str):
        raise ValueError("Email must be text.")

    normalized = email.strip().lower()

    if (
        len(normalized) > 254
        or not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            normalized,
        )
    ):
        raise ValueError("Enter a valid email address.")

    return normalized


def _validate_password(password: str) -> None:
    """Validate a new password without modifying its contents."""
    if not isinstance(password, str):
        raise ValueError("Password must be text.")

    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must contain between {MIN_PASSWORD_LENGTH} "
            f"and {MAX_PASSWORD_LENGTH} characters."
        )


def _hash_password(
    password: str,
    salt: bytes,
    iterations: int = HASH_ITERATIONS,
) -> bytes:
    """Derive a password hash using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode("utf-8"),
        salt,
        iterations,
    )


def initialize_auth_database(
    database_path: str | Path = DEFAULT_AUTH_DATABASE_PATH,
) -> None:
    """Create the authentication table if it does not exist."""
    with closing(_connect(database_path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash BLOB NOT NULL,
                    password_salt BLOB NOT NULL,
                    password_iterations INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )


def register_user(
    username: str,
    email: str,
    password: str,
    database_path: str | Path = DEFAULT_AUTH_DATABASE_PATH,
) -> dict[str, str]:
    """Register an account and return its non-secret identity fields."""
    normalized_username = _normalize_username(username)
    normalized_email = _normalize_email(email)
    _validate_password(password)

    salt = secrets.token_bytes(SALT_BYTES)
    password_hash = _hash_password(password, salt)
    user_id = str(uuid.uuid4())

    initialize_auth_database(database_path)

    try:
        with closing(_connect(database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO users (
                        user_id,
                        username,
                        email,
                        password_hash,
                        password_salt,
                        password_iterations,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        normalized_username,
                        normalized_email,
                        password_hash,
                        salt,
                        HASH_ITERATIONS,
                        _utc_now(),
                    ),
                )
    except sqlite3.IntegrityError as exc:
        raise ValueError(
            "That username or email is already registered."
        ) from exc

    return {
        "user_id": user_id,
        "username": normalized_username,
        "email": normalized_email,
    }


def authenticate_user(
    username_or_email: str,
    password: str,
    database_path: str | Path = DEFAULT_AUTH_DATABASE_PATH,
) -> dict[str, str] | None:
    """Authenticate credentials; return identity fields or None."""
    if (
        not isinstance(username_or_email, str)
        or not username_or_email.strip()
        or not isinstance(password, str)
        or not password
        or len(password) > MAX_PASSWORD_LENGTH
    ):
        return None

    identifier = username_or_email.strip().lower()
    initialize_auth_database(database_path)

    with closing(_connect(database_path)) as connection:
        user = connection.execute(
            """
            SELECT
                user_id,
                username,
                email,
                password_hash,
                password_salt,
                password_iterations
            FROM users
            WHERE username = ? OR email = ?
            """,
            (identifier, identifier),
        ).fetchone()

    if user is None:
        # Perform a comparable derivation for unknown accounts.
        _hash_password(
            password,
            b"gradpath-invalid-account-salt",
            HASH_ITERATIONS,
        )
        return None

    candidate_hash = _hash_password(
        password,
        user["password_salt"],
        user["password_iterations"],
    )

    if not hmac.compare_digest(
        candidate_hash,
        user["password_hash"],
    ):
        return None

    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
    }
