
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

VOCAB_FILE = DATA / "initial_skill_vocabulary.csv"
COMPARISON_FILE = DATA / "skill_role_comparison.csv"
MATCHES_FILE = DATA / "job_skill_matches_baseline_relevant.csv"
JOBS_FILE = DATA / "jobs_role_validated.csv"

OUT_FILE = DATA / "skill_priority_scores.csv"
REPORT_FILE = DATA / "skill_priority_report.md"

ROLES = ["Data Analyst", "Data Scientist"]


def evidence_level(count):
    """Describe observed match volume, not statistical certainty."""
    if count == 0:
        return "No detected evidence"
    if count <= 2:
        return "Very limited (1-2 jobs)"
    if count <= 5:
        return "Limited (3-5 jobs)"
    if count <= 10:
        return "Moderate (6-10 jobs)"
    return "Stronger (11+ jobs)"


def main():
    # Load source datasets.
    vocab = pd.read_csv(VOCAB_FILE).fillna("")
    comparison = pd.read_csv(COMPARISON_FILE)
    matches = pd.read_csv(MATCHES_FILE)
    jobs = pd.read_csv(JOBS_FILE)

    # Validate required columns.
    required_vocab = {
        "skill_id",
        "skill_name",
        "skill_category",
        "role",
        "source",
        "aliases",
    }
    required_comparison = {
        "skill_id",
        "data_analyst_jobs",
        "data_analyst_total_jobs",
        "data_analyst_frequency_pct",
        "data_scientist_jobs",
        "data_scientist_total_jobs",
        "data_scientist_frequency_pct",
    }
    required_matches = {
        "job_id",
        "skill_id",
        "role_category",
        "role_relevance",
    }
    required_jobs = {
        "job_id",
        "role_category",
        "role_relevance",
    }

    if not required_vocab.issubset(vocab.columns):
        raise ValueError("Skill vocabulary is missing required columns.")

    if not required_comparison.issubset(comparison.columns):
        raise ValueError("Role comparison file is missing required columns.")

    if not required_matches.issubset(matches.columns):
        raise ValueError("Skill matches file is missing required columns.")

    if not required_jobs.issubset(jobs.columns):
        raise ValueError("Validated jobs file is missing required columns.")

    # Validate taxonomy and identifiers.
    if vocab["skill_id"].duplicated().any():
        raise ValueError("Duplicate skill IDs in vocabulary.")

    if comparison["skill_id"].duplicated().any():
        raise ValueError("Duplicate skill IDs in role comparison.")

    if matches.duplicated(["job_id", "skill_id"]).any():
        raise ValueError("Duplicate job-skill pairs in match data.")

    if jobs["job_id"].duplicated().any():
        raise ValueError("Duplicate job IDs in validated jobs data.")

    allowed_vocab_roles = {"Both", *ROLES}
    unexpected_roles = set(vocab["role"].astype(str)) - allowed_vocab_roles

    if unexpected_roles:
        raise ValueError(
            f"Unexpected vocabulary role values: {unexpected_roles}"
        )

    # Keep only relevant listings and calculate denominators dynamically.
    relevant = jobs.loc[
        jobs["role_relevance"].eq("relevant")
    ].copy()

    relevant["job_id"] = relevant["job_id"].astype(str)
    matches["job_id"] = matches["job_id"].astype(str)
    comparison["skill_id"] = comparison["skill_id"].astype(str)
    vocab["skill_id"] = vocab["skill_id"].astype(str)

    relevant_role_values = set(relevant["role_category"].dropna().unique())

    for role in ROLES:
        if role not in relevant_role_values:
            raise ValueError(f"No relevant jobs found for role: {role}")

    denominators = (
        relevant.groupby("role_category")["job_id"]
        .nunique()
        .to_dict()
    )

    # Validate that all match rows refer to relevant jobs and agree on role.
    role_map = relevant[["job_id", "role_category"]].rename(
        columns={"role_category": "validated_role"}
    )

    checked = matches.merge(
        role_map,
        on="job_id",
        how="left",
        validate="many_to_one",
    )

    if checked["validated_role"].isna().any():
        raise ValueError(
            "Some skill matches do not map to relevant validated jobs."
        )

    if not checked["role_category"].eq(checked["validated_role"]).all():
        raise ValueError(
            "Skill-match role labels disagree with validated job roles."
        )

    if not set(matches["role_category"].dropna().unique()).issubset(set(ROLES)):
        raise ValueError("Unexpected role category in skill-match data.")

    # Validate the comparison denominators against the source jobs.
    for role in ROLES:
        prefix = "data_analyst" if role == "Data Analyst" else "data_scientist"
        expected_total = int(denominators[role])

        observed_totals = comparison[f"{prefix}_total_jobs"].dropna().unique()

        if len(observed_totals) != 1 or int(observed_totals[0]) != expected_total:
            raise ValueError(
                f"Denominator mismatch for {role}: "
                f"expected {expected_total}, found {observed_totals.tolist()}."
            )

    # Build a role-specific row for each applicable vocabulary skill.
    rows = []

    for _, skill in vocab.iterrows():
        applicable_roles = (
            ROLES if skill["role"] == "Both" else [skill["role"]]
        )

        skill_comparison = comparison.loc[
            comparison["skill_id"].eq(skill["skill_id"])
        ]

        if len(skill_comparison) > 1:
            raise ValueError(
                f"Multiple comparison rows for skill {skill['skill_id']}."
            )

        for role in applicable_roles:
            prefix = (
                "data_analyst"
                if role == "Data Analyst"
                else "data_scientist"
            )

            total_jobs = int(denominators[role])

            if not skill_comparison.empty:
                record = skill_comparison.iloc[0]
                jobs_with_skill = int(record[f"{prefix}_jobs"])
            else:
                # No baseline match: retain the skill with a zero count.
                jobs_with_skill = 0

            if not 0 <= jobs_with_skill <= total_jobs:
                raise ValueError(
                    f"Invalid match count for {skill['skill_name']} "
                    f"({role}): {jobs_with_skill}/{total_jobs}."
                )

            # Calculate frequency from the validated source denominator.
            frequency_pct = round(
                jobs_with_skill / total_jobs * 100,
                2,
            )

            # Cross-check the precomputed comparison where available.
            if not skill_comparison.empty:
                recorded_pct = float(
                    skill_comparison.iloc[0][f"{prefix}_frequency_pct"]
                )

                if abs(recorded_pct - frequency_pct) > 0.02:
                    raise ValueError(
                        f"Frequency mismatch for {skill['skill_name']} "
                        f"({role}): comparison={recorded_pct}, "
                        f"recalculated={frequency_pct}."
                    )

            rows.append({
                "skill_id": skill["skill_id"],
                "skill_name": skill["skill_name"],
                "skill_category": skill["skill_category"],
                "taxonomy_role": skill["role"],
                "role_category": role,
                "taxonomy_source": skill["source"],
                "jobs_with_skill": jobs_with_skill,
                "relevant_jobs_total": total_jobs,
                "observed_frequency_pct": frequency_pct,
                "evidence_level": evidence_level(jobs_with_skill),
                "scoring_method": (
                    "Observed frequency: distinct matched jobs "
                    "divided by relevant jobs"
                ),
            })

    result = pd.DataFrame(rows)

    # Check uniqueness before ranking.
    if result.duplicated(["skill_id", "role_category"]).any():
        raise ValueError("Duplicate skill-role pairs in scoring output.")

    # Rank by observed frequency. Ties use count, then skill name.
    result = result.sort_values(
        [
            "role_category",
            "observed_frequency_pct",
            "jobs_with_skill",
            "skill_name",
        ],
        ascending=[True, False, False, True],
    ).reset_index(drop=True)

    result["priority_rank"] = (
        result.groupby("role_category").cumcount() + 1
    )

    columns = [
        "role_category",
        "priority_rank",
        "skill_id",
        "skill_name",
        "skill_category",
        "taxonomy_role",
        "taxonomy_source",
        "jobs_with_skill",
        "relevant_jobs_total",
        "observed_frequency_pct",
        "evidence_level",
        "scoring_method",
    ]

    result = result[columns]

    # Write machine-readable output.
    result.to_csv(OUT_FILE, index=False, encoding="utf-8")

    # Write a human-readable report.
    lines = [
        "# GradPath Skill Priority Report",
        "",
        "## Method",
        "",
        "Skills are ranked separately for Data Analyst and Data Scientist.",
        "Ranking is based on observed frequency in relevant job listings:",
        "distinct jobs with a detected skill match divided by relevant jobs.",
        "Role denominators are calculated from jobs_role_validated.csv.",
        "All vocabulary skills applicable to each role are retained,",
        "including skills with zero detected matches.",
        "",
        "Evidence labels describe the number of detected job matches only.",
        "They do not measure statistical certainty or prove that a skill is",
        "required by the market. Zero matches do not mean a skill is unnecessary.",
        "The baseline matcher uses a fixed vocabulary and limited job-description",
        "text, so skills can be missed.",
        "",
        "Priority rank is a descriptive frequency ranking, not a complete",
        "measure of educational value, skill difficulty, or employer importance.",
        "",
        "## Results by role",
        "",
    ]

    for role in ROLES:
        subset = result.loc[
            result["role_category"].eq(role)
        ].sort_values("priority_rank")

        matched_count = int((subset["jobs_with_skill"] > 0).sum())
        zero_count = int((subset["jobs_with_skill"] == 0).sum())

        lines.extend([
            f"### {role}",
            "",
            f"- Relevant jobs: {int(denominators[role])}",
            f"- Skills ranked: {len(subset)}",
            f"- Skills with detected matches: {matched_count}",
            f"- Skills with zero detected matches: {zero_count}",
            "",
            "| Rank | Skill | Matched jobs | Observed frequency | Evidence |",
            "|---:|---|---:|---:|---|",
        ])

        for _, row in subset.head(10).iterrows():
            lines.append(
                f"| {row['priority_rank']} | {row['skill_name']} | "
                f"{row['jobs_with_skill']} / {row['relevant_jobs_total']} | "
                f"{row['observed_frequency_pct']:.2f}% | "
                f"{row['evidence_level']} |"
            )

        lines.append("")

    REPORT_FILE.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    # Print summary.
    print("DAY 4 SKILL PRIORITY SCORING COMPLETE")
    print(f"Vocabulary skills: {vocab['skill_id'].nunique()}")
    print(f"Role-specific rows: {len(result)}")
    print(f"Relevant job totals: {denominators}")
    print(f"Output: {OUT_FILE.relative_to(ROOT)}")
    print(f"Report: {REPORT_FILE.relative_to(ROOT)}")

    print("\nRows by role:")
    print(result.groupby("role_category").size().to_string())

    print("\nTop 10 skills per role:")

    display_columns = [
        "priority_rank",
        "skill_name",
        "jobs_with_skill",
        "observed_frequency_pct",
        "evidence_level",
    ]

    for role in ROLES:
        print(f"\n{role}")
        subset = result.loc[
            result["role_category"].eq(role)
        ].sort_values("priority_rank")

        print(subset[display_columns].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
