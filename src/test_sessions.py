
import sqlite3

import pytest

from gradpath.auth import register_user
from gradpath.sessions import (
    create_session,
    get_session_user,
    initialize_session_database,
    revoke_session,
)


@pytest.fixture
def database_path(tmp_path):
    return tmp_path / "test_sessions.db"


@pytest.fixture
def user(database_path):
    return register_user(
        "session_user",
        "session@example.com",
        "a-strong-test-password",
        database_path,
    )


def test_create_session_returns_token_and_expiry(database_path, user):
    session = create_session(user["user_id"], database_path)

    assert session["token"]
    assert session["expires_at"]
    assert get_session_user(session["token"], database_path) == user


def test_raw_session_token_is_not_stored(database_path, user):
    session = create_session(user["user_id"], database_path)
    initialize_session_database(database_path)

    with sqlite3.connect(database_path) as connection:
        stored_token = connection.execute(
            "SELECT token_hash FROM sessions"
        ).fetchone()[0]

    assert stored_token != session["token"]


def test_invalid_or_missing_token_is_rejected(database_path):
    assert get_session_user(None, database_path) is None
    assert get_session_user("", database_path) is None
    assert get_session_user("invalid-token", database_path) is None


def test_revoked_session_is_rejected(database_path, user):
    session = create_session(user["user_id"], database_path)

    assert revoke_session(session["token"], database_path) is True
    assert get_session_user(session["token"], database_path) is None


def test_session_cannot_be_created_for_unknown_user(database_path):
    with pytest.raises(ValueError, match="account does not exist"):
        create_session("unknown-user-id", database_path)


@pytest.mark.parametrize("ttl_seconds", [0, -1, True, 1.5])
def test_invalid_session_lifetime_is_rejected(
    database_path, user, ttl_seconds
):
    with pytest.raises(ValueError, match="positive integer"):
        create_session(
            user["user_id"],
            database_path,
            ttl_seconds=ttl_seconds,
        )
