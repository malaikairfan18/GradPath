from pathlib import Path
import re
import pandas as pd

INPUT = Path("data/processed/jobs_title_normalized.csv")
OUTPUT = Path("data/processed/jobs_seniority_analyzed.csv")
SUMMARY = Path("data/processed/seniority_distribution.csv")
REPORT = Path("data/processed/seniority_analysis_report.md")

EXPECTED_TOTAL = 312
EXPECTED_RELEVANT = 251

RULES = [
    ("Management / Principal",
     r"\b(manager|head\s+of|director|principal|chief)\b",
     "Management, principal, or executive marker in title."),
    ("Lead",
     r"\b(lead|team\s+lead)\b",
     "Lead marker in title; takes precedence over Senior."),
    ("Senior",
     r"\b(senior|sr\.?|staff)\b",
     "Senior, sr., or staff marker in title."),
    ("Junior",
     r"\b(junior|jr\.?|associate)\b",
     "Junior or associate marker in title."),
    ("Entry-level / Graduate",
     r"\b(graduate|trainee|placement|apprentice|entry[- ]level)\b",
     "Graduate, trainee, placement, apprentice, or entry-level marker."),
    ("Mid-level / Experienced",
     r"\b(mid[- ]level|intermediate)\b",
     "Explicit mid-level or intermediate marker in title."),
]

def classify(title):
    title = str(title) if pd.notna(title) else ""
    for label, pattern, reason in RULES:
        if re.search(pattern, title, flags=re.IGNORECASE):
            return pd.Series([label, reason])
    return pd.Series([
        "Unspecified",
        "No explicit seniority marker found in title."
    ])

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT}")

    df = pd.read_csv(INPUT)

    required = {"job_id", "job_title", "role_category", "role_relevance"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if len(df) != EXPECTED_TOTAL:
        raise ValueError(f"Expected {EXPECTED_TOTAL} rows, got {len(df)}")
    if df["job_id"].isna().any() or df["job_id"].duplicated().any():
        raise ValueError("Job IDs are missing or duplicated.")

    df[["seniority_level", "seniority_reason"]] = df["job_title"].apply(classify)
    df["seniority_method"] = "Rule-based job-title classification"

    relevant = df[df["role_relevance"].eq("relevant")].copy()
    if len(relevant) != EXPECTED_RELEVANT:
        raise ValueError(
            f"Expected {EXPECTED_RELEVANT} relevant jobs, got {len(relevant)}"
        )

    summary = (
        relevant.groupby(["role_category", "seniority_level"])
        .size()
        .rename("job_count")
        .reset_index()
    )
    totals = relevant["role_category"].value_counts().to_dict()
    summary["role_total"] = summary["role_category"].map(totals)
    summary["percentage_within_role"] = (
        100 * summary["job_count"] / summary["role_total"]
    ).round(2)

    order = [
        "Entry-level / Graduate",
        "Junior",
        "Mid-level / Experienced",
        "Unspecified",
        "Senior",
        "Lead",
        "Management / Principal",
    ]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    summary.to_csv(SUMMARY, index=False)

    all_counts = (
        df.groupby(["role_relevance", "seniority_level"])
        .size().reset_index(name="job_count")
    )
    role_table = (
        relevant.groupby(["role_category", "seniority_level"])
        .size().unstack(fill_value=0)
        .reindex(columns=order, fill_value=0)
    )

    report_lines = [
        "# GradPath Phase 2 Day 5 - Seniority Analysis",
        "",
        "## Scope",
        f"- All collected listings: {len(df)}",
        f"- Relevant listings: {len(relevant)}",
        "- Method: rule-based classification of job titles.",
        "",
        "## Limitations",
        "- Unspecified does not mean entry-level.",
        "- Labels are inferred from title wording, not verified experience requirements.",
        "- Rule order resolves titles containing multiple seniority markers.",
        "- This collected sample is not necessarily representative of the entire UK market.",
        "",
        "## Relevant jobs by role and seniority",
        "```text\n" + summary.to_string(index=False) + "\n```",
        "",
        "## Relevant job counts by role",
        "```text\n" + role_table.to_string() + "\n```",
        "",
        "## Counts across all collected listings",
        "```text\n" + all_counts.to_string(index=False) + "\n```",
        "",
    ]
    REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print("Seniority analysis completed successfully.")
    print(f"Total jobs: {len(df)}")
    print(f"Relevant jobs: {len(relevant)}")
    print("\nSeniority counts across all jobs:")
    print(df["seniority_level"].value_counts().to_string())
    print("\nRelevant jobs by role and seniority:")
    print(role_table.to_string())
    print("\nRelevant-only summary:")
    print(summary.to_string(index=False))
    print("\nCreated files:")
    for path in [OUTPUT, SUMMARY, REPORT]:
        print(f"{path} ({path.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()
