
import sqlite3

import pytest

from gradpath.auth import (
    authenticate_user,
    initialize_auth_database,
    register_user,
)


@pytest.fixture
def database_path(tmp_path):
    return tmp_path / "test_auth.db"


def test_register_user_returns_identity_without_password(database_path):
    user = register_user(
        "Malaika_DS",
        "malaika@example.com",
        "a-strong-test-password",
        database_path,
    )

    assert user["username"] == "malaika_ds"
    assert user["email"] == "malaika@example.com"
    assert user["user_id"]
    assert "password" not in user
    assert "password_hash" not in user


def test_login_accepts_username_and_email(database_path):
    register_user(
        "data_user",
        "data@example.com",
        "a-strong-test-password",
        database_path,
    )

    by_username = authenticate_user(
        "data_user", "a-strong-test-password", database_path
    )
    by_email = authenticate_user(
        "data@example.com", "a-strong-test-password", database_path
    )

    assert by_username is not None
    assert by_email is not None
    assert by_username["user_id"] == by_email["user_id"]


def test_login_rejects_wrong_password(database_path):
    register_user(
        "data_user",
        "data@example.com",
        "a-strong-test-password",
        database_path,
    )

    assert (
        authenticate_user(
            "data_user", "incorrect-password", database_path
        )
        is None
    )


def test_login_rejects_unknown_account(database_path):
    assert (
        authenticate_user(
            "unknown_user", "a-strong-test-password", database_path
        )
        is None
    )


def test_duplicate_username_is_rejected_case_insensitively(database_path):
    register_user(
        "data_user",
        "first@example.com",
        "a-strong-test-password",
        database_path,
    )

    with pytest.raises(ValueError, match="already registered"):
        register_user(
            "DATA_USER",
            "second@example.com",
            "another-strong-password",
            database_path,
        )


def test_duplicate_email_is_rejected(database_path):
    register_user(
        "first_user",
        "same@example.com",
        "a-strong-test-password",
        database_path,
    )

    with pytest.raises(ValueError, match="already registered"):
        register_user(
            "second_user",
            "SAME@example.com",
            "another-strong-password",
            database_path,
        )


@pytest.mark.parametrize(
    "username,email,password",
    [
        ("ab", "valid@example.com", "a-strong-test-password"),
        ("valid_user", "not-an-email", "a-strong-test-password"),
        ("valid_user", "valid@example.com", "short"),
        ("invalid user", "valid@example.com", "a-strong-test-password"),
    ],
)
def test_registration_rejects_invalid_input(
    database_path, username, email, password
):
    with pytest.raises(ValueError):
        register_user(username, email, password, database_path)


def test_password_is_stored_as_hash_not_plain_text(database_path):
    password = "a-strong-test-password"

    register_user(
        "secure_user",
        "secure@example.com",
        password,
        database_path,
    )

    initialize_auth_database(database_path)

    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT password_hash, password_salt, password_iterations
            FROM users
            WHERE username = ?
            """,
            ("secure_user",),
        ).fetchone()

    password_hash, salt, iterations = row

    assert password.encode() not in password_hash
    assert len(salt) == 32
    assert iterations >= 600_000
    assert password_hash != password.encode()


def test_each_account_gets_a_unique_salt(database_path):
    register_user(
        "first_user",
        "first@example.com",
        "a-strong-test-password",
        database_path,
    )
    register_user(
        "second_user",
        "second@example.com",
        "a-strong-test-password",
        database_path,
    )

    with sqlite3.connect(database_path) as connection:
        salts = connection.execute(
            "SELECT password_salt FROM users ORDER BY username"
        ).fetchall()

    assert salts[0][0] != salts[1][0]
