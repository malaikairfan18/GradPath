from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

JOBS_FILE = PROCESSED / "jobs_role_validated.csv"
MATCHES_FILE = PROCESSED / "job_skill_matches_baseline_relevant.csv"

OUT_OVERALL = PROCESSED / "skill_frequency_overall.csv"
OUT_ROLE = PROCESSED / "skill_frequency_by_role.csv"
OUT_REPORT = PROCESSED / "skill_frequency_report.md"

EXPECTED_RELEVANT_JOBS = 251

def main():
    jobs = pd.read_csv(JOBS_FILE)
    matches = pd.read_csv(MATCHES_FILE)

    required_jobs = {"job_id", "role_category", "role_relevance"}
    required_matches = {"job_id", "role_category", "skill_id", "skill_name"}

    if not required_jobs.issubset(jobs.columns):
        raise ValueError(f"Missing job columns: {required_jobs - set(jobs.columns)}")
    if not required_matches.issubset(matches.columns):
        raise ValueError(f"Missing match columns: {required_matches - set(matches.columns)}")

    jobs["job_id"] = jobs["job_id"].astype(str)
    matches["job_id"] = matches["job_id"].astype(str)

    relevant = jobs.loc[jobs["role_relevance"].eq("relevant")].copy()

    if relevant["job_id"].duplicated().any():
        raise ValueError("Relevant jobs contain duplicate job IDs; investigate before counting.")

    if len(relevant) != EXPECTED_RELEVANT_JOBS:
        raise ValueError(
            f"Expected {EXPECTED_RELEVANT_JOBS} relevant jobs, found {len(relevant)}."
        )

    if matches[["job_id", "skill_id"]].isna().any().any():
        raise ValueError("Match file contains missing job IDs or skill IDs.")

    if matches["skill_name"].isna().any():
        raise ValueError("Match file contains missing skill names.")

    # Every match must belong to a relevant job and have the same role label.
    job_roles = relevant[["job_id", "role_category"]].rename(
        columns={"role_category": "validated_role"}
    )
    checked = matches.merge(job_roles, on="job_id", how="left", validate="many_to_one")

    if checked["validated_role"].isna().any():
        raise ValueError("Some skill matches do not belong to relevant jobs.")

    if not checked["role_category"].eq(checked["validated_role"]).all():
        raise ValueError("Role labels disagree between job and skill-match files.")

    # Denominators: all relevant jobs, including jobs with no detected skill.
    total_jobs = relevant["job_id"].nunique()
    jobs_by_role = (
        relevant.groupby("role_category")["job_id"]
        .nunique()
        .to_dict()
    )

    # Overall frequency: one job can contribute at most once to each skill.
    overall = (
        matches.groupby(["skill_id", "skill_name"], as_index=False)
        .agg(
            match_count=("job_id", "size"),
            jobs_with_skill=("job_id", "nunique"),
            roles_with_skill=("role_category", "nunique"),
        )
    )
    overall["relevant_jobs_total"] = total_jobs
    overall["observed_job_frequency_pct"] = (
        overall["jobs_with_skill"] / total_jobs * 100
    ).round(2)
    overall = overall.sort_values(
        ["jobs_with_skill", "match_count", "skill_name"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    overall.insert(0, "overall_rank", range(1, len(overall) + 1))

    # Role-specific frequency: denominator is all relevant jobs in that role.
    role_frequency = (
        matches.groupby(["role_category", "skill_id", "skill_name"], as_index=False)
        .agg(
            match_count=("job_id", "size"),
            jobs_with_skill=("job_id", "nunique"),
        )
    )
    role_frequency["relevant_jobs_in_role"] = (
        role_frequency["role_category"].map(jobs_by_role)
    )
    role_frequency["observed_job_frequency_pct"] = (
        role_frequency["jobs_with_skill"]
        / role_frequency["relevant_jobs_in_role"]
        * 100
    ).round(2)

    role_frequency = role_frequency.sort_values(
        ["role_category", "jobs_with_skill", "match_count", "skill_name"],
        ascending=[True, False, False, True],
    ).reset_index(drop=True)
    role_frequency["role_rank"] = (
        role_frequency.groupby("role_category").cumcount() + 1
    )
    role_frequency = role_frequency[
        [
            "role_category",
            "role_rank",
            "skill_id",
            "skill_name",
            "match_count",
            "jobs_with_skill",
            "relevant_jobs_in_role",
            "observed_job_frequency_pct",
        ]
    ]

    PROCESSED.mkdir(parents=True, exist_ok=True)
    overall.to_csv(OUT_OVERALL, index=False)
    role_frequency.to_csv(OUT_ROLE, index=False)

    role_summary = (
        relevant.groupby("role_category")["job_id"]
        .nunique()
        .sort_index()
    )
    match_summary = (
        matches.groupby("role_category")["job_id"]
        .agg(match_rows="size", jobs_with_matches="nunique")
        .sort_index()
    )

    report = [
        "# GradPath Phase 2 Day 2 — Skill Frequency Analysis",
        "",
        "## Purpose",
        "",
        "Measure how frequently baseline skills were detected in relevant "
        "Data Analyst and Data Scientist job postings collected from Adzuna.",
        "",
        "## Dataset coverage",
        "",
        f"- Collected jobs: {len(jobs)}",
        f"- Relevant jobs: {len(relevant)}",
        f"- Baseline skill-match rows: {len(matches)}",
        f"- Distinct skills observed in matches: {overall['skill_id'].nunique()}",
        f"- Relevant jobs with at least one detected baseline skill: "
        f"{matches['job_id'].nunique()}",
        "",
        "### Relevant jobs by role",
        "",
        "| Role | Relevant jobs | Match rows | Jobs with at least one match |",
        "|---|---:|---:|---:|",
    ]

    for role, count in role_summary.items():
        rows = int(match_summary.loc[role, "match_rows"]) if role in match_summary.index else 0
        with_matches = int(match_summary.loc[role, "jobs_with_matches"]) if role in match_summary.index else 0
        report.append(f"| {role} | {count} | {rows} | {with_matches} |")

    report.extend([
        "",
        "## Top 10 skills overall",
        "",
        "| Rank | Skill | Jobs with skill | Relevant jobs | Observed frequency (%) | Match rows |",
        "|---:|---|---:|---:|---:|---:|",
    ])

    for row in overall.head(10).itertuples(index=False):
        report.append(
            f"| {row.overall_rank} | {row.skill_name} | {row.jobs_with_skill} "
            f"| {row.relevant_jobs_total} | {row.observed_job_frequency_pct:.2f} "
            f"| {row.match_count} |"
        )

    report.extend([
        "",
        "## Methodology and interpretation",
        "",
        "- A skill's `match_count` is the number of rows in the extracted match file.",
        "- `jobs_with_skill` counts distinct job IDs for that skill.",
        "- Overall frequency divides distinct jobs with the detected skill by all relevant jobs.",
        "- Role-specific frequency divides by all relevant jobs in that role.",
        "- Rankings prioritize distinct jobs with the detected skill; match count and skill name break ties.",
        "- These are observed frequencies in the collected sample, not estimates of the entire UK job market.",
        "- Adzuna descriptions may be snippets. A skill not detected is not proof that the job does not require it.",
        "- The baseline vocabulary is limited to 31 skills derived from O*NET and ESCO. Unlisted skills cannot be measured here.",
        "- Frequency measures observed mentions/detections, not skill importance, proficiency, or causation.",
        "- The dataset can contain multiple skills per job, so match-row counts should not be summed as unique jobs.",
        "",
        "## Validation",
        "",
        "- Relevant job IDs are unique.",
        "- Every match maps to a relevant job.",
        "- Role labels agree between the job and match datasets.",
        "- Missing job IDs, skill IDs, and skill names are rejected.",
        "- The relevant-job count is checked against the Day 1 checkpoint (251 jobs); match-row counts are derived from the current filtered dataset.",
        "",
        "## Output files",
        "",
        "- `skill_frequency_overall.csv`",
        "- `skill_frequency_by_role.csv`",
        "- `skill_frequency_report.md`",
        "",
    ])

    OUT_REPORT.write_text("\n".join(report), encoding="utf-8")

    print("DAY 2 ANALYSIS COMPLETE")
    print(f"Collected jobs: {len(jobs)}")
    print(f"Relevant jobs: {len(relevant)}")
    print(f"Skill-match rows: {len(matches)}")
    print(f"Distinct detected skills: {overall['skill_id'].nunique()}")
    print(f"Jobs with at least one detected skill: {matches['job_id'].nunique()}")
    print("\nRelevant jobs by role:")
    print(role_summary.to_string())
    print("\nTop 10 skills overall:")
    print(overall.head(10).to_string(index=False))
    print("\nFiles created:")
    print(OUT_OVERALL.relative_to(ROOT))
    print(OUT_ROLE.relative_to(ROOT))
    print(OUT_REPORT.relative_to(ROOT))

if __name__ == "__main__":
    main()
