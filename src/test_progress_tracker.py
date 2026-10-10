
"""Tests for the GradPath Phase 6 learning progress tracker."""

import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

from gradpath.progress_tracker import (
    assign_learning_activity,
    get_learning_progress_summary,
    initialize_database,
    record_assessment_attempt,
    record_skill_evidence,
    update_learning_progress,
    validate_resource_assignment,
)


def expect_value_error(function, *args, **kwargs):
    """Assert that a function rejects invalid input."""
    try:
        function(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(
        f"{function.__name__} should have raised ValueError."
    )


def run_tests():
    """Run Phase 6 tests using an isolated temporary database."""
    with tempfile.TemporaryDirectory() as temp:
        database_path = Path(temp) / "test_progress.db"

        # 1. Database initialization and schema.
        initialize_database(database_path)
        initialize_database(database_path)

        with closing(sqlite3.connect(database_path)) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                    """
                ).fetchall()
            }

            version_row = connection.execute(
                """
                SELECT value
                FROM schema_metadata
                WHERE key = 'schema_version'
                """
            ).fetchone()

        expected_tables = {
            "learning_activities",
            "progress_events",
            "assessment_attempts",
            "skill_evidence",
            "schema_metadata",
        }
        assert expected_tables.issubset(tables)
        assert version_row is not None
        assert version_row[0] == "1"

        print("1. Database initialization tests passed.")

        # 2. Resource catalogue validation.
        resource = validate_resource_assignment(
            "LR001", "SK001", "Data Analyst"
        )
        assert resource["resource_id"] == "LR001"
        assert resource["skill_id"] == "SK001"

        expect_value_error(
            validate_resource_assignment,
            "LR001", "WRONG_SKILL", "Data Analyst",
        )
        expect_value_error(
            validate_resource_assignment,
            "UNKNOWN_RESOURCE", "SK001", "Data Analyst",
        )
        expect_value_error(
            validate_resource_assignment,
            "LR001", "SK001", "Unsupported Role",
        )

        print("2. Resource validation tests passed.")

        # 3. Assign an activity and check its initial event.
        candidate_id = "TEST_CANDIDATE_001"

        activity = assign_learning_activity(
            candidate_id=candidate_id,
            resource_id="LR001",
            skill_id="SK001",
            target_role="Data Analyst",
            database_path=database_path,
        )
        activity_id = activity["activity_id"]

        assert activity["candidate_id"] == candidate_id
        assert activity["status"] == "not_started"
        assert activity["progress_percent"] == 0

        with closing(sqlite3.connect(database_path)) as connection:
            event_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM progress_events
                WHERE activity_id = ?
                """,
                (activity_id,),
            ).fetchone()[0]

        assert event_count == 1

        # Duplicate assignment must be rejected without adding an event.
        expect_value_error(
            assign_learning_activity,
            candidate_id,
            "LR001",
            "SK001",
            "Data Analyst",
            database_path,
        )

        with closing(sqlite3.connect(database_path)) as connection:
            activity_count = connection.execute(
                "SELECT COUNT(*) FROM learning_activities"
            ).fetchone()[0]
            total_events = connection.execute(
                "SELECT COUNT(*) FROM progress_events"
            ).fetchone()[0]

        assert activity_count == 1
        assert total_events == 1

        print("3. Activity assignment tests passed.")

        # 4. Progress updates, status transitions, and event history.
        updated = update_learning_progress(
            activity_id, 40, database_path
        )
        assert updated["status"] == "in_progress"
        assert updated["progress_percent"] == 40
        assert updated["started_at"] is not None

        completed = update_learning_progress(
            activity_id, 100, database_path
        )
        assert completed["status"] == "completed"
        assert completed["progress_percent"] == 100
        assert completed["completed_at"] is not None

        expect_value_error(
            update_learning_progress,
            activity_id, 50, database_path,
        )
        expect_value_error(
            update_learning_progress,
            99999, 50, database_path,
        )

        for invalid_progress in (-1, 101, 40.5, True, "50"):
            expect_value_error(
                update_learning_progress,
                activity_id, invalid_progress, database_path,
            )

        with closing(sqlite3.connect(database_path)) as connection:
            events = connection.execute(
                """
                SELECT event_type, new_status, progress_percent
                FROM progress_events
                WHERE activity_id = ?
                ORDER BY event_id
                """,
                (activity_id,),
            ).fetchall()

        assert len(events) == 3
        assert events[0][0] == "assigned"
        assert events[1][2] == 40
        assert events[2][1] == "completed"
        assert events[2][2] == 100

        print("4. Progress update and history tests passed.")

        # 5. Assessment attempts, including separate retakes.
        first_attempt = record_assessment_attempt(
            candidate_id=candidate_id,
            skill_id="SK001",
            assessment_type="quiz",
            score=6,
            max_score=10,
            passed=False,
            activity_id=activity_id,
            assessment_metadata={"attempt_number": 1},
            database_path=database_path,
        )

        second_attempt = record_assessment_attempt(
            candidate_id=candidate_id,
            skill_id="SK001",
            assessment_type="quiz",
            score=9,
            max_score=10,
            passed=True,
            activity_id=activity_id,
            assessment_metadata={"attempt_number": 2},
            database_path=database_path,
        )

        assert first_attempt["attempt_id"] != second_attempt["attempt_id"]
        assert first_attempt["passed"] == 0
        assert second_attempt["passed"] == 1

        # Scoreless qualitative evaluations are also supported.
        qualitative_attempt = record_assessment_attempt(
            candidate_id=candidate_id,
            skill_id="SK002",
            assessment_type="project_evaluation",
            database_path=database_path,
        )
        assert qualitative_attempt["score"] is None
        assert qualitative_attempt["max_score"] is None

        expect_value_error(
            record_assessment_attempt,
            candidate_id, "SK001", "unknown_type",
            database_path=database_path,
        )
        expect_value_error(
            record_assessment_attempt,
            candidate_id, "SK001", "quiz",
            score=11, max_score=10,
            database_path=database_path,
        )
        expect_value_error(
            record_assessment_attempt,
            candidate_id, "SK001", "quiz",
            score=5, max_score=0,
            database_path=database_path,
        )
        expect_value_error(
            record_assessment_attempt,
            candidate_id, "SK001", "quiz",
            score=5,
            database_path=database_path,
        )
        expect_value_error(
            record_assessment_attempt,
            candidate_id, "SK001", "quiz",
            passed="yes",
            database_path=database_path,
        )
        expect_value_error(
            record_assessment_attempt,
            candidate_id, "SK001", "quiz",
            activity_id=99999,
            database_path=database_path,
        )
        expect_value_error(
            record_assessment_attempt,
            "ANOTHER_CANDIDATE", "SK001", "quiz",
            activity_id=activity_id,
            database_path=database_path,
        )
        expect_value_error(
            record_assessment_attempt,
            candidate_id, "SK002", "quiz",
            activity_id=activity_id,
            database_path=database_path,
        )

        print("5. Assessment attempt tests passed.")

        # 6. Skill evidence and verification states.
        unverified = record_skill_evidence(
            candidate_id=candidate_id,
            skill_id="SK001",
            evidence_type="project",
            verification_status="unverified",
            explanation="Project evidence awaiting review.",
            database_path=database_path,
        )
        verified = record_skill_evidence(
            candidate_id=candidate_id,
            skill_id="SK001",
            evidence_type="assessment",
            verification_status="verified",
            source_id=str(second_attempt["attempt_id"]),
            proficiency_level="intermediate",
            database_path=database_path,
        )

        assert unverified["verification_status"] == "unverified"
        assert verified["verification_status"] == "verified"
        assert unverified["evidence_id"] != verified["evidence_id"]

        expect_value_error(
            record_skill_evidence,
            candidate_id, "SK001", "unknown_evidence_type",
            database_path=database_path,
        )
        expect_value_error(
            record_skill_evidence,
            candidate_id, "SK001", "project",
            verification_status="unknown_status",
            database_path=database_path,
        )
        expect_value_error(
            record_skill_evidence,
            candidate_id, "SK001", "project",
            explanation=123,
            database_path=database_path,
        )

        # Confirm evidence persisted after its connection was closed.
        with closing(sqlite3.connect(database_path)) as connection:
            evidence_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM skill_evidence
                WHERE candidate_id = ?
                """,
                (candidate_id,),
            ).fetchone()[0]

        assert evidence_count == 2

        print("6. Skill evidence tests passed.")

        # 7. Progress summary calculations.
        second_activity = assign_learning_activity(
            candidate_id=candidate_id,
            resource_id="LR002",
            skill_id="SK002",
            target_role="Data Analyst",
            database_path=database_path,
        )
        assert second_activity["status"] == "not_started"

        summary = get_learning_progress_summary(
            candidate_id=candidate_id,
            target_role="Data Analyst",
            database_path=database_path,
        )

        activities = summary["learning_activities"]
        assessments = summary["assessments"]
        evidence = summary["skill_evidence"]

        assert activities["total"] == 2
        assert activities["completed"] == 1
        assert activities["not_started"] == 1
        assert activities["in_progress"] == 0
        assert activities["average_progress_percent"] == 50.0

        assert assessments["total_attempts"] == 3
        assert assessments["skills_assessed"] == 2
        assert assessments["average_score_percent"] == 75.0

        assert evidence["total_records"] == 2
        assert evidence["verified_records"] == 1
        assert evidence["skills_with_verified_evidence"] == 1

        expect_value_error(
            get_learning_progress_summary,
            candidate_id,
            "Unsupported Role",
            database_path,
        )

        print("7. Progress summary tests passed.")
        print("\nAll Phase 6 progress tracker tests passed.")


if __name__ == "__main__":
    run_tests()
