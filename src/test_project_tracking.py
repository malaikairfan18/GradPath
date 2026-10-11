
"""Tests for GradPath Phase 8 project tracking."""

from contextlib import closing
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gradpath.progress_tracker import initialize_database

from gradpath.project_tracking import (
    SUPPORTED_SCHEMA_VERSION,
    assign_project,
    initialize_project_tracking_database,
    submit_project_skill_evidence,
    update_project_status,
)


class ProjectTrackingTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test_progress.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialization_creates_phase_6_and_phase_8_tables(self):
        initialize_project_tracking_database(self.database_path)

        with closing(sqlite3.connect(self.database_path)) as connection:
            tables = {
                row[0]
                for row in connection.execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                """)
            }

        self.assertTrue({
            "learning_activities",
            "progress_events",
            "assessment_attempts",
            "skill_evidence",
            "schema_metadata",
            "project_assignments",
            "project_events",
        }.issubset(tables))

    def test_initialization_is_repeatable(self):
        initialize_project_tracking_database(self.database_path)
        initialize_project_tracking_database(self.database_path)


    def test_initialization_sets_schema_version_to_two(self):
        initialize_project_tracking_database(self.database_path)

        with closing(sqlite3.connect(self.database_path)) as connection:
            version = connection.execute("""
                SELECT value
                FROM schema_metadata
                WHERE key = 'schema_version'
            """).fetchone()[0]

        self.assertEqual(version, str(SUPPORTED_SCHEMA_VERSION))
        self.assertEqual(version, "2")

    def test_existing_version_one_database_is_upgraded(self):
        initialize_database(database_path=self.database_path)

        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute("""
                INSERT INTO schema_metadata (key, value)
                VALUES ('test_marker', 'preserve_me')
            """)
            connection.commit()

        initialize_project_tracking_database(self.database_path)

        with closing(sqlite3.connect(self.database_path)) as connection:
            version = connection.execute("""
                SELECT value
                FROM schema_metadata
                WHERE key = 'schema_version'
            """).fetchone()[0]

            marker = connection.execute("""
                SELECT value
                FROM schema_metadata
                WHERE key = 'test_marker'
            """).fetchone()[0]

            project_tables = {
                row[0]
                for row in connection.execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                """)
            }

        self.assertEqual(version, "2")
        self.assertEqual(marker, "preserve_me")
        self.assertIn("project_assignments", project_tables)
        self.assertIn("project_events", project_tables)

    def test_newer_schema_version_is_rejected_without_downgrade(self):
        initialize_database(database_path=self.database_path)

        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute("""
                UPDATE schema_metadata
                SET value = '99'
                WHERE key = 'schema_version'
            """)
            connection.commit()

        with self.assertRaisesRegex(ValueError, "schema version"):
            initialize_project_tracking_database(self.database_path)

        with closing(sqlite3.connect(self.database_path)) as connection:
            version = connection.execute("""
                SELECT value
                FROM schema_metadata
                WHERE key = 'schema_version'
            """).fetchone()[0]

            project_tables = {
                row[0]
                for row in connection.execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                """)
            }

        self.assertEqual(version, "99")
        self.assertNotIn("project_assignments", project_tables)
        self.assertNotIn("project_events", project_tables)


    def test_assign_valid_data_analyst_project(self):
        assignment_id = assign_project(
            candidate_id="candidate-001",
            project_id="PRJ001",
            target_role="Data Analyst",
            database_path=self.database_path,
        )

        self.assertIsInstance(assignment_id, int)

        with closing(sqlite3.connect(self.database_path)) as connection:
            assignment = connection.execute("""
                SELECT candidate_id, project_id, target_role, status
                FROM project_assignments
                WHERE assignment_id = ?
            """, (assignment_id,)).fetchone()

            event = connection.execute("""
                SELECT event_type, previous_status, new_status
                FROM project_events
                WHERE assignment_id = ?
            """, (assignment_id,)).fetchone()

        self.assertEqual(
            assignment,
            ("candidate-001", "PRJ001", "Data Analyst", "not_started"),
        )
        self.assertEqual(event, ("assigned", None, "not_started"))

    def test_unknown_project_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown project_id"):
            assign_project(
                candidate_id="candidate-001",
                project_id="PRJ999",
                target_role="Data Analyst",
                database_path=self.database_path,
            )

    def test_role_incompatible_project_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not compatible"):
            assign_project(
                candidate_id="candidate-001",
                project_id="PRJ003",
                target_role="Data Scientist",
                database_path=self.database_path,
            )

    def test_invalid_target_role_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported target_role"):
            assign_project(
                candidate_id="candidate-001",
                project_id="PRJ001",
                target_role="Data Engineer",
                database_path=self.database_path,
            )

    def test_empty_candidate_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "candidate_id"):
            assign_project(
                candidate_id=" ",
                project_id="PRJ001",
                target_role="Data Analyst",
                database_path=self.database_path,
            )

    def test_duplicate_assignment_is_rejected(self):
        arguments = {
            "candidate_id": "candidate-001",
            "project_id": "PRJ001",
            "target_role": "Data Analyst",
            "database_path": self.database_path,
        }

        first_id = assign_project(**arguments)

        with self.assertRaisesRegex(ValueError, "already assigned"):
            assign_project(**arguments)

        with closing(sqlite3.connect(self.database_path)) as connection:
            assignment_count = connection.execute("""
                SELECT COUNT(*)
                FROM project_assignments
                WHERE candidate_id = ?
            """, ("candidate-001",)).fetchone()[0]

            event_count = connection.execute("""
                SELECT COUNT(*)
                FROM project_events
                WHERE assignment_id = ?
            """, (first_id,)).fetchone()[0]

        self.assertEqual(assignment_count, 1)
        self.assertEqual(event_count, 1)

    def test_status_can_change_from_not_started_to_in_progress(self):
        assignment_id = assign_project(
            candidate_id="candidate_status_1",
            project_id="PRJ001",
            target_role="Data Analyst",
            database_path=self.database_path,
        )

        update_project_status(
            assignment_id,
            "in_progress",
            database_path=self.database_path,
        )

        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute("""
                SELECT status, started_at, completed_at
                FROM project_assignments
                WHERE assignment_id = ?
            """, (assignment_id,)).fetchone()

        self.assertEqual(row[0], "in_progress")
        self.assertIsNotNone(row[1])
        self.assertIsNone(row[2])

    def test_status_can_change_to_completed(self):
        assignment_id = assign_project(
            candidate_id="candidate_status_2",
            project_id="PRJ001",
            target_role="Data Analyst",
            database_path=self.database_path,
        )

        update_project_status(
            assignment_id,
            "in_progress",
            database_path=self.database_path,
        )
        update_project_status(
            assignment_id,
            "completed",
            database_path=self.database_path,
        )

        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute("""
                SELECT status, started_at, completed_at
                FROM project_assignments
                WHERE assignment_id = ?
            """, (assignment_id,)).fetchone()

        self.assertEqual(row[0], "completed")
        self.assertIsNotNone(row[1])
        self.assertIsNotNone(row[2])

    def test_invalid_status_transition_is_rejected(self):
        assignment_id = assign_project(
            candidate_id="candidate_status_3",
            project_id="PRJ001",
            target_role="Data Analyst",
            database_path=self.database_path,
        )

        with self.assertRaises(ValueError):
            update_project_status(
                assignment_id,
                "completed",
                database_path=self.database_path,
            )

    def test_completed_project_cannot_be_reopened(self):
        assignment_id = assign_project(
            candidate_id="candidate_status_4",
            project_id="PRJ001",
            target_role="Data Analyst",
            database_path=self.database_path,
        )

        update_project_status(
            assignment_id,
            "in_progress",
            database_path=self.database_path,
        )
        update_project_status(
            assignment_id,
            "completed",
            database_path=self.database_path,
        )

        with self.assertRaises(ValueError):
            update_project_status(
                assignment_id,
                "in_progress",
                database_path=self.database_path,
            )

    def test_status_changes_are_recorded_in_project_events(self):
        assignment_id = assign_project(
            candidate_id="candidate_status_5",
            project_id="PRJ001",
            target_role="Data Analyst",
            database_path=self.database_path,
        )

        update_project_status(
            assignment_id,
            "in_progress",
            database_path=self.database_path,
        )

        with closing(sqlite3.connect(self.database_path)) as connection:
            rows = connection.execute("""
                SELECT event_type, previous_status, new_status
                FROM project_events
                WHERE assignment_id = ?
                ORDER BY event_id
            """, (assignment_id,)).fetchall()

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ("assigned", None, "not_started"))
        self.assertEqual(
            rows[1],
            ("status_changed", "not_started", "in_progress"),
        )



    def test_valid_project_skill_evidence_is_saved_as_unverified(self):
        assignment_id = assign_project(
            candidate_id="candidate-1",
            project_id="PRJ001",
            target_role="Data Analyst",
            database_path=self.database_path,
        )

        result = submit_project_skill_evidence(
            assignment_id=assignment_id,
            candidate_id="candidate-1",
            skill_id="SK001",
            explanation="Used Python to clean and analyze the dataset.",
            database_path=self.database_path,
        )

        self.assertEqual(result["candidate_id"], "candidate-1")
        self.assertEqual(result["skill_id"], "SK001")
        self.assertEqual(result["evidence_type"], "project")
        self.assertEqual(result["source_id"], str(assignment_id))
        self.assertEqual(result["verification_status"], "unverified")

    def test_unknown_skill_is_rejected(self):
        assignment_id = assign_project(
            candidate_id="candidate-1",
            project_id="PRJ001",
            target_role="Data Analyst",
            database_path=self.database_path,
        )

        with self.assertRaisesRegex(ValueError, "Unknown skill_id"):
            submit_project_skill_evidence(
                assignment_id=assignment_id,
                candidate_id="candidate-1",
                skill_id="SK999",
                explanation="Some project evidence.",
                database_path=self.database_path,
            )

    def test_evidence_from_wrong_candidate_is_rejected(self):
        assignment_id = assign_project(
            candidate_id="candidate-1",
            project_id="PRJ001",
            target_role="Data Analyst",
            database_path=self.database_path,
        )

        with self.assertRaisesRegex(ValueError, "does not belong"):
            submit_project_skill_evidence(
                assignment_id=assignment_id,
                candidate_id="candidate-2",
                skill_id="SK001",
                explanation="Some project evidence.",
                database_path=self.database_path,
            )

    def test_skill_not_in_assigned_project_is_rejected(self):
        assignment_id = assign_project(
            candidate_id="candidate-1",
            project_id="PRJ001",
            target_role="Data Analyst",
            database_path=self.database_path,
        )

        with self.assertRaisesRegex(ValueError, "not listed for project"):
            submit_project_skill_evidence(
                assignment_id=assignment_id,
                candidate_id="candidate-1",
                skill_id="SK003",
                explanation="Some project evidence.",
                database_path=self.database_path,
            )

    def test_unknown_assignment_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown project assignment"):
            submit_project_skill_evidence(
                assignment_id=99999,
                candidate_id="candidate-1",
                skill_id="SK001",
                explanation="Some project evidence.",
                database_path=self.database_path,
            )

    def test_empty_explanation_is_rejected(self):
        assignment_id = assign_project(
            candidate_id="candidate-1",
            project_id="PRJ001",
            target_role="Data Analyst",
            database_path=self.database_path,
        )

        with self.assertRaisesRegex(ValueError, "explanation"):
            submit_project_skill_evidence(
                assignment_id=assignment_id,
                candidate_id="candidate-1",
                skill_id="SK001",
                explanation="   ",
                database_path=self.database_path,
            )



if __name__ == "__main__":
    unittest.main(verbosity=2)
