
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from gradpath.auth import register_user
from gradpath.cv_history import (
    get_cv_analysis,
    list_cv_analyses,
    save_cv_analysis,
)


@pytest.fixture
def setup_users(tmp_path):
    database_path = tmp_path / "test_cv_history.db"

    first_user = register_user(
        username="firstuser",
        email="first@example.com",
        password="StrongPass123!",
        database_path=database_path,
    )

    second_user = register_user(
        username="seconduser",
        email="second@example.com",
        password="StrongPass123!",
        database_path=database_path,
    )

    return database_path, first_user, second_user


def sample_profile(candidate_id="placeholder"):
    return {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "source_document": {
            "file_type": "pdf",
            "extraction_status": "success",
            "text_char_count": 1200,
        },
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "skills": [
            {
                "skill": "Python",
                "verification_status": "unverified",
            }
        ],
        "extraction_warnings": [],
    }


def test_save_and_retrieve_cv_analysis(setup_users):
    database_path, user, _ = setup_users

    profile = sample_profile()

    saved = save_cv_analysis(
        user_id=user["user_id"],
        original_filename="my_cv.pdf",
        file_type="pdf",
        profile=profile,
        database_path=database_path,
    )

    retrieved = get_cv_analysis(
        cv_id=saved["cv_id"],
        user_id=user["user_id"],
        database_path=database_path,
    )

    assert retrieved is not None
    assert retrieved["cv_id"] == saved["cv_id"]
    assert retrieved["original_filename"] == "my_cv.pdf"
    assert retrieved["file_type"] == "pdf"
    assert retrieved["profile"] == profile


def test_cv_history_survives_separate_calls(setup_users):
    database_path, user, _ = setup_users

    saved = save_cv_analysis(
        user_id=user["user_id"],
        original_filename="updated_cv.docx",
        file_type="docx",
        profile=sample_profile(),
        database_path=database_path,
    )

    history = list_cv_analyses(
        user_id=user["user_id"],
        database_path=database_path,
    )

    assert len(history) == 1
    assert history[0]["cv_id"] == saved["cv_id"]
    assert history[0]["original_filename"] == "updated_cv.docx"


def test_users_only_see_their_own_cv_history(setup_users):
    database_path, first_user, second_user = setup_users

    saved = save_cv_analysis(
        user_id=first_user["user_id"],
        original_filename="private_cv.pdf",
        file_type="pdf",
        profile=sample_profile(),
        database_path=database_path,
    )

    first_history = list_cv_analyses(
        user_id=first_user["user_id"],
        database_path=database_path,
    )
    second_history = list_cv_analyses(
        user_id=second_user["user_id"],
        database_path=database_path,
    )

    assert len(first_history) == 1
    assert second_history == []

    unauthorized_result = get_cv_analysis(
        cv_id=saved["cv_id"],
        user_id=second_user["user_id"],
        database_path=database_path,
    )

    assert unauthorized_result is None


def test_each_upload_gets_a_distinct_cv_id(setup_users):
    database_path, user, _ = setup_users

    first = save_cv_analysis(
        user_id=user["user_id"],
        original_filename="cv.pdf",
        file_type="pdf",
        profile=sample_profile(),
        database_path=database_path,
    )

    second = save_cv_analysis(
        user_id=user["user_id"],
        original_filename="cv.pdf",
        file_type="pdf",
        profile=sample_profile(),
        database_path=database_path,
    )

    assert first["cv_id"] != second["cv_id"]

    history = list_cv_analyses(
        user_id=user["user_id"],
        database_path=database_path,
    )
    assert len(history) == 2


def test_rejects_unsupported_file_type(setup_users):
    database_path, user, _ = setup_users

    with pytest.raises(ValueError, match="Unsupported CV file type"):
        save_cv_analysis(
            user_id=user["user_id"],
            original_filename="cv.txt",
            file_type="txt",
            profile=sample_profile(),
            database_path=database_path,
        )


def test_rejects_unknown_user(setup_users):
    database_path, _, _ = setup_users

    with pytest.raises(Exception):
        save_cv_analysis(
            user_id="nonexistent-user",
            original_filename="cv.pdf",
            file_type="pdf",
            profile=sample_profile(),
            database_path=database_path,
        )
