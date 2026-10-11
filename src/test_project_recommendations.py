"""Automated tests for GradPath project recommendations."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gradpath.project_recommendations import (
    PROJECT_CATALOGUE_PATH,
    VOCABULARY_PATH,
    recommend_projects,
)


class ProjectRecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocabulary = pd.read_csv(VOCABULARY_PATH).fillna("")
        cls.projects = pd.read_csv(
            PROJECT_CATALOGUE_PATH,
            dtype=str,
            keep_default_na=False,
        )

    def make_gap(
        self,
        skill_id="SK001",
        skill_name="Python",
        role="Data Analyst",
        status="potential_gap",
        market_jobs=10,
        market_total=100,
        priority=10.0,
        market_status="observed_matches",
    ):
        return {
            "target_role": role,
            "skill_id": skill_id,
            "skill_name": skill_name,
            "candidate_status": status,
            "priority_score": priority,
            "market_priority_rank": 1 if market_jobs > 0 else None,
            "market_jobs_with_skill": market_jobs,
            "market_relevant_jobs_total": market_total,
            "market_evidence_level": "observed" if market_jobs > 0 else "limited",
            "market_evidence_status": market_status,
            "esco_mapping_status": "not_mapped",
            "esco_relationship": "none",
            "esco_label": None,
            "extraction_incomplete": False,
        }

    def recommend(self, gaps, role="Data Analyst", **kwargs):
        return recommend_projects(
            skill_gaps=gaps,
            target_role=role,
            projects=kwargs.pop("projects", self.projects),
            vocabulary=kwargs.pop("vocabulary", self.vocabulary),
            **kwargs,
        )

    def test_real_catalogue_loads_and_returns_python_projects(self):
        results = self.recommend([self.make_gap()])

        self.assertEqual(
            {item["project_id"] for item in results},
            {"PRJ001", "PRJ004"},
        )

    def test_unknown_market_evidence_does_not_crash_or_become_zero(self):
        gap = self.make_gap(
            market_jobs=0,
            priority=0.0,
            market_status="no_observed_matches",
        )

        results = self.recommend([gap])

        self.assertTrue(results)
        for item in results:
            self.assertIsNone(item["mean_market_priority"])
            self.assertFalse(item["market_priority_used_for_ranking"])
            self.assertNotIn("SK001", item["market_supported_skill_ids"])
            self.assertIn(
                "does not mean these skills have no real-world demand",
                item["explanation"],
            )

    def test_recommendations_are_deterministic(self):
        gaps = [
            self.make_gap(),
            self.make_gap(
                skill_id="SK006",
                skill_name="Data Analysis",
                market_jobs=0,
                priority=0.0,
                market_status="no_observed_matches",
            ),
        ]

        first = self.recommend(gaps)
        second = self.recommend(gaps)

        self.assertEqual(first, second)

    def test_verified_skills_are_excluded_by_default(self):
        gap = self.make_gap(status="verified_skill_present")

        self.assertEqual(self.recommend([gap]), [])

    def test_maintenance_can_include_verified_skills(self):
        gap = self.make_gap(status="verified_skill_present")

        results = self.recommend([gap], include_maintenance=True)

        self.assertTrue(results)
        self.assertTrue(
            all("SK001" in item["covered_skill_ids"] for item in results)
        )

    def test_empty_gap_list_returns_no_recommendations(self):
        self.assertEqual(self.recommend([]), [])

    def test_hour_limit_filters_projects(self):
        results = self.recommend([self.make_gap()], max_hours=15)

        self.assertTrue(results)
        self.assertTrue(
            all(item["estimated_hours"] <= 15 for item in results)
        )
        self.assertEqual(
            {item["project_id"] for item in results},
            {"PRJ001"},
        )

    def test_difficulty_limit_filters_projects(self):
        results = self.recommend(
            [self.make_gap()],
            max_difficulty="Beginner",
        )

        self.assertTrue(results)
        self.assertTrue(
            all(item["difficulty"] == "Beginner" for item in results)
        )

    def test_project_role_filter_is_respected(self):
        gap = self.make_gap(
            skill_id="SK010",
            skill_name="Statistical Modeling",
            role="Data Scientist",
        )

        results = self.recommend([gap], role="Data Scientist")

        self.assertTrue(results)
        self.assertTrue(
            all(item["project_roles"] in {"Both", "Data Scientist"} for item in results)
        )
        self.assertIn("PRJ005", {item["project_id"] for item in results})

    def test_duplicate_project_ids_are_rejected(self):
        projects = pd.concat(
            [self.projects, self.projects.iloc[[0]]],
            ignore_index=True,
        )

        with self.assertRaisesRegex(ValueError, "Duplicate project_id"):
            self.recommend([self.make_gap()], projects=projects)

    def test_unknown_project_skill_is_rejected(self):
        projects = self.projects.copy()
        projects.loc[0, "skill_ids"] = "SK999"

        with self.assertRaisesRegex(ValueError, "Unknown skill ID"):
            self.recommend([self.make_gap()], projects=projects)

    def test_role_incompatible_project_skill_is_rejected(self):
        projects = self.projects.copy()
        row = projects.index[projects["project_id"] == "PRJ003"][0]
        projects.loc[row, "skill_ids"] = "SK003;SK010"

        with self.assertRaisesRegex(ValueError, "not compatible"):
            self.recommend([self.make_gap()], projects=projects)

    def test_role_incompatible_prerequisite_is_rejected(self):
        projects = self.projects.copy()
        row = projects.index[projects["project_id"] == "PRJ003"][0]
        projects.loc[row, "prerequisites"] = "SK010"

        with self.assertRaisesRegex(ValueError, "Prerequisite"):
            self.recommend([self.make_gap()], projects=projects)

    def test_duplicate_gap_skill_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate skill gap"):
            self.recommend([self.make_gap(), self.make_gap()])

    def test_unknown_gap_skill_is_rejected(self):
        gap = self.make_gap(skill_id="SK999", skill_name="Unknown")

        with self.assertRaisesRegex(ValueError, "Unknown skill_id"):
            self.recommend([gap])

    def test_project_completion_never_marks_skill_verified(self):
        results = self.recommend([self.make_gap()])

        self.assertTrue(results)
        for item in results:
            self.assertEqual(item["evidence_type_for_tracking"], "project")
            self.assertEqual(item["initial_verification_status"], "unverified")

    def test_invalid_target_role_is_rejected(self):
        with self.assertRaises(ValueError):
            self.recommend([self.make_gap()], role="Data Engineer")

    def test_invalid_max_hours_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "max_hours"):
            self.recommend([self.make_gap()], max_hours=0)

    def test_invalid_difficulty_limit_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "max_difficulty"):
            self.recommend([self.make_gap()], max_difficulty="Expert")


    def test_multiskill_project_covers_multiple_gaps(self):
        gaps = [
            self.make_gap(),
            self.make_gap(
                skill_id="SK006",
                skill_name="Data Analysis",
                priority=20.0,
            ),
        ]

        results = self.recommend(gaps)

        self.assertTrue(results)
        best = results[0]
        self.assertEqual(best["project_id"], "PRJ001")
        self.assertEqual(best["covered_gap_count"], 2)
        self.assertEqual(
            set(best["covered_skill_ids"]),
            {"SK001", "SK006"},
        )

    def test_missing_required_gap_field_is_rejected(self):
        gap = self.make_gap()
        gap.pop("skill_name")

        with self.assertRaises(ValueError):
            self.recommend([gap])

    def test_invalid_catalogue_difficulty_is_rejected(self):
        projects = self.projects.copy()
        row = projects.index[projects["project_id"] == "PRJ001"][0]
        projects.loc[row, "difficulty"] = "Expert"

        with self.assertRaises(ValueError):
            self.recommend([self.make_gap()], projects=projects)


if __name__ == "__main__":
    unittest.main(verbosity=2)
