import csv
import sqlite3
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from gradpath.progress_tracker import (
    initialize_database,
    record_assessment_attempt,
    record_skill_evidence,
)
from gradpath.readiness_scoring import score_readiness


@contextmanager
def managed_connection(database_path):
    """Commit successful test transactions and always close SQLite."""
    connection = sqlite3.connect(database_path)
    try:
        with connection:
            yield connection
    finally:
        connection.close()



class ReadinessScoringTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.database_path = self.root / "progress.db"
        self.vocabulary_path = self.root / "skills.csv"

        with self.vocabulary_path.open(
            "w", encoding="utf-8", newline=""
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "skill_id", "skill_name", "skill_category",
                    "role", "source", "aliases",
                ],
            )
            writer.writeheader()
            writer.writerows([
                {
                    "skill_id": "SK001", "skill_name": "Python",
                    "skill_category": "Programming", "role": "Both",
                    "source": "test", "aliases": "",
                },
                {
                    "skill_id": "SK002", "skill_name": "SQL",
                    "skill_category": "Database", "role": "Data Analyst",
                    "source": "test", "aliases": "",
                },
                {
                    "skill_id": "SK003", "skill_name": "Machine Learning",
                    "skill_category": "ML", "role": "Data Scientist",
                    "source": "test", "aliases": "",
                },
            ])

        initialize_database(self.database_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def score(self, candidate="candidate-1", role="Data Analyst"):
        return score_readiness(
            candidate_id=candidate,
            target_role=role,
            database_path=self.database_path,
            vocabulary_path=self.vocabulary_path,
        )

    def add_evidence(
        self, skill_id, status, candidate="candidate-1",
        evidence_type="portfolio",
    ):
        return record_skill_evidence(
            candidate_id=candidate,
            skill_id=skill_id,
            evidence_type=evidence_type,
            verification_status=status,
            database_path=self.database_path,
        )

    def add_activity(self, candidate, skill_id, role):
        now = "2026-10-11T12:00:00+00:00"
        with managed_connection(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO learning_activities (
                    candidate_id, resource_id, skill_id, target_role,
                    status, progress_percent, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 'in_progress', 50, ?, ?)
                """,
                (
                    candidate, f"resource-{skill_id}-{role}",
                    skill_id, role, now, now,
                ),
            )
            return cursor.lastrowid

    def test_empty_candidate_has_zero_coverage(self):
        result = self.score()
        self.assertEqual(result["coverage_percent"], 0.0)
        self.assertEqual(result["verified_skill_count"], 0)
        self.assertEqual(result["eligible_skill_count"], 2)
        self.assertEqual(
            result["coverage_status_counts"]["no_recorded_evidence"], 2
        )

    def test_empty_role_vocabulary_returns_no_percentage(self):
        empty_vocabulary = self.root / "empty_vocabulary.csv"
        empty_vocabulary.write_text(
            "skill_id,skill_name,role\n",
            encoding="utf-8",
        )

        report = score_readiness(
            candidate_id="candidate-1",
            target_role="Data Analyst",
            database_path=self.database_path,
            vocabulary_path=empty_vocabulary,
        )

        self.assertIsNone(report["coverage_percent"])
        self.assertEqual(
            report["coverage_calculation_status"],
            "no_eligible_skills",
        )
        self.assertEqual(report["eligible_skill_count"], 0)
        self.assertEqual(report["verified_skill_count"], 0)


    def test_denominator_is_specific_to_role(self):
        analyst = self.score(role="Data Analyst")
        scientist = self.score(role="Data Scientist")
        self.assertEqual(analyst["eligible_skill_count"], 2)
        self.assertEqual(scientist["eligible_skill_count"], 2)
        self.assertEqual(
            {item["skill_id"] for item in analyst["skills"]},
            {"SK001", "SK002"},
        )
        self.assertEqual(
            {item["skill_id"] for item in scientist["skills"]},
            {"SK001", "SK003"},
        )

    def test_only_verified_evidence_counts(self):
        self.add_evidence("SK001", "verified")
        self.add_evidence("SK002", "unverified")
        result = self.score()
        self.assertEqual(result["verified_skill_count"], 1)
        self.assertEqual(result["coverage_percent"], 50.0)

    def test_duplicate_verified_records_count_skill_once(self):
        self.add_evidence("SK001", "verified")
        self.add_evidence("SK001", "verified", evidence_type="assessment")
        result = self.score()
        self.assertEqual(result["verified_skill_count"], 1)
        self.assertEqual(result["coverage_percent"], 50.0)

    def test_verified_and_rejected_evidence_is_conflict(self):
        self.add_evidence("SK001", "verified")
        self.add_evidence("SK001", "rejected")
        result = self.score()
        self.assertEqual(result["verified_skill_count"], 0)
        self.assertEqual(result["evidence_conflict_count"], 1)
        skill = next(item for item in result["skills"]
                     if item["skill_id"] == "SK001")
        self.assertEqual(skill["coverage_status"], "conflicting_evidence")
        self.assertFalse(skill["counts_toward_coverage"])

    def test_rejected_evidence_does_not_count(self):
        self.add_evidence("SK001", "rejected")
        result = self.score()
        self.assertEqual(result["verified_skill_count"], 0)

    def test_candidate_evidence_is_isolated(self):
        self.add_evidence("SK001", "verified", candidate="someone-else")
        result = self.score(candidate="candidate-1")
        self.assertEqual(result["verified_skill_count"], 0)

    def test_assessment_scores_are_separated_by_type(self):
        activity_id = self.add_activity(
            "candidate-1", "SK001", "Data Analyst"
        )
        record_assessment_attempt(
            candidate_id="candidate-1",
            skill_id="SK001",
            assessment_type="quiz",
            score=8,
            max_score=10,
            activity_id=activity_id,
            database_path=self.database_path,
        )
        record_assessment_attempt(
            candidate_id="candidate-1",
            skill_id="SK001",
            assessment_type="coding_exercise",
            score=3,
            max_score=4,
            activity_id=activity_id,
            database_path=self.database_path,
        )
        result = self.score()
        by_type = result["assessments"]["by_type"]
        self.assertEqual(by_type["quiz"]["average_score_percent"], 80.0)
        self.assertEqual(
            by_type["coding_exercise"]["average_score_percent"], 75.0
        )
        self.assertEqual(result["verified_skill_count"], 0)

    def test_scoreless_assessment_is_reported(self):
        activity_id = self.add_activity(
            "candidate-1", "SK001", "Data Analyst"
        )
        record_assessment_attempt(
            candidate_id="candidate-1",
            skill_id="SK001",
            assessment_type="project_evaluation",
            activity_id=activity_id,
            database_path=self.database_path,
        )
        result = self.score()
        evaluation = result["assessments"]["by_type"]["project_evaluation"]
        self.assertEqual(evaluation["attempt_count"], 1)
        self.assertEqual(evaluation["scoreless_attempt_count"], 1)
        self.assertIsNone(evaluation["average_score_percent"])

    def test_unlinked_assessment_is_unattributed(self):
        record_assessment_attempt(
            candidate_id="candidate-1",
            skill_id="SK001",
            assessment_type="quiz",
            score=7,
            max_score=10,
            database_path=self.database_path,
        )
        result = self.score()
        self.assertEqual(
            result["assessments"]["unattributed"]["attempt_count"], 1
        )
        self.assertEqual(
            result["assessments"]["by_type"]["quiz"]["attempt_count"], 0
        )

    def test_other_role_assessment_is_not_in_target_role_average(self):
        activity_id = self.add_activity(
            "candidate-1", "SK001", "Data Scientist"
        )
        record_assessment_attempt(
            candidate_id="candidate-1",
            skill_id="SK001",
            assessment_type="quiz",
            score=10,
            max_score=10,
            activity_id=activity_id,
            database_path=self.database_path,
        )
        result = self.score(role="Data Analyst")
        self.assertEqual(
            result["assessments"]["by_type"]["quiz"]["attempt_count"], 0
        )
        self.assertEqual(result["assessments"]["other_role_attempt_count"], 1)

    def test_database_version_two_is_supported_read_only(self):
        with managed_connection(self.database_path) as connection:
            connection.execute(
                "UPDATE schema_metadata SET value = '2' "
                "WHERE key = 'schema_version'"
            )
        result = self.score()
        self.assertEqual(result["database_schema_version"], 2)

    def test_unsupported_database_version_is_rejected(self):
        with managed_connection(self.database_path) as connection:
            connection.execute(
                "UPDATE schema_metadata SET value = '99' "
                "WHERE key = 'schema_version'"
            )
        with self.assertRaisesRegex(ValueError, "Unsupported database schema"):
            self.score()

    def test_invalid_role_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported target_role"):
            self.score(role="Data Engineer")

    def test_blank_candidate_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "candidate_id"):
            self.score(candidate=" ")

    def test_missing_database_is_rejected_without_creation(self):
        missing = self.root / "does-not-exist.db"
        with self.assertRaises(FileNotFoundError):
            score_readiness(
                "candidate-1", "Data Analyst",
                database_path=missing,
                vocabulary_path=self.vocabulary_path,
            )
        self.assertFalse(missing.exists())

    def test_database_is_not_modified_by_scoring(self):
        with managed_connection(self.database_path) as connection:
            before_version = connection.execute(
                "SELECT value FROM schema_metadata "
                "WHERE key = 'schema_version'"
            ).fetchone()[0]
            before_evidence = connection.execute(
                "SELECT COUNT(*) FROM skill_evidence"
            ).fetchone()[0]

        self.score()

        with managed_connection(self.database_path) as connection:
            after_version = connection.execute(
                "SELECT value FROM schema_metadata "
                "WHERE key = 'schema_version'"
            ).fetchone()[0]
            after_evidence = connection.execute(
                "SELECT COUNT(*) FROM skill_evidence"
            ).fetchone()[0]

        self.assertEqual(before_version, after_version)
        self.assertEqual(before_evidence, after_evidence)

    def test_duplicate_vocabulary_ids_are_rejected(self):
        with self.vocabulary_path.open(
            "a", encoding="utf-8", newline=""
        ) as file:
            writer = csv.writer(file)
            writer.writerow([
                "SK001", "Duplicate Python", "Programming",
                "Both", "test", "",
            ])
        with self.assertRaisesRegex(ValueError, "duplicate skill ID"):
            self.score()


    def test_scoring_is_deterministic(self):
        first_report = score_readiness(
            candidate_id="candidate-1",
            target_role="Data Analyst",
            database_path=self.database_path,
            vocabulary_path=self.vocabulary_path,
        )

        second_report = score_readiness(
            candidate_id="candidate-1",
            target_role="Data Analyst",
            database_path=self.database_path,
            vocabulary_path=self.vocabulary_path,
        )

        self.assertEqual(first_report, second_report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
