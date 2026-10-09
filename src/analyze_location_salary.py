from pathlib import Path
import pandas as pd

INPUT = Path("data/processed/jobs_seniority_analyzed.csv")
OUT = Path("data/processed")

EXPECTED_TOTAL = 312
EXPECTED_RELEVANT = 251


def classify_location(value):
    """Assign a cautious broad region based on explicit location text."""
    if pd.isna(value) or not str(value).strip():
        return "Missing"

    text = str(value).strip().lower()

    if text in {"uk", "united kingdom", "great britain"}:
        return "UK-wide / unspecified"

    if "northern ireland" in text or "belfast" in text:
        return "Northern Ireland"
    if "scotland" in text or any(
        x in text for x in ["glasgow", "edinburgh", "dundee", "aberdeen"]
    ):
        return "Scotland"
    if "wales" in text or any(x in text for x in ["cardiff", "swansea"]):
        return "Wales"
    if "london" in text:
        return "London"
    if any(x in text for x in [
        "manchester", "liverpool", "lancashire", "cumbria", "cheshire"
    ]):
        return "North West England"
    if any(x in text for x in [
        "leeds", "yorkshire", "sheffield", "hull", "bradford"
    ]):
        return "Yorkshire and Humber"
    if any(x in text for x in [
        "newcastle", "durham", "sunderland", "northumberland", "teesside"
    ]):
        return "North East England"
    if any(x in text for x in [
        "birmingham", "west midlands", "staffordshire", "worcestershire",
        "nottingham", "derby", "leicester", "east midlands"
    ]):
        return "Midlands"
    if any(x in text for x in [
        "bristol", "devon", "cornwall", "somerset", "dorset",
        "gloucestershire", "south west"
    ]):
        return "South West England"
    if any(x in text for x in [
        "cambridge", "norwich", "suffolk", "essex", "east of england"
    ]):
        return "East of England"
    if any(x in text for x in [
        "oxford", "oxfordshire", "surrey", "kent", "sussex",
        "hampshire", "berkshire", "buckinghamshire", "south east"
    ]):
        return "South East England"

    return "Other / town-level location"


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Input not found: {INPUT}")

    df = pd.read_csv(INPUT)

    required = {
        "job_id", "role_category", "role_relevance", "location",
        "country", "latitude", "longitude", "salary_min", "salary_max",
        "salary_is_predicted", "contract_type"
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if len(df) != EXPECTED_TOTAL:
        raise ValueError(f"Expected {EXPECTED_TOTAL} rows, got {len(df)}")
    if df["job_id"].isna().any() or df["job_id"].duplicated().any():
        raise ValueError("Job IDs are missing or duplicated.")

    relevant = df[df["role_relevance"].eq("relevant")].copy()
    if len(relevant) != EXPECTED_RELEVANT:
        raise ValueError(
            f"Expected {EXPECTED_RELEVANT} relevant jobs, got {len(relevant)}"
        )

    # ---------- LOCATION ANALYSIS ----------
    relevant["location_text"] = (
        relevant["location"].fillna("").astype(str).str.strip()
    )
    relevant["location_region"] = relevant["location"].apply(classify_location)

    location_summary = (
        relevant.groupby(
            ["role_category", "location_region", "location_text"],
            dropna=False
        )
        .size()
        .rename("job_count")
        .reset_index()
    )

    role_totals = relevant["role_category"].value_counts().to_dict()
    location_summary["role_total"] = (
        location_summary["role_category"].map(role_totals)
    )
    location_summary["percentage_within_role"] = (
        location_summary["job_count"] /
        location_summary["role_total"] * 100
    ).round(2)

    location_summary = location_summary.sort_values(
        ["role_category", "job_count", "location_text"],
        ascending=[True, False, True]
    )

    region_summary = (
        relevant.groupby(["role_category", "location_region"])
        .size()
        .rename("job_count")
        .reset_index()
    )
    region_summary["role_total"] = (
        region_summary["role_category"].map(role_totals)
    )
    region_summary["percentage_within_role"] = (
        region_summary["job_count"] /
        region_summary["role_total"] * 100
    ).round(2)

    # ---------- SALARY QUALITY ----------
    for col in ["salary_min", "salary_max", "latitude", "longitude"]:
        relevant[col] = pd.to_numeric(relevant[col], errors="coerce")

    low_min = relevant["salary_min"].le(0)
    low_max = relevant["salary_max"].lt(100)
    reversed_range = relevant["salary_max"].lt(relevant["salary_min"])
    high_max = relevant["salary_max"].gt(200000)

    relevant["salary_quality_flags"] = ""
    flag_rules = [
        (low_min, "Minimum salary is zero or negative"),
        (low_max, "Maximum below 100; pay-period/unit needs review"),
        (reversed_range, "Maximum is below minimum"),
        (high_max, "Maximum above 200000; needs review"),
        (relevant["salary_min"].isna(), "Minimum salary missing"),
        (relevant["salary_max"].isna(), "Maximum salary missing"),
    ]

    for mask, message in flag_rules:
        relevant.loc[mask, "salary_quality_flags"] = (
            relevant.loc[mask, "salary_quality_flags"]
            .apply(lambda current: f"{current}; {message}" if current else message)
        )

    relevant["salary_quality_status"] = relevant[
        "salary_quality_flags"
    ].apply(lambda value: "Needs review" if value else "Passed basic checks")

    # Basic checks only; this does not prove the salary is accurate
    # or that all salaries share the same pay period.
    usable = relevant[
        relevant["salary_quality_status"].eq("Passed basic checks")
    ].copy()

    quality_summary = (
        relevant.groupby(
            ["role_category", "salary_quality_status"], dropna=False
        )
        .size()
        .rename("job_count")
        .reset_index()
    )

    quality_summary["role_total"] = (
        quality_summary["role_category"].map(role_totals)
    )
    quality_summary["percentage_within_role"] = (
        quality_summary["job_count"] /
        quality_summary["role_total"] * 100
    ).round(2)

    flag_summary = (
        relevant.groupby("salary_is_predicted", dropna=False)
        .size()
        .rename("job_count")
        .reset_index()
    )
    flag_summary["percentage_of_relevant_jobs"] = (
        flag_summary["job_count"] / len(relevant) * 100
    ).round(2)

    # Summarize usable values separately for predicted/non-predicted salaries.
    salary_summary = (
        usable.groupby(
            ["role_category", "salary_is_predicted"], dropna=False
        )
        .agg(
            job_count=("job_id", "nunique"),
            median_salary_min=("salary_min", "median"),
            median_salary_max=("salary_max", "median"),
            mean_salary_min=("salary_min", "mean"),
            mean_salary_max=("salary_max", "mean"),
            minimum_observed=("salary_min", "min"),
            maximum_observed=("salary_max", "max"),
        )
        .reset_index()
    )

    numeric_cols = [
        "median_salary_min", "median_salary_max",
        "mean_salary_min", "mean_salary_max",
        "minimum_observed", "maximum_observed"
    ]
    salary_summary[numeric_cols] = salary_summary[numeric_cols].round(2)

    # ---------- DATA QUALITY SNAPSHOT ----------
    coordinate_missing = (
        relevant["latitude"].isna() | relevant["longitude"].isna()
    ).sum()

    contract_missing = relevant["contract_type"].isna().sum()

    # ---------- SAVE OUTPUTS ----------
    OUT.mkdir(parents=True, exist_ok=True)

    location_summary.to_csv(OUT / "job_location_summary.csv", index=False)
    region_summary.to_csv(OUT / "job_region_summary.csv", index=False)
    quality_summary.to_csv(OUT / "salary_quality_summary.csv", index=False)
    salary_summary.to_csv(OUT / "salary_market_summary.csv", index=False)

    # Export all relevant listings with review flags; original data remains unchanged.
    detail_cols = [
        "job_id", "job_title", "role_category", "location",
        "location_region", "latitude", "longitude", "salary_min",
        "salary_max", "salary_is_predicted", "salary_quality_status",
        "salary_quality_flags", "contract_type", "source_url"
    ]
    relevant[detail_cols].to_csv(
        OUT / "location_salary_quality_detail.csv", index=False
    )

    report = [
        "# GradPath Phase 2 Day 6 - Location and Salary Analysis",
        "",
        "## Scope",
        f"- Total collected listings: {len(df)}",
        f"- Relevant listings analysed: {len(relevant)}",
        f"- Country code in relevant sample: {', '.join(sorted(relevant['country'].dropna().astype(str).unique()))}",
        "",
        "## Location coverage",
        f"- Distinct location strings: {relevant['location'].nunique()}",
        f"- Listings without coordinates: {coordinate_missing}",
        "",
        "### Listings by inferred broad region",
        "Region labels are heuristic, based on text in the location field.",
        "",
        "```text",
        region_summary.to_string(index=False),
        "```",
        "",
        "### Most frequent exact locations",
        "",
        "```text",
        location_summary.head(30).to_string(index=False),
        "```",
        "",
        "## Salary quality",
        f"- Listings passing basic salary checks: {len(usable)} of {len(relevant)}",
        f"- Listings flagged for review: {len(relevant) - len(usable)}",
        f"- Listings missing contract type: {contract_missing}",
        "",
        "### Salary quality by role",
        "",
        "```text",
        quality_summary.to_string(index=False),
        "```",
        "",
        "### Predicted salary flag counts",
        "",
        "```text",
        flag_summary.to_string(index=False),
        "```",
        "",
        "### Salary summaries after basic checks",
        "",
        "```text",
        salary_summary.to_string(index=False),
        "```",
        "",
        "## Interpretation and limitations",
        "- Salary fields are source-provided figures; the pay period and unit are not verified here.",
        "- Values passing basic checks are not guaranteed to be accurate or comparable.",
        "- Predicted and non-predicted salaries are summarized separately.",
        "- Records flagged for review are retained in the detailed output and excluded from primary salary summaries.",
        "- Location regions are heuristic; they should not be treated as verified administrative boundaries.",
        "- The collected sample is not necessarily representative of the entire UK job market.",
        "",
        "## Output files",
        "- `job_location_summary.csv`: counts by exact location and role",
        "- `job_region_summary.csv`: counts by inferred broad region and role",
        "- `salary_quality_summary.csv`: basic salary quality by role",
        "- `salary_market_summary.csv`: salary summaries by role and predicted flag",
        "- `location_salary_quality_detail.csv`: relevant listings and quality flags",
        "",
    ]

    report_path = OUT / "location_salary_analysis_report.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    print("Day 6 location and salary analysis completed.")
    print(f"All collected jobs: {len(df)}")
    print(f"Relevant jobs: {len(relevant)}")
    print(f"Passed basic salary checks: {len(usable)}")
    print(f"Flagged for salary review: {len(relevant) - len(usable)}")

    print("\nSalary quality by role:")
    print(quality_summary.to_string(index=False))

    print("\nSalary summary by role and predicted flag:")
    print(salary_summary.to_string(index=False))

    print("\nMost frequent broad regions:")
    print(
        region_summary.sort_values("job_count", ascending=False)
        .head(15).to_string(index=False)
    )

    print("\nFiles created:")
    for name in [
        "job_location_summary.csv",
        "job_region_summary.csv",
        "salary_quality_summary.csv",
        "salary_market_summary.csv",
        "location_salary_quality_detail.csv",
        "location_salary_analysis_report.md",
    ]:
        path = OUT / name
        print(f"- {path} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
