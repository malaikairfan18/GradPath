from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

JOBS_FILE = DATA / "jobs_role_validated.csv"
BASELINE_FILE = DATA / "job_skill_matches_baseline.csv"
OUTPUT_FILE = DATA / "job_skill_matches_baseline_relevant.csv"


def main():
    jobs = pd.read_csv(JOBS_FILE, dtype={"job_id": str})
    matches = pd.read_csv(BASELINE_FILE, dtype={"job_id": str})

    required_jobs = {"job_id", "role_category", "role_relevance"}
    required_matches = {
        "job_id", "skill_id", "skill_name", "role_category"
    }

    if not required_jobs.issubset(jobs.columns):
        raise ValueError(
            f"Missing job columns: {required_jobs - set(jobs.columns)}"
        )

    if not required_matches.issubset(matches.columns):
        raise ValueError(
            f"Missing match columns: {required_matches - set(matches.columns)}"
        )

    if jobs["job_id"].isna().any() or matches["job_id"].isna().any():
        raise ValueError("Missing job IDs detected.")

    if jobs["job_id"].duplicated().any():
        raise ValueError("Validated jobs contain duplicate job IDs.")

    if matches[["skill_id", "skill_name", "role_category"]].isna().any().any():
        raise ValueError("Baseline matches contain missing required values.")

    if matches.duplicated(["job_id", "skill_id"]).any():
        raise ValueError("Baseline contains duplicate job-skill pairs.")

    job_lookup = jobs[
        ["job_id", "role_category", "role_relevance"]
    ].rename(columns={
        "role_category": "validated_role",
        "role_relevance": "validated_relevance",
    })

    checked = matches.merge(
        job_lookup,
        on="job_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    if checked["_merge"].ne("both").any():
        missing_ids = checked.loc[
            checked["_merge"].ne("both"), "job_id"
        ].unique().tolist()
        raise ValueError(
            f"Baseline contains job IDs missing from validated jobs: {missing_ids[:10]}"
        )

    if not checked["role_category"].eq(checked["validated_role"]).all():
        raise ValueError("Role categories disagree with validated job records.")

    relevant = checked.loc[
        checked["validated_relevance"].eq("relevant")
    ].copy()

    relevant = relevant.drop(
        columns=["validated_role", "validated_relevance", "_merge"]
    )

    if relevant.duplicated(["job_id", "skill_id"]).any():
        raise ValueError("Duplicate job-skill pairs found after filtering.")

    relevant_job_count = jobs.loc[
        jobs["role_relevance"].eq("relevant"), "job_id"
    ].nunique()

    if relevant_job_count != 251:
        raise ValueError(
            f"Expected 251 unique relevant jobs; found {relevant_job_count}."
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    relevant.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print("=" * 55)
    print("RELEVANT SKILL MATCH FILTER COMPLETE")
    print("=" * 55)
    print(f"Baseline match rows: {len(matches)}")
    print(f"Relevant jobs: {relevant_job_count}")
    print(f"Relevant match rows: {len(relevant)}")
    print(f"Unique jobs with detected skills: {relevant['job_id'].nunique()}")
    print(f"Unique skills detected: {relevant['skill_id'].nunique()}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
