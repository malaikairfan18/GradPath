
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from gradpath.auth import register_user
from gradpath_api import app, get_auth_database_path


FRONTEND_ORIGIN = "http://localhost:5173"
TEST_PASSWORD = "StrongPass123!"


@pytest.fixture
def client(tmp_path):
    database_path = tmp_path / "test_auth.db"

    app.dependency_overrides[get_auth_database_path] = (
        lambda: database_path
    )

    with TestClient(app) as test_client:
        test_client.test_database_path = database_path
        yield test_client

    app.dependency_overrides.clear()

def get_csrf_headers(client):
    response = client.get("/api/auth/csrf")
    assert response.status_code == 200

    token = response.json()["csrf_token"]

    return {
        "Origin": FRONTEND_ORIGIN,
        "X-CSRF-Token": token,
    }


def test_register_creates_authenticated_session(client):
    headers = get_csrf_headers(client)

    response = client.post(
        "/api/auth/register",
        headers=headers,
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    user = response.json()["user"]
    assert user["username"] == "testuser"
    assert user["email"] == "test@example.com"
    assert "password" not in user
    assert "password_hash" not in user

    assert "gradpath_session" in client.cookies

    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["user"]["user_id"] == user["user_id"]


def test_login_accepts_email(client):
    register_user(
        username="loginuser",
        email="login@example.com",
        password=TEST_PASSWORD,
        database_path=client.test_database_path,
    )

    headers = get_csrf_headers(client)

    response = client.post(
        "/api/auth/login",
        headers=headers,
        json={
            "username_or_email": "login@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "login@example.com"
    assert client.get("/api/auth/me").status_code == 200


def test_login_rejects_wrong_password(client):
    register_user(
        username="wrongpassuser",
        email="wrongpass@example.com",
        password=TEST_PASSWORD,
        database_path=client.test_database_path,
    )

    response = client.post(
        "/api/auth/login",
        headers=get_csrf_headers(client),
        json={
            "username_or_email": "wrongpassuser",
            "password": "IncorrectPassword123!",
        },
    )

    assert response.status_code == 401


def test_register_rejects_missing_csrf_token(client):
    response = client.post(
        "/api/auth/register",
        headers={"Origin": FRONTEND_ORIGIN},
        json={
            "username": "nocrsfuser",
            "email": "nocrsf@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 403


def test_register_rejects_untrusted_origin(client):
    response = client.post(
        "/api/auth/register",
        headers={
            "Origin": "https://untrusted.example",
        },
        json={
            "username": "originuser",
            "email": "origin@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 403


def test_logout_revokes_session(client):
    register_response = client.post(
        "/api/auth/register",
        headers=get_csrf_headers(client),
        json={
            "username": "logoutuser",
            "email": "logout@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert register_response.status_code == 200
    assert client.get("/api/auth/me").status_code == 200

    logout_response = client.post(
        "/api/auth/logout",
        headers=get_csrf_headers(client),
    )

    assert logout_response.status_code == 200
    assert client.get("/api/auth/me").status_code == 401


def client_database_path(client):
    # Each test gets its own database through the dependency override.
    # The helper below is replaced by the fixture's explicit path.
    return app.dependency_overrides[get_auth_database_path]()


def test_cv_upload_requires_authentication(client):
    response = client.post(
        "/api/cv/analyze",
        files={
            "file": (
                "sample.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_authenticated_cv_upload_is_saved_to_history(client, monkeypatch):
    import gradpath_api

    register_response = client.post(
        "/api/auth/register",
        headers=get_csrf_headers(client),
        json={
            "username": "cvowner",
            "email": "cvowner@example.com",
            "password": TEST_PASSWORD,
        },
    )
    assert register_response.status_code == 200

    def fake_build_candidate_profile(file_path, candidate_id):
        return {
            "candidate_id": candidate_id,
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "skills": [
                {"skill": "Python", "verification_status": "unverified"}
            ],
            "extraction_warnings": [],
        }

    monkeypatch.setattr(
        gradpath_api,
        "build_candidate_profile",
        fake_build_candidate_profile,
    )

    upload_response = client.post(
        "/api/cv/analyze",
        files={
            "file": (
                "sample.pdf",
                b"controlled test content",
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert upload_data["cv_id"]
    assert upload_data["profile"]["candidate_id"].startswith("user_")

    history_response = client.get("/api/cv/history")
    assert history_response.status_code == 200

    analyses = history_response.json()["analyses"]
    assert len(analyses) == 1
    assert analyses[0]["cv_id"] == upload_data["cv_id"]
    assert analyses[0]["original_filename"] == "sample.pdf"

    detail_response = client.get(
        f"/api/cv/history/{upload_data['cv_id']}"
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["analysis"]["profile"] == upload_data["profile"]


def test_user_cannot_access_another_users_cv_history(client, monkeypatch):
    import gradpath_api

    def register(username, email):
        response = client.post(
            "/api/auth/register",
            headers=get_csrf_headers(client),
            json={
                "username": username,
                "email": email,
                "password": TEST_PASSWORD,
            },
        )
        assert response.status_code == 200
        return response.json()["user"]

    first_user = register("firstowner", "firstowner@example.com")

    def fake_build_candidate_profile(file_path, candidate_id):
        return {
            "candidate_id": candidate_id,
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "skills": [],
            "extraction_warnings": [],
        }

    monkeypatch.setattr(
        gradpath_api,
        "build_candidate_profile",
        fake_build_candidate_profile,
    )

    upload_response = client.post(
        "/api/cv/analyze",
        files={
            "file": (
                "private.pdf",
                b"controlled test content",
                "application/pdf",
            )
        },
    )
    assert upload_response.status_code == 200
    first_cv_id = upload_response.json()["cv_id"]

    # Log out the first user, then log in as a different user.
    logout_response = client.post(
        "/api/auth/logout",
        headers=get_csrf_headers(client),
    )
    assert logout_response.status_code == 200

    second_user = register("secondowner", "secondowner@example.com")
    assert second_user["user_id"] != first_user["user_id"]

    history_response = client.get("/api/cv/history")
    assert history_response.status_code == 200
    assert history_response.json()["analyses"] == []

    detail_response = client.get(f"/api/cv/history/{first_cv_id}")
    assert detail_response.status_code == 404
    assert detail_response.json()["detail"] == "CV analysis not found."
