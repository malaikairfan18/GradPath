from pathlib import Path
import pandas as pd

BASE = Path("data/processed")

JOBS_FILE = BASE / "jobs_seniority_analyzed.csv"
MATCHES_FILE = BASE / "job_skill_matches_baseline_relevant.csv"
LOCATION_FILE = BASE / "location_salary_quality_detail.csv"
PRIORITY_FILE = BASE / "skill_priority_scores.csv"
FREQUENCY_FILE = BASE / "skill_frequency_overall.csv"
ROLE_COMPARISON_FILE = BASE / "skill_role_comparison.csv"

OUTPUT_FILE = BASE / "jobs_market_intelligence.csv"
RELEVANT_OUTPUT_FILE = BASE / "jobs_market_intelligence_relevant.csv"
REPORT_FILE = BASE / "phase2_market_intelligence_report.md"
DICTIONARY_FILE = BASE / "phase2_data_dictionary.csv"


def require_columns(df, columns, filename):
    missing = set(columns) - set(df.columns)
    if missing:
        raise ValueError(f"{filename} is missing columns: {sorted(missing)}")


def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return pd.read_csv(path)


def main():
    jobs = read_csv(JOBS_FILE)
    matches = read_csv(MATCHES_FILE)
    location = read_csv(LOCATION_FILE)
    priorities = read_csv(PRIORITY_FILE)
    frequencies = read_csv(FREQUENCY_FILE)
    comparison = read_csv(ROLE_COMPARISON_FILE)

    require_columns(
        jobs,
        [
            "job_id", "role_category", "job_title", "normalized_title",
            "title_family", "role_relevance", "seniority_level",
            "seniority_reason", "location", "salary_min", "salary_max",
        ],
        JOBS_FILE.name,
    )
    require_columns(
        matches,
        ["job_id", "skill_name", "role_category", "role_relevance"],
        MATCHES_FILE.name,
    )
    require_columns(
        location,
        [
            "job_id", "location_region", "salary_quality_status",
            "salary_quality_flags",
        ],
        LOCATION_FILE.name,
    )

    # Core job table: one record per collected listing.
    if jobs["job_id"].isna().any() or jobs["job_id"].duplicated().any():
        raise ValueError("Core jobs contain missing or duplicate job IDs.")

    if len(jobs) != 312:
        raise ValueError(f"Expected 312 collected jobs; found {len(jobs)}.")

    relevant_ids = set(
        jobs.loc[jobs["role_relevance"].eq("relevant"), "job_id"]
    )
    if len(relevant_ids) != 251:
        raise ValueError(
            f"Expected 251 relevant jobs; found {len(relevant_ids)}."
        )

    if location["job_id"].isna().any() or location["job_id"].duplicated().any():
        raise ValueError("Location/salary detail must have unique, non-missing IDs.")

    if not set(location["job_id"]).issubset(relevant_ids):
        raise ValueError("Location/salary detail contains non-relevant job IDs.")

    # Keep only the location/salary fields not already present in the core table.
    location_fields = location[
        [
            "job_id", "location_region", "salary_quality_status",
            "salary_quality_flags",
        ]
    ].copy()

    # A left join preserves every collected job.
    master = jobs.merge(
        location_fields,
        on="job_id",
        how="left",
        validate="one_to_one",
        indicator="_location_merge",
    )

    if len(master) != len(jobs):
        raise ValueError("Location join unexpectedly changed the job row count.")

    master["location_salary_analysis_available"] = (
        master["_location_merge"].eq("both")
    )
    master = master.drop(columns="_location_merge")

    # Skill evidence is many-to-one aggregated before joining to jobs.
    # This avoids multiplying job rows when a listing matches several skills.
    if matches["job_id"].isna().any():
        raise ValueError("Skill matches contain missing job IDs.")

    if not set(matches["job_id"]).issubset(relevant_ids):
        raise ValueError("Relevant skill-match file contains non-relevant job IDs.")

    if matches.duplicated(["job_id", "skill_name"]).any():
        raise ValueError("Duplicate job-skill pairs found in relevant matches.")

    skill_agg = (
        matches.groupby("job_id")
        .agg(
            detected_skill_count=("skill_name", "nunique"),
            detected_skills=(
                "skill_name",
                lambda values: " | ".join(sorted(set(values.dropna().astype(str))))
            ),
        )
        .reset_index()
    )

    master = master.merge(
        skill_agg,
        on="job_id",
        how="left",
        validate="one_to_one",
    )

    master["detected_skill_count"] = (
        master["detected_skill_count"].fillna(0).astype(int)
    )
    master["detected_skills"] = master["detected_skills"].fillna("")

    # Skills must never be attached to uncertain or irrelevant listings.
    non_relevant_with_skills = master[
        ~master["role_relevance"].eq("relevant")
        & master["detected_skill_count"].gt(0)
    ]
    if not non_relevant_with_skills.empty:
        raise ValueError("Non-relevant jobs unexpectedly have attached skills.")

    relevant_master = master[master["role_relevance"].eq("relevant")].copy()

    if len(master) != 312 or master["job_id"].nunique() != 312:
        raise ValueError("Final master dataset failed 312-row uniqueness check.")

    if len(relevant_master) != 251:
        raise ValueError("Final relevant dataset failed 251-row check.")

    # Save the final tables.
    master.to_csv(OUTPUT_FILE, index=False)
    relevant_master.to_csv(RELEVANT_OUTPUT_FILE, index=False)

    # Build a data dictionary from the actual output columns.
    descriptions = {
        "job_id": "Unique source listing identifier.",
        "role_category": "Role associated with the collection query.",
        "role_relevance": "Title-based relevance classification; not a guarantee of full job fit.",
        "normalized_title": "Standardized job-title representation.",
        "title_family": "Broad job-title family.",
        "seniority_level": "Rule-based seniority classification from the title.",
        "seniority_reason": "Explanation of the seniority rule applied.",
        "location_region": "Heuristically inferred broad region; may be missing for non-relevant jobs.",
        "salary_quality_status": "Outcome of basic salary plausibility checks.",
        "salary_quality_flags": "Reasons a salary record was flagged for review.",
        "location_salary_analysis_available": "Whether a relevant job has a location/salary quality record.",
        "detected_skill_count": "Number of distinct skills detected in the available description text.",
        "detected_skills": "Distinct detected skills joined with a pipe separator.",
        "description": "Source job description, which may be truncated.",
        "description_clean": "Cleaned description text, if present in the source table.",
        "salary_min": "Source-provided minimum salary; pay period is not verified.",
        "salary_max": "Source-provided maximum salary; pay period is not verified.",
        "salary_is_predicted": "Source-provided predicted-salary indicator.",
    }

    dictionary = pd.DataFrame({
        "column_name": master.columns,
        "description": [
            descriptions.get(
                column,
                "Source field retained from the job collection or preprocessing pipeline."
            )
            for column in master.columns
        ],
    })
    dictionary.to_csv(DICTIONARY_FILE, index=False)

    skill_jobs = int(master["detected_skill_count"].gt(0).sum())
    relevant_skill_jobs = int(
        relevant_master["detected_skill_count"].gt(0).sum()
    )
    relevant_no_skill = len(relevant_master) - relevant_skill_jobs
    salary_review = int(
        relevant_master["salary_quality_status"].eq("Needs review").sum()
    )

    role_counts = (
        relevant_master["role_category"].value_counts().sort_index()
    )
    relevance_counts = master["role_relevance"].value_counts().sort_index()
    seniority_counts = (
        relevant_master["seniority_level"].value_counts().sort_index()
    )

    report = [
        "# GradPath Phase 2 — Market Intelligence",
        "",
        "## Dataset overview",
        f"- Collected listings: {len(master)}",
        f"- Unique job IDs: {master['job_id'].nunique()}",
        f"- Relevant listings: {len(relevant_master)}",
        f"- Relevant jobs with at least one detected skill: {relevant_skill_jobs}",
        f"- Relevant jobs with no detected skills: {relevant_no_skill}",
        f"- All jobs with detected skills: {skill_jobs}",
        f"- Relevant jobs flagged for salary review: {salary_review}",
        "",
        "## Relevance labels",
        "```text",
        relevance_counts.to_string(),
        "```",
        "",
        "## Relevant jobs by role",
        "```text",
        role_counts.to_string(),
        "```",
        "",
        "## Relevant jobs by seniority",
        "```text",
        seniority_counts.to_string(),
        "```",
        "",
        "## Skill analysis outputs",
        f"- Relevant job-skill match rows: {len(matches)}",
        f"- Distinct skills in priority table: {priorities['skill_name'].nunique()}",
        f"- Overall skill frequency rows: {len(frequencies)}",
        f"- Role comparison rows: {len(comparison)}",
        "",
        "## Methodology and limitations",
        "- The master dataset has one row per collected listing.",
        "- Job-skill evidence is aggregated from relevant listings only.",
        "- Skills are detected from the collected description text and are not guaranteed to capture all job requirements.",
        "- Many source descriptions are short snippets, so absence of a detected skill is not proof that the job does not require it.",
        "- Relevance and seniority labels are rule-based and should be interpreted as estimates.",
        "- Location-region labels are heuristic.",
        "- Salary values are source-provided; pay period and comparability have not been verified.",
        "- The data represents this collected sample, not a census of the UK job market.",
        "",
        "## Final outputs",
        "- `jobs_market_intelligence.csv`: all 312 collected listings.",
        "- `jobs_market_intelligence_relevant.csv`: the 251 relevant listings.",
        "- `phase2_data_dictionary.csv`: column descriptions.",
        "- `phase2_market_intelligence_report.md`: summary and limitations.",
        "",
        "## Separate analytical tables retained",
        "- `job_skill_matches_baseline_relevant.csv`",
        "- `skill_frequency_overall.csv`",
        "- `skill_frequency_by_role.csv`",
        "- `skill_role_comparison.csv`",
        "- `skill_priority_scores.csv`",
        "- `seniority_distribution.csv`",
        "- `job_region_summary.csv`",
        "- `salary_market_summary.csv`",
        "",
    ]

    REPORT_FILE.write_text("\n".join(report), encoding="utf-8")

    print("Market intelligence dataset built successfully.")
    print("Master rows:", len(master))
    print("Master unique job IDs:", master["job_id"].nunique())
    print("Relevant rows:", len(relevant_master))
    print("Relevant unique job IDs:", relevant_master["job_id"].nunique())
    print("Relevant jobs with detected skills:", relevant_skill_jobs)
    print("Relevant jobs with no detected skills:", relevant_no_skill)
    print("Salary-review listings among relevant jobs:", salary_review)

    print("\nRelevant jobs by role:")
    print(role_counts.to_string())

    print("\nOutput files:")
    for path in [
        OUTPUT_FILE, RELEVANT_OUTPUT_FILE, DICTIONARY_FILE, REPORT_FILE
    ]:
        print(f"- {path} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
