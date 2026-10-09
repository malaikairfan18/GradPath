from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

JOBS_FILE = DATA / "jobs_role_validated.csv"
MATCHES_FILE = DATA / "job_skill_matches_baseline_relevant.csv"
OUT_CSV = DATA / "skill_role_comparison.csv"
OUT_REPORT = DATA / "skill_role_comparison_report.md"

ROLES = ["Data Analyst", "Data Scientist"]


def main():
    jobs = pd.read_csv(JOBS_FILE)
    matches = pd.read_csv(MATCHES_FILE)

    relevant = jobs.loc[jobs["role_relevance"].eq("relevant")].copy()
    relevant["job_id"] = relevant["job_id"].astype(str)
    matches["job_id"] = matches["job_id"].astype(str)

    if len(relevant) != 251:
        raise ValueError(
            f"Expected 251 relevant jobs, found {len(relevant)}."
        )

    if relevant["job_id"].duplicated().any():
        raise ValueError("Duplicate relevant job IDs detected.")

    if matches[["job_id", "skill_id", "skill_name", "role_category"]].isna().any().any():
        raise ValueError("Missing values in required skill-match columns.")

    if not set(matches["role_category"]).issubset(set(ROLES)):
        raise ValueError("Unexpected role category found.")

    role_map = relevant[["job_id", "role_category"]].rename(
        columns={"role_category": "validated_role"}
    )
    checked = matches.merge(
        role_map, on="job_id", how="left", validate="many_to_one"
    )

    if checked["validated_role"].isna().any():
        raise ValueError("Some matches do not map to relevant jobs.")

    if not checked["role_category"].eq(checked["validated_role"]).all():
        raise ValueError("Role labels disagree between input datasets.")

    if matches.duplicated(["job_id", "skill_id"]).any():
        raise ValueError("Duplicate job-skill pairs detected.")

    denominators = (
        relevant.groupby("role_category")["job_id"].nunique().to_dict()
    )

    if any(role not in denominators for role in ROLES):
        raise ValueError("One or more expected roles are missing.")

    # Build the union of skills observed in either role.
    skills = (
        matches[["skill_id", "skill_name"]]
        .drop_duplicates()
        .sort_values(["skill_id", "skill_name"])
    )

    if skills["skill_id"].duplicated().any():
        raise ValueError("A skill ID maps to multiple skill names.")

    # Count distinct jobs per skill and role.
    counts = (
        matches.groupby(["skill_id", "role_category"])["job_id"]
        .nunique()
        .unstack(fill_value=0)
        .reindex(columns=ROLES, fill_value=0)
    )

    result = skills.set_index("skill_id").join(counts, how="left").fillna(0)

    result["data_analyst_jobs"] = result["Data Analyst"].astype(int)
    result["data_scientist_jobs"] = result["Data Scientist"].astype(int)
    result["data_analyst_total_jobs"] = denominators["Data Analyst"]
    result["data_scientist_total_jobs"] = denominators["Data Scientist"]

    result["data_analyst_frequency_pct"] = (
        result["data_analyst_jobs"]
        / denominators["Data Analyst"] * 100
    ).round(2)

    result["data_scientist_frequency_pct"] = (
        result["data_scientist_jobs"]
        / denominators["Data Scientist"] * 100
    ).round(2)

    result["difference_percentage_points"] = (
        result["data_scientist_frequency_pct"]
        - result["data_analyst_frequency_pct"]
    ).round(2)

    result["higher_observed_frequency"] = result[
        "difference_percentage_points"
    ].map(
        lambda x: "Data Scientist" if x > 0
        else "Data Analyst" if x < 0
        else "Equal"
    )

    result["observed_in_both_roles"] = (
        (result["data_analyst_jobs"] > 0)
        & (result["data_scientist_jobs"] > 0)
    )

    result = result.reset_index()
    result = result.rename(
        columns={
            "index": "skill_id",
            "skill_name": "skill_name",
        }
    )

    result = result.sort_values(
        ["difference_percentage_points", "skill_name"],
        ascending=[False, True],
    ).reset_index(drop=True)

    result.insert(0, "comparison_rank", range(1, len(result) + 1))

    columns = [
        "comparison_rank",
        "skill_id",
        "skill_name",
        "data_analyst_jobs",
        "data_analyst_total_jobs",
        "data_analyst_frequency_pct",
        "data_scientist_jobs",
        "data_scientist_total_jobs",
        "data_scientist_frequency_pct",
        "difference_percentage_points",
        "higher_observed_frequency",
        "observed_in_both_roles",
    ]
    result = result[columns]

    result.to_csv(OUT_CSV, index=False)

    da_only = result[
        (result["data_analyst_jobs"] > 0)
        & (result["data_scientist_jobs"] == 0)
    ]
    ds_only = result[
        (result["data_scientist_jobs"] > 0)
        & (result["data_analyst_jobs"] == 0)
    ]
    both = result[result["observed_in_both_roles"]]

    lines = [
        "# GradPath Phase 2 Day 3 — Role Skill Comparison",
        "",
        "## Objective",
        "",
        "Compare the observed frequency of baseline skills in relevant "
        "Data Analyst and Data Scientist job postings.",
        "",
        "## Dataset coverage",
        "",
        f"- Relevant Data Analyst jobs: {denominators['Data Analyst']}",
        f"- Relevant Data Scientist jobs: {denominators['Data Scientist']}",
        f"- Skill-match rows: {len(matches)}",
        f"- Distinct observed skills: {len(result)}",
        f"- Skills detected in both roles: {len(both)}",
        f"- Skills detected only in Data Analyst jobs: {len(da_only)}",
        f"- Skills detected only in Data Scientist jobs: {len(ds_only)}",
        "",
        "## Largest observed differences",
        "",
        "Positive differences mean a higher observed frequency in Data "
        "Scientist jobs; negative differences mean a higher frequency in "
        "Data Analyst jobs.",
        "",
        "| Skill | Data Analyst jobs | DA frequency (%) | Data Scientist jobs | DS frequency (%) | Difference (percentage points) |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    ranked = result.assign(
        absolute_difference=result["difference_percentage_points"].abs()
    ).sort_values(
        ["absolute_difference", "skill_name"],
        ascending=[False, True],
    ).head(10)

    for row in ranked.itertuples(index=False):
        lines.append(
            f"| {row.skill_name} | {row.data_analyst_jobs} "
            f"| {row.data_analyst_frequency_pct:.2f} "
            f"| {row.data_scientist_jobs} "
            f"| {row.data_scientist_frequency_pct:.2f} "
            f"| {row.difference_percentage_points:+.2f} |"
        )

    lines.extend([
        "",
        "## Interpretation and limitations",
        "",
        "- Frequencies use distinct jobs, not raw match-row counts.",
        "- Each role uses its own relevant-job denominator.",
        "- Percentage-point difference is Data Scientist frequency minus "
        "Data Analyst frequency.",
        "- A zero detected count means no match was found by the baseline "
        "extractor, not that the skill is absent from the role.",
        "- Adzuna descriptions may be snippets, limiting skill detection.",
        "- The analysis covers only the baseline vocabulary grounded in "
        "O*NET and ESCO; other skills cannot appear in this comparison.",
        "- Results are descriptive observations from this sample, not "
        "proof of statistical significance or a complete UK market ranking.",
        "- The higher-frequency label describes this sample only and "
        "should not be interpreted as causal evidence.",
        "",
        "## Output",
        "",
        "- `skill_role_comparison.csv`",
        "- `skill_role_comparison_report.md`",
        "",
    ])

    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("DAY 3 COMPARISON COMPLETE")
    print(f"Relevant jobs: {len(relevant)}")
    print(f"Observed skills compared: {len(result)}")
    print(f"Skills in both roles: {len(both)}")
    print(f"Data Analyst only: {len(da_only)}")
    print(f"Data Scientist only: {len(ds_only)}")
    print("\nLargest role differences:")
    display_columns = [
        "skill_name",
        "data_analyst_frequency_pct",
        "data_scientist_frequency_pct",
        "difference_percentage_points",
    ]
    display = ranked[display_columns].copy()
    display = display.rename(columns={
        "skill_name": "Skill",
        "data_analyst_frequency_pct": "DA (%)",
        "data_scientist_frequency_pct": "DS (%)",
        "difference_percentage_points": "Difference (pp)",
    })
    print(display.to_string(
        index=False,
        formatters={
            "DA (%)": lambda value: f"{value:.2f}",
            "DS (%)": lambda value: f"{value:.2f}",
            "Difference (pp)": lambda value: f"{value:+.2f}",
        },
        col_space=8,
    ))
    print("\nCreated:")
    print(OUT_CSV)
    print(OUT_REPORT)


if __name__ == "__main__":
    main()
